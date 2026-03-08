from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('accounts', '0006_rename_tables'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='sector',
            table='catalog_sector',
        ),
        migrations.AlterModelTable(
            name='producttag',
            table='catalog_producttag',
        ),
        migrations.AlterModelTable(
            name='productrequest',
            table='catalog_productrequest',
        ),
        # Product has M2M tags field - AlterModelTable handles renaming M2M tables automatically
        migrations.AlterModelTable(
            name='product',
            table='catalog_product',
        ),
    ]
