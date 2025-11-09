from django.db import models
from django.contrib.auth import get_user_model
from meeting_pages.models import MeetingPage
import uuid

User = get_user_model()


class Availability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['weekday', 'start_time']
        unique_together = ['user', 'weekday', 'start_time', 'end_time']

    def __str__(self):
        return f"{self.user.email} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting_page = models.ForeignKey(MeetingPage, on_delete=models.CASCADE, related_name='bookings')
    user_input = models.JSONField(default=dict, help_text="Form data submitted by the user")
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    attendee_email = models.EmailField(blank=True, null=True)
    attendee_name = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    management_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Booking {self.id} - {self.attendee_email or 'No email'} - {self.date}"
