# Automatic SKU Generation Guide

## 🎯 Overview

The system now automatically generates SKUs for new whole sale products, making product registration faster and more efficient while maintaining the existing relationship with retail sale products.

## 🔄 How It Works

### **Automatic SKU Generation**
When creating a new whole sale product:

1. **Leave SKU field blank** → System generates automatically
2. **Enter custom SKU** → System uses your custom SKU
3. **Edit existing product** → SKU becomes editable (required)

### **SKU Format**
```
CATEGORY-NAME-YEAR-SEQUENTIAL
```
**Example**: `FIL-SPR-26-001`

- **CATEGORY**: First 3 letters of category name
- **NAME**: First 3 letters of product name  
- **YEAR**: Last 2 digits of current year (2026 → 26)
- **SEQUENTIAL**: 3-digit number (001, 002, 003...)

## 📊 Examples

### **Spring Files PVC**
```
Category: Files & Folders → FIL
Name: Spring Files PVC → SPR
Year: 2026 → 26
Sequential: 001
Result: FIL-SPR-26-001
```

### **OPC Document Folders**
```
Category: Files & Folders → FIL
Name: OPC Document Folders → OPC
Year: 2026 → 26
Sequential: 002
Result: FIL-OPC-26-002
```

### **PVC Products**
```
Category: PVC Products → PVC
Name: PVC Binding Covers → PVC
Year: 2026 → 26
Sequential: 003
Result: PVC-PVC-26-003
```

## 🎮 User Interface

### **New Product Form**
```
📝 Add Whole Sale Product
├── Product Name *: [Spring Files PVC]
├── Category *: [Files & Folders]
├── SKU: [FIL-SPR-26-XXX] (readonly, auto-generated)
├── Supplier *: [PVC Products Tanzania]
└── ... other fields
```

### **Real-time Preview**
- **Type product name** → SKU updates instantly
- **Select category** → SKU updates instantly
- **Preview format**: `FIL-SPR-26-XXX` (XXX = placeholder)
- **Final SKU**: Generated on save with actual sequential number

### **Edit Product Form**
```
✏️ Update Whole Sale Product
├── Product Name *: [Spring Files PVC]
├── Category *: [Files & Folders]
├── SKU *: [FIL-SPR-26-001] (editable)
└── ... other fields
```

## ✅ Key Features

### **1. Smart Generation**
- **Category-based**: Uses category abbreviation
- **Name-based**: Uses product name abbreviation
- **Year-based**: Includes current year
- **Sequential**: Daily numbering for uniqueness

### **2. Flexibility**
- **Auto-generate**: Leave blank for automatic SKU
- **Custom SKU**: Enter your own SKU format
- **Editable**: SKUs editable for existing products
- **Unique**: Ensures no duplicate SKUs

### **3. User-Friendly**
- **Real-time preview**: See SKU as you type
- **Clear placeholders**: Shows format before generation
- **Helpful hints**: "Leave blank to auto-generate SKU"
- **Validation**: Prevents duplicate SKUs

## 🔧 Technical Details

### **Generation Logic**
```python
def generate_sku(self):
    category_abbr = re.sub(r'[^A-Za-z0-9]', '', self.category.name)[:3].upper()
    name_abbr = re.sub(r'[^A-Za-z0-9]', '', self.name)[:3].upper()
    year_suffix = str(datetime.datetime.now().year)[-2:]
    sequential = str(Product.objects.filter(created_at__date=today).count() + 1).zfill(3)
    sku = f"{category_abbr}-{name_abbr}-{year_suffix}-{sequential}"
    return sku
```

### **Uniqueness Guarantee**
- Checks existing SKUs
- Adds suffix if conflict (`FIL-SPR-26-001-1`)
- Maintains data integrity

### **Form Behavior**
- **New products**: SKU optional, readonly, auto-generated
- **Existing products**: SKU required, editable
- **Validation**: Prevents duplicate SKUs

## 🎯 Benefits

### **1. Efficiency**
- **Faster registration**: No need to think of SKUs
- **Consistent format**: Standardized SKU structure
- **Time-saving**: Focus on product details, not SKU creation

### **2. Organization**
- **Category grouping**: Easy to identify product type
- **Chronological**: Year and sequence tracking
- **Searchable**: Predictable format for searches

### **3. Relationship Maintenance**
- **Retail sync**: Stationery items created automatically
- **Stock sync**: Inventory quantities synchronized
- **Link preserved**: Whole sale ↔ retail product connection

## 📋 Workflow Examples

### **Adding New Spring Files**
1. **Go to**: Whole Sale Products → Add Whole Sale Product
2. **Enter**: "Spring Files PVC Large" in name field
3. **Select**: "Files & Folders" category
4. **See**: SKU preview `FIL-SPR-26-XXX`
5. **Fill**: Other details (price, cartons, etc.)
6. **Save**: Product created with SKU `FIL-SPR-26-007`
7. **Result**: Retail product automatically linked

### **Adding Custom SKU Product**
1. **Go to**: Whole Sale Products → Add Whole Sale Product
2. **Enter**: Product name and details
3. **Type**: Custom SKU in SKU field (e.g., `SPRING-001`)
4. **Save**: Custom SKU preserved
5. **Result**: Product with your chosen SKU

### **Editing Existing Product**
1. **Go to**: Whole Sale Products → View Product
2. **Click**: Edit Product
3. **Modify**: SKU field (now editable)
4. **Save**: Updated SKU applied
5. **Result**: Product SKU changed, retail link maintained

## ✅ Testing Results

### **Successful Tests:**
- ✅ **Auto-generation**: FIL-TES-26-005
- ✅ **Sequential numbering**: FIL-TES-26-005 → FIL-ANO-26-006
- ✅ **Custom SKU**: CUSTOM-001 preserved
- ✅ **Retail sync**: Stationery item created automatically
- ✅ **Stock sync**: 750 units synchronized correctly

### **Relationship Verification:**
- ✅ **Stationery item created**: Linked automatically
- ✅ **SKU copied**: Same SKU in retail product
- ✅ **Stock synchronized**: Cartons ↔ units conversion
- ✅ **Pricing separate**: Retail pricing independent
- ✅ **Link maintained**: Whole sale ↔ retail connection

## 🚀 Ready for Production

The automatic SKU generation system is fully functional and ready for your whole sale product management:

### **What Works:**
- **Automatic SKU generation** for new products
- **Real-time preview** as you type
- **Custom SKU support** for specific needs
- **Retail product synchronization** maintained
- **Stock synchronization** working perfectly
- **Form validation** preventing duplicates

### **User Benefits:**
- **Faster product registration**
- **Consistent SKU formatting**
- **Better organization**
- **Maintained retail relationships**
- **Professional inventory management**

**Your whole sale product registration is now faster and more efficient with automatic SKU generation!** 🎉
