from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
from .models import Booking, Availability
from .serializers import BookingSerializer, BookingCreateSerializer, AvailabilitySerializer
from customers.models import Customer


class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Availability.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get bookings for meeting pages owned by the user
        return Booking.objects.filter(meeting_page__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_public(self, request):
        """Create booking from public page"""
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                booking = serializer.save(status='booked')

                # Auto-create customer record based on booking data
                user_input = booking.user_input or {}
                attendee_email = booking.attendee_email or user_input.get('email')
                attendee_name = booking.attendee_name or user_input.get('name', '')
                phone = user_input.get('phone', '')
                organization = user_input.get('organization', '')

                customer_defaults = {
                    'name': attendee_name or '',
                    'phone': phone or '',
                    'organization': organization or '',
                    'metadata': user_input,
                }

                if attendee_email:
                    customer, created = Customer.objects.get_or_create(
                        email=attendee_email,
                        defaults=customer_defaults
                    )
                    if not created:
                        # Update metadata and other fields if customer already existed
                        for key, value in customer_defaults.items():
                            if value:
                                if key == 'metadata':
                                    merged = customer.metadata or {}
                                    merged.update(value)
                                    customer.metadata = merged
                                else:
                                    setattr(customer, key, value)
                        customer.save()
                else:
                    Customer.objects.create(
                        name=attendee_name or '',
                        email=None,
                        phone=phone or '',
                        organization=organization or '',
                        metadata=user_input
                    )

            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        # TODO: Send cancellation email
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark booking as completed"""
        booking = self.get_object()
        booking.status = 'completed'
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings"""
        upcoming = self.get_queryset().filter(
            date__gte=timezone.now(),
            status='booked'
        ).order_by('date')[:10]
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available_slots(self, request):
        """Get available time slots for a meeting page"""
        meeting_page_id = request.query_params.get('meeting_page_id')
        date = request.query_params.get('date')

        if not meeting_page_id or not date:
            return Response({'error': 'meeting_page_id and date are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get meeting page
        from meeting_pages.models import MeetingPage
        try:
            meeting_page = MeetingPage.objects.get(id=meeting_page_id, active=True)
        except MeetingPage.DoesNotExist:
            return Response({'error': 'Meeting page not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Get user's availability for the requested weekday
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'},
                            status=status.HTTP_400_BAD_REQUEST)

        weekday = date_obj.weekday()
        availabilities = Availability.objects.filter(
            user=meeting_page.user,
            weekday=weekday,
            is_active=True
        ).order_by('start_time')

        if not availabilities.exists():
            return Response({'slots': [], 'message': 'No availability configured for this date.'})

        # Gather existing bookings for the chosen day
        current_tz = timezone.get_current_timezone()
        start_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()), current_tz)
        end_of_day = start_of_day + timedelta(days=1)
        existing_bookings = Booking.objects.filter(
            meeting_page=meeting_page,
            date__gte=start_of_day,
            date__lt=end_of_day,
            status='booked'
        )

        duration = meeting_page.duration_minutes or 30
        slot_delta = timedelta(minutes=duration)
        now = timezone.now()
        slots = []

        for availability in availabilities:
            start_dt = datetime.combine(date_obj, availability.start_time)
            end_dt = datetime.combine(date_obj, availability.end_time)

            start_dt = timezone.make_aware(start_dt, current_tz) if timezone.is_naive(start_dt) else timezone.localtime(start_dt, current_tz)
            end_dt = timezone.make_aware(end_dt, current_tz) if timezone.is_naive(end_dt) else timezone.localtime(end_dt, current_tz)

            current_slot_start = start_dt
            while current_slot_start + slot_delta <= end_dt:
                current_slot_end = current_slot_start + slot_delta

                # Skip slots in the past
                if current_slot_end <= now:
                    current_slot_start += slot_delta
                    continue

                # Check overlap with existing bookings
                overlap_exists = existing_bookings.filter(
                    date__gte=current_slot_start,
                    date__lt=current_slot_end
                ).exists()

                if not overlap_exists:
                    slots.append({
                        'time': current_slot_start.isoformat(),
                        'end_time': current_slot_end.isoformat(),
                        'display': timezone.localtime(current_slot_start, current_tz).strftime('%I:%M %p'),
                        'duration_minutes': duration
                    })

                current_slot_start = current_slot_end

        return Response({'slots': slots})
