"""
Data migration: Seeds the three default subscription plans (Standard, Plus, Premium)
and assigns the Standard plan to all existing Tenants.
"""
from django.db import migrations
from datetime import date


def seed_plans_and_assign(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    TenantSubscription = apps.get_model('subscriptions', 'TenantSubscription')
    Tenant = apps.get_model('accounts', 'Tenant')

    today = date.today()

    standard = SubscriptionPlan.objects.create(
        name_tr='Standart',
        name_en='Standard',
        description_tr='Temel üyelik paketi. Ücretsiz olarak sunulmaktadır.',
        description_en='Basic membership package. Offered for free.',
        monthly_price=0,
        show_company_profile=False,
        company_username_editable=False,
        has_business_card=False,
        display_company_name=False,
        display_open_address=False,
        display_city=True,
        display_phone=False,
        display_email=False,
        display_website=False,
        max_active_products=5,
        display_order=1,
        is_active=True,
    )

    SubscriptionPlan.objects.create(
        name_tr='Artı',
        name_en='Plus',
        description_tr='Gelişmiş görünürlük özellikleri ile işletmenizi öne çıkarın.',
        description_en='Stand out with enhanced visibility features.',
        monthly_price=1000,
        show_company_profile=False,
        company_username_editable=False,
        has_business_card=False,
        display_company_name=True,
        display_open_address=False,
        display_city=True,
        display_phone=False,
        display_email=False,
        display_website=False,
        max_active_products=15,
        display_order=2,
        is_active=True,
    )

    SubscriptionPlan.objects.create(
        name_tr='Premium',
        name_en='Premium',
        description_tr='Tüm özellikler açık. Sınırsız ürün. Tam görünürlük.',
        description_en='All features included. Unlimited products. Full visibility.',
        monthly_price=5000,
        show_company_profile=True,
        company_username_editable=True,
        has_business_card=True,
        display_company_name=True,
        display_open_address=True,
        display_city=True,
        display_phone=True,
        display_email=True,
        display_website=True,
        max_active_products=None,
        display_order=3,
        is_active=True,
    )

    # Assign Standard to all existing tenants
    for tenant in Tenant.objects.all():
        TenantSubscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': standard,
                'status': 'active',
                'started_at': today,
                'expires_at': None,
            }
        )


def reverse_seed(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    TenantSubscription = apps.get_model('subscriptions', 'TenantSubscription')
    TenantSubscription.objects.all().delete()
    SubscriptionPlan.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('subscriptions', '0001_initial'),
        ('accounts', '0011_producer_enquiry'),
    ]
    operations = [
        migrations.RunPython(seed_plans_and_assign, reverse_seed),
    ]
