from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.list_entries, name="list-entries"),
    path('log/', views.log_hours, name="log-hours"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('rpt_timeframe/', views.rpt_timeframe, name="rpt_timeframe"),
]
