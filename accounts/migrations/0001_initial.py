from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0017_alter_tenant_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='SignupRequest',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('username', models.CharField(max_length=150, unique=True)),
                        ('email', models.EmailField(max_length=254)),
                        ('first_name', models.CharField(max_length=100)),
                        ('last_name', models.CharField(max_length=100)),
                        ('password_hash', models.CharField(max_length=255)),
                        ('company_name', models.CharField(max_length=200)),
                        ('phone_number', models.CharField(max_length=20)),
                        ('country', models.CharField(max_length=100)),
                        ('city', models.CharField(max_length=100)),
                        ('open_address', models.TextField(blank=True, null=True)),
                        ('website', models.URLField(blank=True, max_length=255, null=True)),
                        ('about_company', models.TextField(blank=True, null=True)),
                        ('is_buyer', models.BooleanField(default=False)),
                        ('is_producer', models.BooleanField(default=False)),
                        ('buyer_interested_sectors_ids', models.TextField(blank=True, null=True)),
                        ('buyer_quarterly_volume', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                        ('producer_sectors_ids', models.TextField(blank=True, null=True)),
                        ('producer_quarterly_sales', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                        ('producer_product_count', models.IntegerField(blank=True, null=True)),
                        ('consent_given', models.BooleanField(default=False, verbose_name='Üyelik Onayı Verildi')),
                        ('consent_timestamp', models.DateTimeField(blank=True, null=True, verbose_name='Onay Tarihi/Saati')),
                        ('consent_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='Onay IP Adresi')),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                        ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                        ('rejection_reason', models.TextField(blank=True, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_signups', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'verbose_name': 'Kayıt Talebi',
                        'verbose_name_plural': 'Kayıt Talepleri',
                        'ordering': ['-created_at'],
                        'db_table': 'main_signuprequest',
                    },
                ),
                migrations.CreateModel(
                    name='SignupRequestHistory',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('changed_at', models.DateTimeField(auto_now_add=True, verbose_name='Değiştirilme Tarihi')),
                        ('changes', models.JSONField(verbose_name='Değişiklikler')),
                        ('signup_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='accounts.signuprequest', verbose_name='Kayıt Talebi')),
                        ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Değiştiren')),
                    ],
                    options={
                        'verbose_name': 'Kayıt Talebi Geçmişi',
                        'verbose_name_plural': 'Kayıt Talebi Geçmişi',
                        'ordering': ['-changed_at'],
                        'db_table': 'main_signuprequesthistory',
                    },
                ),
                migrations.CreateModel(
                    name='ConsentText',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('text_tr', models.TextField(help_text="Kayıt formunda ve onay popup'ında gösterilecek Türkçe metin.", verbose_name='Onay Metni (Türkçe)')),
                        ('text_en', models.TextField(help_text='English text shown in the registration form and confirmation popup.', verbose_name='Consent Text (English)')),
                        ('version', models.CharField(default='v1.0', help_text='Değişiklik yapıldığında versiyonu güncelleyin (örn. v1.1). Bu değer onay kayıtlarına işlenir.', max_length=20, verbose_name='Versiyon')),
                        ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Son Güncelleme')),
                    ],
                    options={
                        'verbose_name': 'Üyelik Onay Metni',
                        'verbose_name_plural': 'Üyelik Onay Metni',
                        'db_table': 'main_consenttext',
                    },
                ),
                migrations.CreateModel(
                    name='MembershipConsent',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('username', models.CharField(max_length=150, verbose_name='Kullanıcı Adı')),
                        ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                        ('company_name', models.CharField(max_length=200, verbose_name='Firma Adı')),
                        ('consent_given_at', models.DateTimeField(verbose_name='Onay Tarihi/Saati')),
                        ('ip_address', models.GenericIPAddressField(verbose_name='IP Adresi')),
                        ('consent_text_version', models.CharField(default='v1.0', max_length=50, verbose_name='Onay Metni Versiyonu')),
                        ('signup_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consent_records', to='accounts.signuprequest', verbose_name='Kayıt Talebi')),
                    ],
                    options={
                        'verbose_name': 'Üyelik Onay Kaydı',
                        'verbose_name_plural': 'Üyelik Onay Kayıtları',
                        'ordering': ['-consent_given_at'],
                        'db_table': 'main_membershipconsent',
                    },
                ),
                migrations.CreateModel(
                    name='Tenant',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                        ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_tenants', to=settings.AUTH_USER_MODEL, verbose_name='Firma Hesabı Sahibi')),
                        ('buyer_interested_sectors', models.ManyToManyField(blank=True, related_name='interested_buyer_tenants', to='catalog.sector', verbose_name='İlgilenilen Sektörler')),
                        ('producer_sectors', models.ManyToManyField(blank=True, related_name='producer_tenants', to='catalog.sector', verbose_name='Sektörler')),
                    ],
                    options={
                        'verbose_name': 'Firma (Tenant)',
                        'verbose_name_plural': 'Firmalar (Tenants)',
                        'ordering': ['company_name'],
                        'db_table': 'main_tenant',
                    },
                ),
                migrations.CreateModel(
                    name='UserProfile',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('tenant_role', models.CharField(choices=[('admin', 'Admin'), ('read_only', 'Read Only')], default='admin', max_length=20, verbose_name='Firma Rolü')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
                        ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='accounts.tenant', verbose_name='Firma')),
                    ],
                    options={
                        'verbose_name': 'Kullanıcı Profili',
                        'verbose_name_plural': 'Kullanıcı Profilleri',
                        'db_table': 'main_userprofile',
                    },
                ),
                migrations.CreateModel(
                    name='ProfileEditRequest',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('first_name', models.CharField(blank=True, max_length=100, verbose_name='Ad')),
                        ('last_name', models.CharField(blank=True, max_length=100, verbose_name='Soyad')),
                        ('company_name', models.CharField(blank=True, max_length=200, verbose_name='Firma Adı')),
                        ('phone_number', models.CharField(blank=True, max_length=20, verbose_name='Telefon Numarası')),
                        ('country', models.CharField(blank=True, max_length=100, verbose_name='Ülke')),
                        ('city', models.CharField(blank=True, max_length=100, verbose_name='Şehir')),
                        ('buyer_interested_sectors_ids', models.TextField(blank=True, null=True, verbose_name="İlgilenilen Sektör ID'leri")),
                        ('buyer_quarterly_volume', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Çeyreklik Alım Hacmi (USD)')),
                        ('producer_sectors_ids', models.TextField(blank=True, null=True, verbose_name="Sektör ID'leri")),
                        ('producer_quarterly_sales', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Çeyreklik Satış Hacmi (USD)')),
                        ('producer_product_count', models.IntegerField(blank=True, null=True, verbose_name='Yaklaşık Ürün Sayısı')),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Durum')),
                        ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='İnceleme Tarihi')),
                        ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='Red Nedeni')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_edit_requests', to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
                        ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_profile_edits', to=settings.AUTH_USER_MODEL, verbose_name='İnceleyen')),
                    ],
                    options={
                        'verbose_name': 'Profil Düzenleme Talebi',
                        'verbose_name_plural': 'Profil Düzenleme Talepleri',
                        'ordering': ['-created_at'],
                        'db_table': 'main_profileeditrequest',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
