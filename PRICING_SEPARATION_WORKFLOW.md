# Pricing Separation Workflow

## 🎯 Concept

**Products** and **Stationery Items** now have **independent pricing** while maintaining **automatic stock synchronization**.

## 📊 Pricing Systems

### **Products (Bulk Management)**
```
📦 Product: Spring Files PVC - Large
├── Supplier Price: TZS 15,000 (what you pay supplier)
├── Selling Price: TZS 20,000 (bulk selling price)
├── Units per Carton: 100
├── Cartons in Stock: 25
└── Total Units: 2,500 (automatically calculated)
```

### **Stationery Items (Retail Management)**
```
🏪 Stationery Item: Spring Files PVC - Large
├── Cost Price: TZS 18,000 (your retail cost - set by you)
├── Unit Price: TZS 250 (retail selling price - set by you)
├── Stock Quantity: 2,500 (auto-synced from product)
└── Profit Margin: 38.9% (calculated from retail prices)
```

## 🔄 Workflow

### **Step 1: Create Product**
1. **Products** → **Add Product**
2. Enter bulk details (supplier price, carton info)
3. **Save** → Creates stationery item with initial pricing

### **Step 2: Set Retail Pricing**
1. **Products** → **View Product** 
2. Click **"📦 View Stationery Item"**
3. **Edit** the stationery item
4. Set your retail prices (cost price, unit price)
5. **Save** → Retail pricing now independent

### **Step 3: Manage Stock**
- Update product cartons → Stationery stock auto-syncs
- Retail pricing remains unchanged
- Perfect inventory separation

## 💰 Pricing Strategy Examples

### **Spring Files PVC - Large**
```
Bulk (Product):          Retail (Stationery):
├── Cost: TZS 15,000     ├── Cost: TZS 18,000  
├── Sell: TZS 20,000     ├── Sell: TZS 250
├── Per unit: TZS 200    ├── Per unit: TZS 250
└── Margin: 25%          └── Margin: 38.9%
```

### **Benefits:**
- **Bulk purchases**: Track supplier costs accurately
- **Retail sales**: Set competitive retail prices
- **Different margins**: Separate profit strategies
- **Stock sync**: Always accurate inventory

## 🎮 Quick Actions

### **Update Product Stock:**
```
Products → Edit Product → Cartons: 25 → 30 → Save
Result: Stationery stock updates 2,500 → 3,000 units
Retail pricing: Unchanged ✅
```

### **Update Retail Pricing:**
```
Products → View Product → 📦 View Stationery Item → Edit
Change Unit Price: TZS 250 → TZS 280 → Save  
Result: Retail pricing updated
Product pricing: Unchanged ✅
```

## 📈 Business Benefits

1. **Accurate Cost Tracking**: Know exactly what you pay suppliers
2. **Flexible Retail Pricing**: Set competitive prices for customers  
3. **Profit Analysis**: Separate margins for bulk vs retail
4. **Stock Accuracy**: Never worry about inventory counts
5. **Business Intelligence**: Clear view of both operations

## ✅ Verification

When you view a product, you should see:
- 📦 **Linked Stationery Item** section
- 💰 **Retail Unit Price** displayed
- ℹ️ **"Pricing managed separately for retail sales"** note
- 🔄 **"Stock automatically synced"** confirmation

**Your pricing is now completely independent while maintaining perfect stock synchronization!** 🎉
