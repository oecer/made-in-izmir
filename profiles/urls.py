from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('company/logo/submit/', views.submit_company_logo_view, name='submit_company_logo'),
    path('company/gallery/submit/', views.submit_gallery_photo_view, name='submit_gallery_photo'),
    path('enquiry/submit/', views.submit_enquiry_view, name='submit_enquiry'),
]
