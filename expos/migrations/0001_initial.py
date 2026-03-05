from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0017_alter_tenant_owner'),
        ('accounts', '0001_initial'),
        ('catalog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Expo',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title_tr', models.CharField(max_length=200, verbose_name='Fuar Başlığı (TR)')),
                        ('title_en', models.CharField(max_length=200, verbose_name='Fuar Başlığı (EN)')),
                        ('description_tr', models.TextField(verbose_name='Fuar Açıklaması (TR)')),
                        ('description_en', models.TextField(verbose_name='Fuar Açıklaması (EN)')),
                        ('location_tr', models.CharField(max_length=200, verbose_name='Konum (TR)')),
                        ('location_en', models.CharField(max_length=200, verbose_name='Konum (EN)')),
                        ('start_date', models.DateField(verbose_name='Başlangıç Tarihi')),
                        ('end_date', models.DateField(verbose_name='Bitiş Tarihi')),
                        ('registration_deadline', models.DateField(verbose_name='Kayıt Son Tarihi')),
                        ('image', models.ImageField(blank=True, null=True, upload_to='expos/', verbose_name='Fuar Görseli')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Fuar',
                        'verbose_name_plural': 'Fuarlar',
                        'ordering': ['start_date'],
                        'db_table': 'main_expo',
                    },
                ),
                migrations.CreateModel(
                    name='ExpoSignup',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('product_count', models.IntegerField(verbose_name='Ürün Sayısı')),
                        ('uses_listed_products', models.BooleanField(default=False, verbose_name="Made in İzmir'de Listelenen Ürünler")),
                        ('product_description', models.TextField(blank=True, verbose_name='Ürün Açıklaması')),
                        ('notes', models.TextField(blank=True, verbose_name='Notlar')),
                        ('status', models.CharField(choices=[('pending', 'Beklemede'), ('confirmed', 'Onaylandı'), ('cancelled', 'İptal Edildi')], default='pending', max_length=20, verbose_name='Durum')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('expo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signups', to='expos.expo', verbose_name='Fuar')),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expo_signups', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
                        ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expo_signups', to='accounts.tenant', verbose_name='Firma')),
                        ('selected_products', models.ManyToManyField(blank=True, related_name='expo_signups', to='catalog.product', verbose_name='Seçilen Ürünler')),
                    ],
                    options={
                        'verbose_name': 'Fuar Kaydı',
                        'verbose_name_plural': 'Fuar Kayıtları',
                        'ordering': ['-created_at'],
                        'db_table': 'main_exposignup',
                        'unique_together': {('expo', 'user')},
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
