from datetime import date
from django.db import migrations


def create_ad_slots_and_dummy_ads(apps, schema_editor):
    AdSlot = apps.get_model('ads', 'AdSlot')
    Ad = apps.get_model('ads', 'Ad')

    slots_data = [
        {
            'slug': 'home_hero_horizontal',
            'name': 'Ana Sayfa Hero Altı',
            'description': 'Ana sayfada hero bölümünün altında, CTA butonlarının hemen altında gösterilir.',
            'width_px': 970,
            'height_px': 90,
            'ad_type': 'horizontal',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'products_top_horizontal',
            'name': 'Ürünler Sayfası Üst',
            'description': 'Ürünler sayfasında hero bölümünün altında, filtre çubuğunun üstünde gösterilir.',
            'width_px': 970,
            'height_px': 90,
            'ad_type': 'horizontal',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'products_grid_card',
            'name': 'Ürünler Grid Kartı',
            'description': 'Ürünler sayfasındaki ürün grid\'ine her N. üründen sonra ürün kartı gibi yerleştirilen reklam.',
            'width_px': 280,
            'height_px': 380,
            'ad_type': 'grid_card',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'product_detail_top',
            'name': 'Ürün Detay Üst',
            'description': 'Ürün detay sayfasında ürün içeriğinin üstünde gösterilir.',
            'width_px': 970,
            'height_px': 90,
            'ad_type': 'horizontal',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'product_detail_bottom',
            'name': 'Ürün Detay Alt',
            'description': 'Ürün detay sayfasında ürün içeriğinin altında gösterilir.',
            'width_px': 970,
            'height_px': 90,
            'ad_type': 'horizontal',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'buyer_dashboard_horizontal',
            'name': 'Alıcı Paneli Yatay',
            'description': 'Alıcı panelinde Hızlı Bağlantılar bölümünün altında gösterilir.',
            'width_px': 970,
            'height_px': 90,
            'ad_type': 'horizontal',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
        {
            'slug': 'buyer_dashboard_grid_card',
            'name': 'Alıcı Paneli Grid Kartı',
            'description': 'Alıcı panelindeki ürün grid\'ine her N. üründen sonra ürün kartı gibi yerleştirilen reklam.',
            'width_px': 280,
            'height_px': 380,
            'ad_type': 'grid_card',
            'grid_interval': 6,
            'max_ads_in_grid': 3,
        },
    ]

    for data in slots_data:
        slot = AdSlot.objects.create(
            is_active=True,
            price_daily=None,
            price_weekly=None,
            price_monthly=None,
            price_currency='TRY',
            **data,
        )
        Ad.objects.create(
            slot=slot,
            advertiser_name='Reklam Alanı',
            image='',
            link_url='#',
            title=f'Buraya reklam verebilirsiniz – {slot.width_px}×{slot.height_px} px',
            start_date=date(2024, 1, 1),
            end_date=date(2099, 12, 31),
            order=0,
            is_active=True,
        )


def reverse_func(apps, schema_editor):
    AdSlot = apps.get_model('ads', 'AdSlot')
    AdSlot.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_ad_slots_and_dummy_ads, reverse_func),
    ]
