from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('subscription/', views.pricing_view, name='pricing'),
    path('user/subscription/', views.my_subscription_view, name='my_subscription'),
]
