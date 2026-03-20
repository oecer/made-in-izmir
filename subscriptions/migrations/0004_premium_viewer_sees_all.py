"""
Data migration: Enable viewer_sees_all on the existing Premium plan.
"""
from django.db import migrations


def enable_premium_viewer_sees_all(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(monthly_price=5000).update(viewer_sees_all=True)


def reverse_migration(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(monthly_price=5000).update(viewer_sees_all=False)


class Migration(migrations.Migration):
    dependencies = [
        ('subscriptions', '0003_add_viewer_sees_all'),
    ]
    operations = [
        migrations.RunPython(enable_premium_viewer_sees_all, reverse_migration),
    ]
