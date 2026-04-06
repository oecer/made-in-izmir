from datetime import date


def ad_context(request):
    _cache_key = '_ads_context_cache'
    cached = getattr(request, _cache_key, None)
    if cached is not None:
        return cached

    # Import here to avoid issues before migrations run
    from .models import Ad, AdSlot

    today = date.today()

    active_ads = (
        Ad.objects
        .filter(
            is_active=True,
            slot__is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .select_related('slot')
        .order_by('slot__slug', 'order')
    )

    ads_by_slot = {}
    for ad in active_ads:
        ads_by_slot.setdefault(ad.slot.slug, []).append(ad)

    ad_slots = {
        slot.slug: slot
        for slot in AdSlot.objects.filter(is_active=True)
    }

    result = {
        'ads_by_slot': ads_by_slot,
        'ad_slots': ad_slots,
    }
    setattr(request, _cache_key, result)
    return result
