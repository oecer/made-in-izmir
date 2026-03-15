from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-account/', views.profile_view, name='profile'),
    path('my-account/edit/', views.edit_profile_view, name='edit_profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
