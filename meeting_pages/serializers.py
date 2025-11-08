from rest_framework import serializers
from .models import MeetingPage
from users.serializers import UserSerializer


class MeetingPageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = MeetingPage
        fields = [
            'id', 'user', 'user_id', 'title', 'slug', 'theme', 'fields',
            'layout_style', 'logo', 'banner_image', 'background_image',
            'active', 'event_type', 'duration_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data.pop('user_id', None)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MeetingPagePublicSerializer(serializers.ModelSerializer):
    """Serializer for public booking page (no sensitive data)"""
    class Meta:
        model = MeetingPage
        fields = [
            'id', 'title', 'slug', 'theme', 'fields', 'layout_style',
            'logo', 'banner_image', 'background_image', 'event_type', 'duration_minutes'
        ]

