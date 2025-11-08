from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingPageViewSet

router = DefaultRouter()
router.register(r'meeting-pages', MeetingPageViewSet, basename='meeting-page')

urlpatterns = [
    path('public/meeting-pages/<slug:slug>/', MeetingPageViewSet.as_view({'get': 'public'}), name='meeting-page-public'),
    path('', include(router.urls)),
]

