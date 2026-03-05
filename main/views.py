from django.shortcuts import render


def index(request):
    """Home page view - includes upcoming expos preview"""
    from django.utils import timezone as tz
    from expos.models import Expo
    today = tz.now().date()
    upcoming_expos = Expo.objects.filter(is_active=True, start_date__gte=today).order_by('start_date')[:3]
    return render(request, 'index.html', {'upcoming_expos': upcoming_expos})


def about(request):
    """About page view"""
    return render(request, 'about.html')


def why_izmir(request):
    """Why Izmir page view"""
    return render(request, 'why_izmir.html')


def producers(request):
    """Producers page view"""
    return render(request, 'producers.html')


def buyers(request):
    """Buyers page view"""
    return render(request, 'buyers.html')


def contact(request):
    """Contact page view - handles both GET (render) and POST (form submission)"""
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            from django.http import HttpResponse
            return HttpResponse(status=400)

        try:
            from django.core.mail import send_mail
            from django.conf import settings

            subject_line = f"[Made in İzmir] İletişim: {subject} - {name}"
            body = (
                f"Ad Soyad: {name}\n"
                f"E-posta:  {email}\n"
                f"Telefon:  {phone or '-'}\n"
                f"Konu:     {subject}\n\n"
                f"Mesaj:\n{message}"
            )
            send_mail(
                subject_line,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception:
            from django.http import HttpResponse
            return HttpResponse(status=500)

        from django.http import HttpResponse
        return HttpResponse(status=200)

    return render(request, 'contact.html')
