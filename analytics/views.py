from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from bookings.models import Booking
from meeting_pages.models import MeetingPage
from .serializers import AnalyticsSerializer


class AnalyticsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get all bookings for user's meeting pages
        bookings = Booking.objects.filter(meeting_page__user=user)
        
        # Calculate KPIs
        total_bookings = bookings.count()
        total_cancellations = bookings.filter(status='cancelled').count()
        total_completed = bookings.filter(status='completed').count()
        
        # Calculate average booking rate per week
        weeks_ago = 4
        start_date = timezone.now() - timedelta(weeks=weeks_ago)
        recent_bookings = bookings.filter(created_at__gte=start_date)
        if weeks_ago > 0:
            average_booking_rate_per_week = recent_bookings.count() / weeks_ago
        else:
            average_booking_rate_per_week = 0
        
        # Upcoming meetings
        upcoming_meetings_count = bookings.filter(
            date__gte=timezone.now(),
            status='booked'
        ).count()
        
        # Daily stats (last 30 days)
        from datetime import datetime
        daily_stats = []
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            day_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            day_bookings = bookings.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            )
            daily_stats.append({
                'date': date.isoformat(),
                'bookings': day_bookings.filter(status='booked').count(),
                'cancellations': day_bookings.filter(status='cancelled').count(),
                'completed': day_bookings.filter(status='completed').count(),
            })
        daily_stats.reverse()
        
        # Weekly stats (last 12 weeks)
        weekly_stats = []
        for i in range(12):
            week_start = timezone.now() - timedelta(weeks=i+1)
            week_end = timezone.now() - timedelta(weeks=i)
            week_bookings = bookings.filter(
                created_at__gte=week_start,
                created_at__lt=week_end
            )
            weekly_stats.append({
                'week': week_start.isoformat(),
                'bookings': week_bookings.filter(status='booked').count(),
                'cancellations': week_bookings.filter(status='cancelled').count(),
                'completed': week_bookings.filter(status='completed').count(),
            })
        weekly_stats.reverse()
        
        # Monthly stats (last 12 months)
        monthly_stats = []
        for i in range(12):
            month_start = timezone.now() - timedelta(days=30*(i+1))
            month_end = timezone.now() - timedelta(days=30*i)
            month_bookings = bookings.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            )
            monthly_stats.append({
                'month': month_start.strftime('%Y-%m'),
                'bookings': month_bookings.filter(status='booked').count(),
                'cancellations': month_bookings.filter(status='cancelled').count(),
                'completed': month_bookings.filter(status='completed').count(),
            })
        monthly_stats.reverse()
        
        data = {
            'total_bookings': total_bookings,
            'total_cancellations': total_cancellations,
            'total_completed': total_completed,
            'average_booking_rate_per_week': round(average_booking_rate_per_week, 2),
            'upcoming_meetings_count': upcoming_meetings_count,
            'daily_stats': daily_stats,
            'weekly_stats': weekly_stats,
            'monthly_stats': monthly_stats,
        }
        
        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)
