"""
Context processor that injects `sub_features` into every template.

`sub_features` reflects the CURRENT USER's subscription plan — used for:
  - Gating the user's own dashboard features (business card card, etc.)
  - Showing their own subscription limits

For product detail / buyer dashboard pages, the PRODUCER's plan controls
visibility. Those views must pass `producer_plan` explicitly in their context.
"""


_STANDARD_DEFAULTS = {
    'show_company_profile': False,
    'company_username_editable': False,
    'has_business_card': False,
    'display_company_name': False,
    'display_open_address': False,
    'display_city': True,
    'display_phone': False,
    'display_email': False,
    'display_website': False,
    'viewer_sees_all': False,
    'max_active_products': 5,
    'plan_name_tr': 'Standart',
    'plan_name_en': 'Standard',
    'monthly_price': 0,
}


def subscription_features(request):
    """Inject sub_features dict into every template context."""
    if not request.user.is_authenticated:
        return {'sub_features': _STANDARD_DEFAULTS.copy()}

    # Per-request cache to avoid repeated DB hits within the same request
    _cache_key = '_sub_plan_cache'
    cached = getattr(request, _cache_key, None)
    if cached is not None:
        return {'sub_features': cached}

    try:
        tenant = request.user.profile.tenant
        if not tenant:
            result = _STANDARD_DEFAULTS.copy()
            setattr(request, _cache_key, result)
            return {'sub_features': result}
    except Exception:
        result = _STANDARD_DEFAULTS.copy()
        setattr(request, _cache_key, result)
        return {'sub_features': result}

    plan = tenant.get_active_plan()
    if plan is None:
        result = _STANDARD_DEFAULTS.copy()
        setattr(request, _cache_key, result)
        return {'sub_features': result}

    result = {
        'show_company_profile': plan.show_company_profile,
        'company_username_editable': plan.company_username_editable,
        'has_business_card': plan.has_business_card,
        'display_company_name': plan.display_company_name,
        'display_open_address': plan.display_open_address,
        'display_city': plan.display_city,
        'display_phone': plan.display_phone,
        'display_email': plan.display_email,
        'display_website': plan.display_website,
        'viewer_sees_all': plan.viewer_sees_all,
        'max_active_products': plan.max_active_products,
        'plan_name_tr': plan.name_tr,
        'plan_name_en': plan.name_en,
        'monthly_price': plan.monthly_price,
    }
    setattr(request, _cache_key, result)
    return {'sub_features': result}
