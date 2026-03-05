from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0017_alter_tenant_owner'),
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Sector',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name_tr', models.CharField(max_length=200, verbose_name='Sektör Adı (TR)')),
                        ('name_en', models.CharField(max_length=200, verbose_name='Sektör Adı (EN)')),
                    ],
                    options={
                        'verbose_name': 'Sektör',
                        'verbose_name_plural': 'Sektörler',
                        'ordering': ['name_tr'],
                        'db_table': 'main_sector',
                    },
                ),
                migrations.CreateModel(
                    name='ProductTag',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name_tr', models.CharField(max_length=100, verbose_name='Etiket Adı (TR)')),
                        ('name_en', models.CharField(max_length=100, verbose_name='Etiket Adı (EN)')),
                    ],
                    options={
                        'verbose_name': 'Ürün Etiketi',
                        'verbose_name_plural': 'Ürün Etiketleri',
                        'ordering': ['name_tr'],
                        'db_table': 'main_producttag',
                    },
                ),
                migrations.CreateModel(
                    name='ProductRequest',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title_tr', models.CharField(blank=True, max_length=200, verbose_name='Ürün Başlığı (TR)')),
                        ('title_en', models.CharField(blank=True, max_length=200, verbose_name='Ürün Başlığı (EN)')),
                        ('description_tr', models.TextField(blank=True, verbose_name='Ürün Açıklaması (TR)')),
                        ('description_en', models.TextField(blank=True, verbose_name='Ürün Açıklaması (EN)')),
                        ('photo1', models.ImageField(blank=True, null=True, upload_to='product_requests/', verbose_name='Fotoğraf 1')),
                        ('photo2', models.ImageField(blank=True, null=True, upload_to='product_requests/', verbose_name='Fotoğraf 2')),
                        ('photo3', models.ImageField(blank=True, null=True, upload_to='product_requests/', verbose_name='Fotoğraf 3')),
                        ('tags_ids', models.TextField(blank=True, null=True, verbose_name="Etiket ID'leri")),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Durum')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='İnceleme Tarihi')),
                        ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='Red Nedeni')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('producer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_requests', to=settings.AUTH_USER_MODEL, verbose_name='Üretici')),
                        ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_requests', to='accounts.tenant', verbose_name='Firma')),
                        ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_requests', to='catalog.sector', verbose_name='Sektör')),
                        ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_products', to=settings.AUTH_USER_MODEL, verbose_name='İnceleyen')),
                    ],
                    options={
                        'verbose_name': 'Ürün Talebi',
                        'verbose_name_plural': 'Ürün Talepleri',
                        'ordering': ['-created_at'],
                        'db_table': 'main_productrequest',
                    },
                ),
                migrations.CreateModel(
                    name='Product',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title_tr', models.CharField(blank=True, max_length=200, verbose_name='Ürün Başlığı (TR)')),
                        ('title_en', models.CharField(blank=True, max_length=200, verbose_name='Ürün Başlığı (EN)')),
                        ('description_tr', models.TextField(blank=True, verbose_name='Ürün Açıklaması (TR)')),
                        ('description_en', models.TextField(blank=True, verbose_name='Ürün Açıklaması (EN)')),
                        ('photo1', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Fotoğraf 1')),
                        ('photo2', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Fotoğraf 2')),
                        ('photo3', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Fotoğraf 3')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('producer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL, verbose_name='Üretici')),
                        ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='accounts.tenant', verbose_name='Firma')),
                        ('tags', models.ManyToManyField(blank=True, related_name='products', to='catalog.producttag', verbose_name='Etiketler')),
                        ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='catalog.sector', verbose_name='Sektör')),
                    ],
                    options={
                        'verbose_name': 'Ürün',
                        'verbose_name_plural': 'Ürünler',
                        'ordering': ['-created_at'],
                        'db_table': 'main_product',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
