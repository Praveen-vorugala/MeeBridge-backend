from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import MeetingPage
from .serializers import MeetingPageSerializer, MeetingPagePublicSerializer


class MeetingPageViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingPageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingPage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public(self, request, slug=None):
        """Public endpoint for booking page"""
        meeting_page = get_object_or_404(MeetingPage, slug=slug, active=True)
        serializer = MeetingPagePublicSerializer(meeting_page)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, slug=None):
        """Duplicate a meeting page"""
        original = self.get_object()
        original.pk = None
        original.slug = f"{original.slug}-copy"
        original.title = f"{original.title} (Copy)"
        original.save()
        serializer = self.get_serializer(original)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
