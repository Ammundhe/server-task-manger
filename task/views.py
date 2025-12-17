from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
import requests
from datetime import timedelta

from .models import Task, WeatherLog
from .serializers import TaskSerializer, WeatherLogSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics for data visualization"""
        total_tasks = Task.objects.count()

        # Get status breakdown as dictionary
        status_breakdown_qs = Task.objects.values('status').annotate(count=Count('status'))
        status_breakdown = {item['status']: item['count'] for item in status_breakdown_qs}

        # Get priority breakdown as dictionary
        priority_breakdown_qs = Task.objects.values('priority').annotate(count=Count('priority'))
        priority_breakdown = {item['priority']: item['count'] for item in priority_breakdown_qs}

        # Tasks created in the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        tasks_last_7_days = Task.objects.filter(created_at__gte=seven_days_ago).count()

        return Response({
            'total_tasks': total_tasks,
            'status_breakdown': status_breakdown,
            'priority_breakdown': priority_breakdown,
            'tasks_last_7_days': tasks_last_7_days,
        })


class WeatherViewSet(viewsets.ModelViewSet):
    queryset = WeatherLog.objects.all()
    serializer_class = WeatherLogSerializer

    @action(detail=False, methods=['post'])
    def fetch_weather(self, request):
        """Fetch weather data from OpenWeatherMap API and store it"""
        city = request.data.get('city', 'London')
        api_key = settings.WEATHER_API_KEY
        if not api_key:
            return Response(
                {'error': 'Weather API key not configured'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        try:
            response = requests.get(url)
            # Check if request was successful
            if response.status_code != 200:
                try:
                    error_data = response.json()
                except:
                    error_data = {'message': response.text}

                return Response({
                    'error': f'Weather API returned status {response.status_code}',
                    'message': error_data.get('message', 'Unknown error'),
                    'full_response': error_data
                }, status=status.HTTP_400_BAD_REQUEST)

            data = response.json()

            # Create weather log entry
            weather_log = WeatherLog.objects.create(
                city=city,
                temperature=data['main']['temp'],
                description=data['weather'][0]['description'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed']
            )

            serializer = WeatherLogSerializer(weather_log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Network error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest weather logs"""
        logs = WeatherLog.objects.all()[:10]
        serializer = WeatherLogSerializer(logs, many=True)
        return Response(serializer.data)
