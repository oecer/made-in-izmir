from django import template

register = template.Library()


@register.inclusion_tag('ads/ad_banner.html', takes_context=True)
def render_ad(context, slot_slug):
    ads_by_slot = context.get('ads_by_slot', {})
    ad_slots = context.get('ad_slots', {})
    ads = ads_by_slot.get(slot_slug, [])
    slot = ad_slots.get(slot_slug)

    # For horizontal banners only show the highest-priority (lowest order) ad
    top_ad = ads[0] if ads else None

    return {
        'ad': top_ad,
        'slot': slot,
    }


@register.inclusion_tag('ads/ad_grid_card.html', takes_context=True)
def render_grid_ad(context, slot_slug, product_index):
    ads_by_slot = context.get('ads_by_slot', {})
    ad_slots = context.get('ad_slots', {})
    ads = ads_by_slot.get(slot_slug, [])
    slot = ad_slots.get(slot_slug)

    if not ads or not slot:
        return {'show': False}

    grid_interval = slot.grid_interval

    # Show ad after every grid_interval-th product (1-based count)
    if (product_index + 1) % grid_interval != 0:
        return {'show': False}

    # Cycle through available ads
    cycle_index = ((product_index + 1) // grid_interval - 1) % len(ads)
    return {
        'show': True,
        'ad': ads[cycle_index],
        'slot': slot,
    }
