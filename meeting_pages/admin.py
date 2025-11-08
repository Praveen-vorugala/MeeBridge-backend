from django.contrib import admin
from .models import MeetingPage


@admin.register(MeetingPage)
class MeetingPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'user', 'event_type', 'active', 'created_at']
    list_filter = ['active', 'layout_style', 'event_type']
    search_fields = ['title', 'slug', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
