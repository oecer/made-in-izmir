# Product Sector Feature

## Overview
I've added a sector field to products, allowing producers to categorize their products by industry sector. The system automatically filters available sectors based on the producer's profile sectors.

## Key Features

### 1. **Sector Selection**
- Products now have a required `sector` field
- Producers can only select from sectors they chose in their profile
- Displayed as a dropdown with bilingual labels (Turkish | English)

### 2. **User-Based Filtering**
- When a producer creates/edits a product, they only see their profile sectors
- This ensures products are categorized within the producer's expertise areas
- Prevents irrelevant sector assignments

### 3. **Form Integration**
- **Add Product Form**: Sector field appears at the top, before product information
- **Edit Product Form**: Same placement for consistency
- Help text: "Ürününüzün ait olduğu sektörü seçin" / "Select the sector your product belongs to"

### 4. **Admin Panel**
- **Product Requests**: Sector displayed in admin review interface
- **Products**: Sector shown in list view and detail view
- **Filtering**: Admins can filter products by sector
- **Approval**: Sector is copied from ProductRequest to Product during approval

## Implementation Details

### Database Changes
- Added `sector` ForeignKey to `Product` model
- Added `sector` ForeignKey to `ProductRequest` model
- Migration: `0008_product_sector_productrequest_sector.py`

### Form Updates
- `ProductForm` now includes sector field
- Custom `__init__` method filters sectors based on user's profile
- Bilingual sector labels: `{name_tr} | {name_en}`

### View Updates
- `add_product_view`: Passes `user` to form, saves sector to ProductRequest
- `edit_product_view`: Passes `user` to form for sector filtering

### Template Updates
- `add_product.html`: Added sector section with industry icon
- `edit_product.html`: Added sector section (matching add form)
- Both include help text and error handling

### Admin Updates
- `ProductRequestAdmin`: Sector in fieldsets and readonly fields
- `ProductAdmin`: Sector in list display, filters, and fieldsets
- Approval process copies sector from request to product

### Translations
- `dashboard.sector`: "Sektör" / "Sector"
- `dashboard.sector_help`: Help text in both languages

## User Experience

### For Producers
1. **Profile Setup**: Select sectors during signup (e.g., "Tekstil", "Gıda")
2. **Add Product**: 
   - See only their sectors in dropdown
   - Must select one sector (required field)
   - Cannot select sectors outside their profile
3. **Edit Product**: Same sector filtering applies

### For Admins
1. **Review Requests**: See which sector the product belongs to
2. **Filter Products**: Can filter by sector in admin panel
3. **Approval**: Sector automatically copied to approved product

## Example Workflow

```
Producer Profile Sectors: [Tekstil, Gıda, Mobilya]

When adding a product:
├── Sector dropdown shows:
│   ├── Tekstil | Textiles
│   ├── Gıda | Food
│   └── Mobilya | Furniture
│
└── Cannot see other sectors like:
    ├── Otomotiv | Automotive
    └── Elektronik | Electronics
```

## Benefits
- **Quality Control**: Products are categorized correctly
- **User Experience**: Simplified sector selection
- **Data Integrity**: Prevents mismatched sector assignments
- **Filtering**: Easier product discovery by sector
- **Consistency**: Aligns product sectors with producer expertise

## Files Modified
1. `main/models.py` - Added sector fields to Product and ProductRequest
2. `main/forms.py` - Added sector field with user-based filtering
3. `main/views.py` - Updated views to pass user and handle sector
4. `main/admin.py` - Added sector to admin interfaces
5. `main/templates/user_area/add_product.html` - Added sector section
6. `main/templates/user_area/edit_product.html` - Added sector section
7. `main/static/js/translations.js` - Added sector translations
8. Migration: `0008_product_sector_productrequest_sector.py`
