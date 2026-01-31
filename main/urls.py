from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('producers/', views.producers, name='producers'),
    path('buyers/', views.buyers, name='buyers'),
    path('calendar/', views.calendar, name='calendar'),
    path('contact/', views.contact, name='contact'),
]
