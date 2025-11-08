from django.contrib import admin
from .models import Booking, Availability


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'meeting_page', 'attendee_email', 'date', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['attendee_email', 'attendee_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_weekday_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['weekday', 'is_active']
    search_fields = ['user__email']
