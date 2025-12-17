from rest_framework import serializers
from .models import Task, WeatherLog


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'status', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WeatherLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherLog
        fields = ['id', 'city', 'temperature', 'description', 'humidity', 'wind_speed', 'recorded_at']
        read_only_fields = ['recorded_at']
