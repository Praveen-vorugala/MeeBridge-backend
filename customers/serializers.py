from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'organization', 'metadata', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'organization': {'required': False, 'allow_blank': True},
            'metadata': {'required': False}
        }
