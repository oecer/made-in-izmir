from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_contactsubmission_alter_consenttext_id_and_more'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='tenant',
                    name='buyer_interested_sectors',
                    field=models.ManyToManyField(blank=True, related_name='interested_buyer_tenants', to='catalog.sector', verbose_name='İlgilenilen Sektörler'),
                ),
                migrations.AddField(
                    model_name='tenant',
                    name='producer_sectors',
                    field=models.ManyToManyField(blank=True, related_name='producer_tenants', to='catalog.sector', verbose_name='Sektörler'),
                ),
            ],
            database_operations=[],
        ),
    ]
