from django.db import migrations


def backfill_company_username(apps, schema_editor):
    Tenant = apps.get_model('accounts', 'Tenant')
    for tenant in Tenant.objects.filter(company_username__isnull=True):
        tenant.company_username = f"firma{tenant.pk}"
        tenant.save(update_fields=['company_username'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_add_company_email_to_tenant'),
    ]

    operations = [
        migrations.RunPython(backfill_company_username, migrations.RunPython.noop),
    ]
