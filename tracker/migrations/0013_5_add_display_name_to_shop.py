# Generated migration to add missing display_name column to existing shop table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0013_4_create_shop_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='display_name',
            field=models.CharField(max_length=100, default='Default Shop', verbose_name='Display Name'),
        ),
    ]
