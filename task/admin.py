from django.contrib import admin
from .models import Task, WeatherLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']


@admin.register(WeatherLog)
class WeatherLogAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'description', 'humidity', 'recorded_at']
    list_filter = ['city', 'recorded_at']
    search_fields = ['city', 'description']
