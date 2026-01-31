from django.shortcuts import render


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
