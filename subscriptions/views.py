from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan


def pricing_view(request):
    """Public subscription pricing page."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')

    current_plan = None
    if request.user.is_authenticated:
        try:
            tenant = request.user.profile.tenant
            if tenant:
                current_plan = tenant.get_active_plan()
        except Exception:
            pass

    context = {
        'plans': plans,
        'current_plan': current_plan,
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
