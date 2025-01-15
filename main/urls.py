from django.urls import path

from .views import my_endpoint, display_data, fetch_latest_data, chart_view, analyze_heart_rate_view

urlpatterns = [
    path('api/endpoint/', my_endpoint, name='my_endpoint'),
    path('displaydata/', display_data, name="display"),
    path('fetch-latest-data/', fetch_latest_data, name='fetch_latest_data'),
    path('chart-view', chart_view, name='chart_view'),
    path('analyze-heart-rate/', analyze_heart_rate_view, name="analyze-heart-rate/")
]
