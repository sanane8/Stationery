# Generated migration to create Shop model before other migrations reference it

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0013_shop_product_shop_stationeryitem_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('stationery', 'Stationery Shop'), ('duka_la_vinywaji', 'Duka la Vinywaji')], max_length=50, unique=True, verbose_name='Name')),
                ('display_name', models.CharField(max_length=100, verbose_name='Display Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('address', models.TextField(blank=True, verbose_name='Address')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Phone')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Shop',
                'verbose_name_plural': 'Shops',
                'ordering': ['name'],
            },
        ),
    ]
