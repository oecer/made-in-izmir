from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expos', '0001_initial'),
        ('catalog', '0002_rename_tables'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='expo',
            table='expos_expo',
        ),
        # ExpoSignup has M2M selected_products field - AlterModelTable handles renaming M2M tables automatically
        migrations.AlterModelTable(
            name='exposignup',
            table='expos_exposignup',
        ),
    ]
