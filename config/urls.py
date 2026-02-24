"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),

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

# Serve media files (uploaded photos, etc.) in both dev and production.
# We use re_path + serve directly instead of static() because static() is a
# no-op when DEBUG=False, which breaks media serving on cPanel/shared hosting
# where there is no separate web server (nginx/Apache) handling /media/ URLs.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
