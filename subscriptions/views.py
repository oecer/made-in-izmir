import hmac as _hmac
import hashlib
import time
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from .models import SubscriptionPlan

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


def pricing_view(request):
    """Public subscription pricing page with inline subscription request form."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')

    current_plan = None
    pricing_tenant = None
    if request.user.is_authenticated:
        try:
            tenant = request.user.profile.tenant
            if tenant:
                current_plan = tenant.get_active_plan()
                pricing_tenant = tenant
        except Exception:
            pass

    # Handle subscription request form POST
    if request.method == 'POST':
        if request.POST.get('website', ''):
            logger.info('Pricing contact spam: honeypot from %s', request.META.get('REMOTE_ADDR'))
            return HttpResponse(status=200)

        valid, reason = _verify_form_token(
            request.POST.get('form_ts', ''),
            request.POST.get('form_tk', ''),
        )
        if not valid:
            if reason == 'too_slow':
                return HttpResponse('Oturum süresi doldu, sayfayı yenileyip tekrar deneyin.', status=400)
            return HttpResponse(status=400)

        client_ip = _get_client_ip(request)
        if not _check_rate_limit(client_ip):
            return HttpResponse(status=429)

        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        plan_name  = request.POST.get('plan_name', '').strip()
        message    = request.POST.get('message', '').strip()
        username   = request.POST.get('username', '').strip()
        user_id    = request.POST.get('user_id', '').strip()
        tenant_name = request.POST.get('tenant_name', '').strip()
        tenant_id  = request.POST.get('tenant_id', '').strip()

        if not name or not email or not plan_name:
            return HttpResponse(status=400)

        from accounts.models import ContactSubmission
        from django.utils import timezone
        from datetime import timedelta
        full_message = (
            f"[ABONELİK TALEBİ]\n"
            f"İstenen Plan: {plan_name}\n"
            f"Kullanıcı: {username or '-'} (ID: {user_id or '-'})\n"
            f"Firma: {tenant_name or '-'} (ID: {tenant_id or '-'})\n\n"
            f"{message or '-'}"
        )
        if ContactSubmission.objects.filter(
            email=email,
            message=full_message,
            submitted_at__gte=timezone.now() - timedelta(hours=24),
        ).exists():
            return HttpResponse(status=200)

        from django.core.mail import send_mail
        subject_line = f"[Made in İzmir] Abonelik Talebi: {plan_name} - {name}"
        body = (
            f"Ad Soyad: {name}\n"
            f"E-posta:  {email}\n"
            f"Telefon:  {phone or '-'}\n"
            f"Konu:     Abonelik Talebi - {plan_name}\n\n"
            f"Mesaj:\n{full_message}"
        )
        email_ok = True
        try:
            send_mail(
                subject_line, body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception:
            email_ok = False

        ContactSubmission.objects.create(
            name=name, email=email, phone=phone,
            subject=f"Abonelik Talebi - {plan_name}",
            message=full_message,
            ip_address=client_ip, email_sent=email_ok,
        )

        if not email_ok:
            return HttpResponse(status=500)
        return HttpResponse(status=200)

    # GET
    ts = int(time.time())
    context = {
        'plans': plans,
        'current_plan': current_plan,
        'pricing_tenant': pricing_tenant,
        'form_ts': ts,
        'form_tk': _make_form_token(ts),
    }
    return render(request, 'subscriptions/pricing.html', context)


@login_required
def my_subscription_view(request):
    """User's subscription status page (login required)."""
    try:
        tenant = request.user.profile.tenant
    except Exception:
        return redirect('accounts:dashboard')

    if not tenant:
        return redirect('accounts:dashboard')

    plan = tenant.get_active_plan()

    try:
        subscription = tenant.subscription
    except Exception:
        subscription = None

    active_product_count = tenant.products.filter(is_active=True).count() if tenant.is_producer else None

    all_plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')

    context = {
        'plan': plan,
        'subscription': subscription,
        'tenant': tenant,
        'active_product_count': active_product_count,
        'all_plans': all_plans,
    }
    return render(request, 'subscriptions/my_subscription.html', context)
