from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.pick_category, name="checkin-category"),
    path('event/<int:category_id>', views.pick_event, name="checkin-event"),
    path('checkin/<int:event_id>', views.checkin_final, name="checkin"),
    path('rpt_timeframe_activity/', views.rpt_timeframe_activity, name="rpt_timeframe_activity"),
]