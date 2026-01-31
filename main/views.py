from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm


def index(request):
    """Home page view"""
    return render(request, 'index.html')


def about(request):
    """About page view"""
    return render(request, 'about.html')


def producers(request):
    """Producers page view"""
    return render(request, 'producers.html')


def buyers(request):
    """Buyers page view"""
    return render(request, 'buyers.html')


def calendar(request):
    """Calendar page view"""
    return render(request, 'calendar.html')


def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')


def signup_view(request):
    """User registration view - creates signup request for admin approval"""
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            signup_request = form.save()
            messages.success(
                request, 
                'Kayıt talebiniz alındı! Hesabınız yönetici onayından sonra aktif hale gelecektir. '
                'E-posta adresinize onay durumu hakkında bilgi gönderilecektir.'
            )
            return redirect('main:index')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})



def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'main:index')
                return redirect(next_url)
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('main:index')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'auth/profile.html')
