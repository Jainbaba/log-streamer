from django.urls import path
from . import views

urlpatterns = [
    path('api/historical-logs', views.HistoricalLogsView.as_view(), name='historical-logs'),
    path('api/filter-type', views.FilterTypeView.as_view(), name='filter-type'),
    path('health', views.health_check, name='health_check'),
]