from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, AvailabilityViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'availabilities', AvailabilityViewSet, basename='availability')

urlpatterns = [
    path('public/bookings/', BookingViewSet.as_view({'post': 'create_public'}), name='booking-create-public'),
    path('public/bookings/available-slots/', BookingViewSet.as_view({'get': 'available_slots'}), name='booking-available-slots'),
    path('', include(router.urls)),
]

