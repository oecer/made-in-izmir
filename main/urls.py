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
    
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/producer/', views.producer_dashboard_view, name='producer_dashboard'),
    path('dashboard/buyer/', views.buyer_dashboard_view, name='buyer_dashboard'),
    
    # Product management URLs (producers only)
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
]
