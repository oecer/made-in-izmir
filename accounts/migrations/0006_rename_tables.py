from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_open_address_to_profileeditrequest'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='signuprequest',
            table='accounts_signuprequest',
        ),
        migrations.AlterModelTable(
            name='signuprequesthistory',
            table='accounts_signuprequesthistory',
        ),
        migrations.AlterModelTable(
            name='consenttext',
            table='accounts_consenttext',
        ),
        migrations.AlterModelTable(
            name='membershipconsent',
            table='accounts_membershipconsent',
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='accounts_userprofile',
        ),
        migrations.AlterModelTable(
            name='contactsubmission',
            table='accounts_contactsubmission',
        ),
        migrations.AlterModelTable(
            name='profileeditrequest',
            table='accounts_profileeditrequest',
        ),
        # Tenant has M2M fields - AlterModelTable handles renaming M2M tables automatically
        migrations.AlterModelTable(
            name='tenant',
            table='accounts_tenant',
        ),
    ]
