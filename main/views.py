import hmac as _hmac
import hashlib
import time
import logging

from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger(__name__)

_CONTACT_MIN_SECS = getattr(settings, 'CONTACT_MIN_SUBMIT_SECONDS', 4)
_CONTACT_MAX_SECS = getattr(settings, 'CONTACT_MAX_SUBMIT_SECONDS', 3600)
_RATE_LIMIT       = getattr(settings, 'CONTACT_RATE_LIMIT', 3)
_RATE_WINDOW      = getattr(settings, 'CONTACT_RATE_WINDOW', 3600)


def _make_form_token(ts: int) -> str:
    key = settings.SECRET_KEY.encode()
    return _hmac.new(key, str(ts).encode(), hashlib.sha256).hexdigest()


def _verify_form_token(ts_str, token):
    try:
        ts = int(ts_str)
    except (ValueError, TypeError):
        return False, 'invalid'
    expected = _make_form_token(ts)
    if not _hmac.compare_digest(expected, token or ''):
        return False, 'invalid'
    elapsed = int(time.time()) - ts
    if elapsed < _CONTACT_MIN_SECS:
        return False, 'too_fast'
    if elapsed > _CONTACT_MAX_SECS:
        return False, 'too_slow'
    return True, 'ok'


def _get_client_ip(request) -> str:
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def _check_rate_limit(ip: str) -> bool:
    key = f'contact_submit_{ip}'
    count = cache.get(key, 0)
    if count >= _RATE_LIMIT:
        return False
    if count == 0:
        cache.set(key, 1, _RATE_WINDOW)
    else:
        cache.incr(key)
    return True


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
    """Producers page view — passes active subscription plans and live campaigns."""
    from subscriptions.models import SubscriptionPlan, PlanCampaign
    from django.utils import timezone as tz

    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order', 'monthly_price')
    today = tz.now().date()
    active_campaigns = PlanCampaign.objects.filter(
        is_active=True,
        valid_from__lte=today,
        valid_until__gte=today,
    ).select_related('plan')

    # Build a dict: plan_id -> campaign for easy lookup in template
    campaign_by_plan = {c.plan_id: c for c in active_campaigns}

    return render(request, 'producers.html', {
        'plans': plans,
        'campaign_by_plan': campaign_by_plan,
        'today': today,
    })


def buyers(request):
    """Buyers page view"""
    return render(request, 'buyers.html')


def contact(request):
    """Contact page view - handles both GET (render) and POST (form submission)"""
    if request.method == 'POST':

        # Layer 1: Honeypot — bots fill every visible field; humans never see this one
        if request.POST.get('website', ''):
            logger.info('Contact spam: honeypot triggered from %s', request.META.get('REMOTE_ADDR'))
            return HttpResponse(status=200)  # silent success to discourage retries

        # Layer 2: Time-based check — bots submit too fast or replay stale tokens
        valid, reason = _verify_form_token(
            request.POST.get('form_ts', ''),
            request.POST.get('form_tk', ''),
        )
        if not valid:
            logger.info('Contact spam: time check failed (%s) from %s', reason, request.META.get('REMOTE_ADDR'))
            if reason == 'too_slow':
                return HttpResponse('Oturum süresi doldu, sayfayı yenileyip tekrar deneyin.', status=400)
            return HttpResponse(status=400)

        # Layer 3: IP rate limiting
        client_ip = _get_client_ip(request)
        if not _check_rate_limit(client_ip):
            logger.warning('Contact rate limit exceeded for IP %s', client_ip)
            return HttpResponse(status=429)

        # Field validation
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            return HttpResponse(status=400)

        # Layer 4: Duplicate detection — same email+message within 24h
        from accounts.models import ContactSubmission
        from django.utils import timezone
        from datetime import timedelta
        if ContactSubmission.objects.filter(
            email=email,
            message=message,
            submitted_at__gte=timezone.now() - timedelta(hours=24),
        ).exists():
            return HttpResponse(status=200)  # silent — already logged

        # Send email
        from django.core.mail import send_mail
        subject_line = f"[Made in İzmir] İletişim: {subject} - {name}"
        body = (
            f"Ad Soyad: {name}\n"
            f"E-posta:  {email}\n"
            f"Telefon:  {phone or '-'}\n"
            f"Konu:     {subject}\n\n"
            f"Mesaj:\n{message}"
        )
        email_ok = True
        try:
            send_mail(
                subject_line,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception:
            email_ok = False

        # Persist submission for audit trail
        ContactSubmission.objects.create(
            name=name, email=email, phone=phone,
            subject=subject, message=message,
            ip_address=client_ip, email_sent=email_ok,
        )

        if not email_ok:
            return HttpResponse(status=500)

        return HttpResponse(status=200)

    # GET: render form with a signed timestamp for the time-check
    ts = int(time.time())
    return render(request, 'contact.html', {'form_ts': ts, 'form_tk': _make_form_token(ts)})
