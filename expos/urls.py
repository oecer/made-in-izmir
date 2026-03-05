from django.urls import path
from . import views

app_name = 'expos'

urlpatterns = [
    path('calendar/', views.calendar, name='calendar'),
    path('dashboard/calendar/', views.dashboard_calendar_view, name='dashboard_calendar'),
    path('expo/<int:expo_id>/signup/', views.expo_signup_view, name='expo_signup'),
]
