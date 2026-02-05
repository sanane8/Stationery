from django.core.management.base import BaseCommand
from tracker.models import Product, StationeryItem

class Command(BaseCommand):
    help = 'Sync products with stationery items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Create stationery items for products that don\'t have them',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Syncing Products to Stationery Items...')
        self.stdout.write('=' * 50)
        
        products = Product.objects.all()
        self.stdout.write(f'Found {products.count()} products to sync')
        
        for product in products:
            self.stdout.write(f'\n📦 Processing: {product.name} ({product.sku})')
            
            # Create stationery item if not exists
            if not product.stationery_item and options['create_missing']:
                self.stdout.write('  ➕ Creating stationery item...')
                product.create_stationery_item()
                self.stdout.write(f'  ✅ Created stationery item: {product.stationery_item.name}')
            elif product.stationery_item:
                self.stdout.write('  📋 Stationery item already exists')
            else:
                self.stdout.write('  ⚠️  No stationery item linked (use --create-missing to create)')
                continue
            
            # Sync stock
            self.stdout.write(f'  🔄 Syncing stock...')
            product.sync_with_stationery_item()
            
            # Display sync status
            if product.stationery_item:
                self.stdout.write(f'  📊 Stock Status:')
                self.stdout.write(f'     Product: {product.cartons_in_stock} cartons × {product.units_per_carton} units = {product.total_units_in_stock} units')
                self.stdout.write(f'     Stationery: {product.stationery_item.stock_quantity} units')
                if product.total_units_in_stock == product.stationery_item.stock_quantity:
                    self.stdout.write(f'     ✅ Sync Status: MATCH')
                else:
                    self.stdout.write(f'     ❌ Sync Status: MISMATCH')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('🎉 Sync Complete!')
        
        # Summary
        total_products = Product.objects.count()
        linked_products = Product.objects.filter(stationery_item__isnull=False).count()
        
        self.stdout.write(f'\n📈 Summary:')
        self.stdout.write(f'   Total Products: {total_products}')
        self.stdout.write(f'   Linked to Stationery: {linked_products}')
        self.stdout.write(f'   Not Linked: {total_products - linked_products}')
