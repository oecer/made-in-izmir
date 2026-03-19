from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('abonelik/', views.pricing_view, name='pricing'),
    path('kullanici/abonelik/', views.my_subscription_view, name='my_subscription'),
]
