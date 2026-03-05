from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('dashboard/producer/', views.producer_dashboard_view, name='producer_dashboard'),
    path('dashboard/buyer/', views.buyer_dashboard_view, name='buyer_dashboard'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
]
