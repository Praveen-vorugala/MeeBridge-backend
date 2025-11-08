from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class MeetingPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_pages')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    theme = models.JSONField(default=dict, help_text="Colors, fonts, styling configuration")
    fields = models.JSONField(default=list, help_text="List of field configurations")
    layout_style = models.CharField(
        max_length=50,
        choices=[('classic', 'Classic'), ('minimal', 'Minimal'), ('modern', 'Modern')],
        default='classic'
    )
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    active = models.BooleanField(default=True)
    event_type = models.CharField(max_length=100, default='default', help_text="15-min, 30-min, 60-min, etc.")
    duration_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"
