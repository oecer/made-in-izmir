"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('accounts.urls')),
    path('', include('profiles.urls')),
    path('', include('catalog.urls')),
    path('', include('expos.urls')),

    # Password reset flow (built-in Django views with custom templates)
    path('forgot-password/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt',
             success_url='/forgot-password/done/',
         ),
         name='password_reset'),
    path('forgot-password/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('forgot-password/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             success_url='/forgot-password/complete/',
         ),
         name='password_reset_confirm'),
    path('forgot-password/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]

# Public company profile — must be last to not shadow any named route.
from profiles.views import company_profile_view, business_card_view
urlpatterns += [
    path('<slug:company_username>/', company_profile_view, name='company_profile'),
    path('<slug:company_username>/business-card/', business_card_view, name='business_card'),
]

# Serve media files in both dev and production.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
