# Product-Stationery Synchronization Guide

## 🎯 Overview

This system synchronizes stock quantities between Products (managed in cartons) and Stationery Items (managed in individual units). **Pricing is managed separately** - Products track supplier costs and bulk pricing, while Stationery Items have their own retail pricing that you set manually for individual sales.

## 🔄 How It Works

### 1. **Product Model Enhancement**
- Added `stationery_item` field to link Product with StationeryItem
- Added automatic stock sync methods in Product model
- Override save() method to trigger stock synchronization only

### 2. **Stock Synchronization Only**
- **When Product is created**: Creates corresponding StationeryItem with initial pricing
- **When Product stock is updated**: Updates StationeryItem stock quantity only
- **Pricing Separation**: Product pricing and StationeryItem pricing are independent
- **Stock Calculation**: `StationeryItem.stock_quantity = Product.cartons_in_stock × Product.units_per_carton`

### 3. **Data Flow**
```
Product (Cartons) → StationeryItem (Units)
├── Stock Sync: 25 cartons × 100 units = 2500 units ✅
├── Product Pricing: supplier_price, selling_price (for bulk)
├── Stationery Pricing: unit_price, cost_price (for retail) 
└── Category Sync: ProductCategory → Category
```

## 📊 Current Status

### ✅ **Successfully Linked Products:**
1. **PVC Document Folders**
   - Product: 30 cartons × 200 units = 6000 units
   - Stationery: 6000 units ✅ MATCH
   - Pricing: Independent management

2. **Spring Files PVC - Large**
   - Product: 25 cartons × 100 units = 2500 units  
   - Stationery: 2500 units ✅ MATCH
   - Pricing: Independent management

3. **Spring Files PVC - Small**
   - Product: 15 cartons × 150 units = 2250 units
   - Stationery: 2250 units ✅ MATCH
   - Pricing: Independent management

## 🎮 How to Use

### **Creating New Products:**
1. Go to **Products** → **Add Product**
2. Fill in product details:
   - Name, SKU, Category, Supplier
   - Supplier Price, Selling Price (for bulk calculations)
   - Units per Carton, Cartons in Stock
3. **Save** → Creates linked StationeryItem with initial pricing
4. **Important**: Manually update StationeryItem pricing for retail sales

### **Updating Product Stock:**
1. Go to **Products** → **Edit Product**
2. Update **Cartons in Stock**
3. **Save** → Updates StationeryItem stock only (pricing preserved)

### **Managing Retail Pricing:**
1. Go to **Products** → **View Product**
2. Click **"📦 View Stationery Item"** button
3. **Edit** the StationeryItem to set retail pricing
4. **Result**: Retail pricing independent of product pricing

### **Viewing Sync Status:**
1. Go to **Products** → **View Product**
2. Check **"📦 Linked Stationery Item"** section
3. See stock comparison and separate pricing information

## 🔧 Manual Synchronization

If you need to manually sync products:

```bash
# Using the sync script
python sync_products_to_stationery.py

# Or create stationery items for existing products
python manage.py shell
>>> from tracker.models import Product
>>> for product in Product.objects.all():
...     if not product.stationery_item:
...         product.create_stationery_item()
...         print(f"Created: {product.name}")
```

## 📋 Key Features

### **Stock Sync Only:**
- ✅ Product creation → StationeryItem creation
- ✅ Stock updates → Automatic stock sync
- ❌ Price updates → No sync (pricing independent)
- ✅ Category mapping → Automatic category creation

### **Pricing Separation:**
- **Product Pricing**: Supplier costs, bulk selling prices
- **Stationery Pricing**: Retail unit prices, retail costs (set by you)
- **Independence**: Changing product prices doesn't affect retail prices
- **Flexibility**: Set different profit margins for retail vs bulk

### **Visual Indicators:**
- 🟢 **Green badge**: Stock levels match
- 🔴 **Red badge**: Low stock alert
- 📦 **Cube icon**: View linked StationeryItem
- ⚠️ **Warning**: No stationery item linked
- 💰 **Price display**: Shows retail pricing separately

### **Data Integrity:**
- One-to-one relationship between Product and StationeryItem
- Automatic stock calculations
- Independent pricing management
- Consistent category synchronization

## 🎯 Benefits

1. **Dual Inventory Management**: 
   - Manage bulk products in cartons
   - Individual items automatically tracked
   - Separate pricing for bulk vs retail

2. **Stock Consistency Only**:
   - Stock quantities always synchronized
   - Pricing completely independent
   - No accidental price overwrites

3. **Flexible Pricing Strategy**:
   - Set bulk prices in Products
   - Set retail prices in StationeryItems
   - Different profit margins for different channels

4. **Complete Integration**:
   - Existing sales system works with both
   - Reports include both carton and unit data
   - Clear separation of business functions

## 🚀 Ready for Production

The synchronization system is fully functional and ready for your stationery business. You can now:

- **Add spring files (PVC) in cartons** with bulk pricing
- **Set separate retail prices** for individual sales
- **Maintain perfect inventory synchronization**
- **Manage pricing independently** for different sales channels

**Your products and stationery items now have independent pricing while maintaining perfect stock synchronization!** 🎉
