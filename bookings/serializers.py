from rest_framework import serializers
from .models import Booking, Availability
from meeting_pages.serializers import MeetingPageSerializer


class AvailabilitySerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = Availability
        fields = [
            'id', 'user', 'weekday', 'weekday_display', 'start_time', 'end_time',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    meeting_page = MeetingPageSerializer(read_only=True)
    meeting_page_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'meeting_page', 'meeting_page_id', 'user_input', 'date',
            'status', 'attendee_email', 'attendee_name', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings from public page"""

    class Meta:
        model = Booking
        fields = [
            'meeting_page', 'user_input', 'date', 'attendee_email',
            'attendee_name', 'notes', 'status'
        ]
        extra_kwargs = {
            'attendee_email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'attendee_name': {'required': False, 'allow_blank': True},
            'notes': {'required': False, 'allow_blank': True},
            'status': {'required': False}
        }

    def validate(self, attrs):
        # Ensure meeting_page is provided
        if 'meeting_page' not in attrs or attrs['meeting_page'] is None:
            raise serializers.ValidationError({'meeting_page': 'Meeting page is required.'})
        return attrs

    def create(self, validated_data):
        validated_data.setdefault('attendee_email', None)
        validated_data.setdefault('attendee_name', '')
        validated_data.setdefault('notes', '')
        validated_data.setdefault('status', 'booked')
        return super().create(validated_data)

