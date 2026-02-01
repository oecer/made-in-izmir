# Product Approval System

## Overview
I've implemented a product approval workflow similar to the signup approval system. Now when producers create products, they go through an admin review process before becoming visible on the platform.

## How It Works

### For Producers
1. **Submit Product**: When a producer fills out the "Add Product" form, it creates a `ProductRequest` instead of a `Product` directly
2. **Pending Status**: The product request is marked as "pending" and waits for admin approval
3. **Notification**: The producer sees a success message: "Ürün talebiniz alındı! Ürününüz yönetici onayından sonra aktif hale gelecektir."
4. **Dashboard**: Pending requests are not shown in the producer dashboard (only approved products appear)

### For Admins
1. **Access Admin Panel**: Go to `/admin` and log in
2. **View Product Requests**: Click on "Ürün Talepleri" (Product Requests) in the admin sidebar
3. **Review Submissions**: 
   - See all pending product requests with:
     - Product title (TR/EN)
     - Producer name and company
     - Status (Pending/Approved/Rejected)
     - Creation date
   - Click on any request to view full details including:
     - All product information
     - Photo previews
     - Tags
     - Producer information

4. **Approve Products**:
   - **Method 1 (Bulk)**: Select multiple pending requests and choose "Approve selected product requests" from the Actions dropdown
   - **Method 2 (Individual)**: Open a product request, change Status to "Approved", and save
   - When approved:
     - A new `Product` is created with all the data from the request
     - Photos are copied over
     - Tags are assigned
     - The product becomes visible to buyers
     - The request status changes to "approved"

5. **Reject Products**:
   - Select pending requests and choose "Reject selected product requests" from Actions
   - Or open a request, change Status to "Rejected", optionally add a rejection reason, and save

## Database Changes

### New Model: `ProductRequest`
Located in `main/models.py`, this model stores:
- Producer information
- Product details (title, description in TR/EN)
- Photos (up to 3)
- Tags (stored as comma-separated IDs)
- Status (pending/approved/rejected)
- Review information (who reviewed, when, rejection reason)

### Modified Views
- `add_product_view`: Now creates `ProductRequest` instead of `Product`
- Success messages updated to inform about approval process

### Admin Interface
- New `ProductRequestAdmin` class with:
  - List view showing pending requests
  - Detailed view with photo previews
  - Bulk approve/reject actions
  - Individual approval workflow

## Files Modified
1. `main/models.py` - Added `ProductRequest` model
2. `main/admin.py` - Added `ProductRequestAdmin` with approval actions
3. `main/views.py` - Updated `add_product_view` to create requests
4. `main/static/js/translations.js` - Added approval message translations
5. Migration created: `0007_remove_product_approval_status_and_more.py`

## Testing the System
1. Log in as a producer
2. Go to "Yeni Ürün Ekle" (Add New Product)
3. Fill out the form and submit
4. You'll see the pending message
5. Log in to `/admin` as an admin
6. Go to "Ürün Talepleri"
7. Select the pending request and approve it
8. The product will now appear in the producer's dashboard and be visible to buyers

## Benefits
- **Quality Control**: Admins can review products before they go live
- **Prevent Spam**: Reduces low-quality or inappropriate product listings
- **Consistency**: Matches the existing signup approval workflow
- **Audit Trail**: Track who approved/rejected products and when
- **Flexibility**: Admins can bulk approve or review individually
