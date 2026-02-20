# Generated manually to fix debt shop assignments

import django.db.models.deletion
from django.db import migrations, models


def fix_debt_shop_assignments(apps, schema_editor):
    """Fix debt shop assignments based on their items"""
    Debt = apps.get_model('tracker', 'Debt')
    StationeryItem = apps.get_model('tracker', 'StationeryItem')
    
    # Update all debts to use their item's shop
    debts_to_update = []
    for debt in Debt.objects.all():
        if debt.item and debt.item.shop:
            debt.shop = debt.item.shop
            debts_to_update.append(debt)
    
    # Bulk update
    if debts_to_update:
        Debt.objects.bulk_update(debts_to_update, ['shop'])
        print(f"Updated {len(debts_to_update)} debts to use their item's shop")


def reverse_fix_debt_shop_assignments(apps, schema_editor):
    """Reverse debt shop assignments fix"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0016_category_shop_debt_shop_expenditure_shop_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_debt_shop_assignments, reverse_fix_debt_shop_assignments),
    ]
