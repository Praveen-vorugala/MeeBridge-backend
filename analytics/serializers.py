from rest_framework import serializers


class AnalyticsSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    total_cancellations = serializers.IntegerField()
    total_completed = serializers.IntegerField()
    average_booking_rate_per_week = serializers.FloatField()
    upcoming_meetings_count = serializers.IntegerField()
    daily_stats = serializers.ListField(child=serializers.DictField())
    weekly_stats = serializers.ListField(child=serializers.DictField())
    monthly_stats = serializers.ListField(child=serializers.DictField())

