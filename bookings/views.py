from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .models import Booking, Availability
from .serializers import BookingSerializer, BookingCreateSerializer, AvailabilitySerializer
from customers.models import Customer
from .emails import send_booking_email


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

    def perform_create(self, serializer):
        booking = serializer.save()
        transaction.on_commit(lambda: send_booking_email(booking, action='created'))

    def perform_update(self, serializer):
        booking = serializer.save()
        transaction.on_commit(lambda: send_booking_email(booking, action='updated'))

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

                Customer.objects.create(
                    name=attendee_name or '',
                    email=attendee_email,
                    phone=phone or '',
                    organization=organization or '',
                    metadata=user_input
                )

                transaction.on_commit(lambda: send_booking_email(booking, action='created'))

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
        tz_name = request.query_params.get('timezone')

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
        if tz_name:
            try:
                target_tz = ZoneInfo(tz_name)
            except ZoneInfoNotFoundError:
                target_tz = timezone.get_default_timezone()
        else:
            target_tz = timezone.get_default_timezone()

        start_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()), target_tz)
        end_of_day = start_of_day + timedelta(days=1)

        existing_bookings = Booking.objects.filter(
            meeting_page__user=meeting_page.user,
            date__gte=start_of_day,
            date__lt=end_of_day,
        ).order_by('date')

        slots = []

        for booking in existing_bookings:
            user_input = booking.user_input or {}
            selected_date = user_input.get('selected_date')
            selected_time = user_input.get('selected_time')
            booking_tz = user_input.get('timezone') or tz_name
            fallback_start = booking.date.astimezone(target_tz)

            if selected_date and selected_time:
                time_str = selected_time if len(selected_time) > 5 else f"{selected_time}:00"
                dt_str = f"{selected_date}T{time_str}"
                try:
                    booking_tzinfo = ZoneInfo(booking_tz) if booking_tz else target_tz
                except ZoneInfoNotFoundError:
                    booking_tzinfo = target_tz

                try:
                    parsed_dt = datetime.fromisoformat(dt_str)
                    if parsed_dt.tzinfo is None:
                        parsed_dt = parsed_dt.replace(tzinfo=booking_tzinfo)
                    booking_start = parsed_dt.astimezone(target_tz)
                except ValueError:
                    booking_start = fallback_start
            else:
                booking_start = fallback_start

            slots.append({
                'time': booking_start.isoformat(),
                'display': booking_start.strftime('%I:%M %p'),
                'duration_minutes': booking.meeting_page.duration_minutes if booking.meeting_page else None,
                'status': booking.status,
                'booking_id': str(booking.id),
                'attendee_name': booking.attendee_name,
                'attendee_email': booking.attendee_email,
            })

        return Response({'slots': slots})
