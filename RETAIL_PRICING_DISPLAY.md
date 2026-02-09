# Retail Pricing Display Guide

## 🎯 Overview

When viewing a Product (like OPC), the **"📦 Linked Stationery Item"** section now displays **retail pricing information** from the Stationery Item system, not the bulk pricing from the Product system.

## 📊 What You See

### **Product Detail Page - Stationery Item Section**
```
📦 Linked Stationery Item
┌─────────────────────────┬─────────────────────────┐
│ Name: OPC                │ Retail Unit Price: TZS 25,000
│ SKU: OPC-001             │ Retail Cost Price: TZS 18,000  
│ Stock Quantity: 2,500    │ Retail Profit Margin: 38.9%
│                         │                         │
│ 🔄 Stock auto-synced     │ 💰 Retail pricing info  │
│ ℹ️ Pricing managed       │    from stationery item │
└─────────────────────────┴─────────────────────────┘
```

## 🔄 Data Sources

### **Product System (Bulk)**
```
📦 Product: OPC
├── Supplier Price: TZS 15,000 (what you pay supplier)
├── Selling Price: TZS 20,000 (bulk selling price)
├── Cartons: 25 × 100 units = 2,500 units
└── Purpose: Bulk purchasing and cost tracking
```

### **Stationery Item System (Retail)**
```
🏪 Stationery Item: OPC
├── Cost Price: TZS 18,000 (your retail cost)
├── Unit Price: TZS 25,000 (retail selling price)
├── Stock: 2,500 units (auto-synced)
├── Profit Margin: 38.9% (calculated from retail prices)
└── Purpose: Individual sales and customer pricing
```

## 📈 Display Features

### **Retail Pricing Table:**
- **Retail Unit Price**: What customers pay per unit
- **Retail Cost Price**: Your cost for retail operations  
- **Retail Profit Margin**: Percentage profit on retail sales
- **Color Coding**: Green (>20%), Yellow (10-20%), Red (<10%)

### **Visual Indicators:**
- 🟢 **High Margin**: >20% profit (green badge)
- 🟡 **Medium Margin**: 10-20% profit (yellow badge)  
- 🔴 **Low Margin**: <10% profit (red badge)
- 🔄 **Stock Sync**: Automatic inventory updates
- ℹ️ **Pricing Note**: Separate retail management

## 🎮 How to Use

### **View Retail Pricing:**
1. **Go to**: Products → View Product (e.g., OPC)
2. **Look for**: "📦 Linked Stationery Item" section
3. **See**: Retail pricing table with margins
4. **Compare**: Product bulk pricing vs retail pricing

### **Update Retail Pricing:**
1. **Click**: "📦 View Stationery Item" button
2. **Edit**: Stationery Item pricing
3. **Set**: Your retail unit price and cost price
4. **Save**: Retail pricing updates independently

### **Monitor Profit Margins:**
- **Green Badge**: Good retail margins (>20%)
- **Yellow Badge**: Acceptable margins (10-20%)
- **Red Badge**: Low margins (<10%) - consider price adjustment

## 💰 Business Benefits

### **Clear Pricing Separation:**
- **Bulk Costs**: Track what you pay suppliers
- **Retail Pricing**: Set competitive customer prices
- **Margin Analysis**: See profitability clearly
- **Strategic Decisions**: Adjust pricing based on margins

### **Example - OPC Product:**
```
Bulk Operations (Product):
├── Purchase Cost: TZS 15,000 per carton
├── Bulk Price: TZS 20,000 per carton  
├── Total Units: 2,500 pieces
└── Bulk Margin: 25%

Retail Operations (Stationery):
├── Retail Cost: TZS 18,000 per 100 units
├── Retail Price: TZS 25,000 per 100 units
├── Per Unit: TZS 250 each
└── Retail Margin: 38.9%
```

## ✅ Verification

When you view any product with a linked stationery item, you should see:

1. **📦 Linked Stationery Item** section
2. **Two-column layout** with basic info and pricing table
3. **Retail Unit Price** from stationery item
4. **Retail Cost Price** from stationery item  
5. **Retail Profit Margin** with color coding
6. **Stock sync confirmation** and pricing separation note

## 🎯 Perfect For Your Business

This display gives you:
- **Complete visibility** of retail profitability
- **Clear separation** between bulk and retail operations
- **Quick margin analysis** for pricing decisions
- **Easy access** to edit retail pricing
- **Professional presentation** of business data

**Your retail pricing information is now clearly displayed from the stationery item system!** 🎉
