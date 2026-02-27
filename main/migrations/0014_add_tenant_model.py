from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_profiles_to_tenants(apps, schema_editor):
    """Create Tenant for each UserProfile and link them."""
    UserProfile = apps.get_model('main', 'UserProfile')
    Tenant = apps.get_model('main', 'Tenant')
    Product = apps.get_model('main', 'Product')
    ProductRequest = apps.get_model('main', 'ProductRequest')
    ExpoSignup = apps.get_model('main', 'ExpoSignup')

    for profile in UserProfile.objects.all():
        tenant = Tenant.objects.create(
            company_name=profile.company_name,
            phone_number=profile.phone_number,
            country=profile.country,
            city=profile.city,
            open_address=profile.open_address or '',
            website=profile.website or '',
            about_company=profile.about_company or '',
            is_buyer=profile.is_buyer,
            is_producer=profile.is_producer,
            buyer_quarterly_volume=profile.buyer_quarterly_volume,
            producer_quarterly_sales=profile.producer_quarterly_sales,
            producer_product_count=profile.producer_product_count,
        )

        # Copy M2M relationships
        tenant.buyer_interested_sectors.set(profile.buyer_interested_sectors.all())
        tenant.producer_sectors.set(profile.producer_sectors.all())

        # Link profile to tenant
        profile.tenant = tenant
        profile.save()

        # Link all products by this user to the tenant
        Product.objects.filter(producer=profile.user).update(tenant=tenant)

        # Link all product requests by this user to the tenant
        ProductRequest.objects.filter(producer=profile.user).update(tenant=tenant)

        # Link all expo signups by this user to the tenant
        ExpoSignup.objects.filter(user=profile.user).update(tenant=tenant)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0013_signuprequest_about_company_and_more'),
    ]

    operations = [
        # Step 1: Create Tenant model
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, verbose_name='Firma Adı')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Telefon Numarası')),
                ('country', models.CharField(max_length=100, verbose_name='Ülke')),
                ('city', models.CharField(max_length=100, verbose_name='Şehir')),
                ('open_address', models.TextField(blank=True, null=True, verbose_name='Açık Adres')),
                ('website', models.URLField(blank=True, max_length=255, null=True, verbose_name='Web Sitesi')),
                ('about_company', models.TextField(blank=True, null=True, verbose_name='Firma Hakkında')),
                ('is_buyer', models.BooleanField(default=False, verbose_name='Alıcı')),
                ('is_producer', models.BooleanField(default=False, verbose_name='Üretici')),
                ('buyer_quarterly_volume', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Çeyreklik Alım Hacmi (USD)')),
                ('producer_quarterly_sales', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Çeyreklik Satış Hacmi (USD)')),
                ('producer_product_count', models.IntegerField(blank=True, null=True, verbose_name='Yaklaşık Ürün Sayısı')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('buyer_interested_sectors', models.ManyToManyField(blank=True, related_name='interested_buyer_tenants', to='main.sector', verbose_name='İlgilenilen Sektörler')),
                ('producer_sectors', models.ManyToManyField(blank=True, related_name='producer_tenants', to='main.sector', verbose_name='Sektörler')),
            ],
            options={
                'verbose_name': 'Firma (Tenant)',
                'verbose_name_plural': 'Firmalar (Tenants)',
                'ordering': ['company_name'],
            },
        ),

        # Step 2: Add nullable tenant FK to UserProfile, Product, ProductRequest, ExpoSignup
        migrations.AddField(
            model_name='userprofile',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='main.tenant', verbose_name='Firma'),
        ),
        migrations.AddField(
            model_name='product',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='main.tenant', verbose_name='Firma'),
        ),
        migrations.AddField(
            model_name='productrequest',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_requests', to='main.tenant', verbose_name='Firma'),
        ),
        migrations.AddField(
            model_name='exposignup',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expo_signups', to='main.tenant', verbose_name='Firma'),
        ),

        # Step 3: Data migration - populate tenants from existing profiles
        migrations.RunPython(migrate_profiles_to_tenants, migrations.RunPython.noop),

        # Step 4: Remove old fields from UserProfile
        migrations.RemoveField(model_name='userprofile', name='about_company'),
        migrations.RemoveField(model_name='userprofile', name='buyer_interested_sectors'),
        migrations.RemoveField(model_name='userprofile', name='buyer_quarterly_volume'),
        migrations.RemoveField(model_name='userprofile', name='city'),
        migrations.RemoveField(model_name='userprofile', name='company_name'),
        migrations.RemoveField(model_name='userprofile', name='country'),
        migrations.RemoveField(model_name='userprofile', name='is_buyer'),
        migrations.RemoveField(model_name='userprofile', name='is_producer'),
        migrations.RemoveField(model_name='userprofile', name='open_address'),
        migrations.RemoveField(model_name='userprofile', name='phone_number'),
        migrations.RemoveField(model_name='userprofile', name='producer_product_count'),
        migrations.RemoveField(model_name='userprofile', name='producer_quarterly_sales'),
        migrations.RemoveField(model_name='userprofile', name='producer_sectors'),
        migrations.RemoveField(model_name='userprofile', name='website'),
    ]
