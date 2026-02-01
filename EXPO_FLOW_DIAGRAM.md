# Expo Calendar User Flow

## Admin Flow
```
Admin Panel
    ↓
Add Expo (Fuarlar)
    ↓
Fill in details:
- Title (TR/EN)
- Description (TR/EN)
- Location (TR/EN)
- Start Date
- End Date
- Registration Deadline
- Image (optional)
- Set Active
    ↓
Save
    ↓
Expo appears on:
- /calendar/ (public)
- /dashboard/calendar/ (users)
```

## User Flow - Viewing Expos

### Public View
```
/calendar/
    ↓
View all active expos
- Upcoming expos
- Past expos
    ↓
If authenticated:
    → Link to /dashboard/calendar/
```

### Dashboard View
```
/dashboard/calendar/
    ↓
See three sections:
1. My Registrations (if any)
   - Expo name
   - Dates
   - Status (pending/confirmed/cancelled)

2. Upcoming Expos (cards)
   - Expo image
   - Title & description
   - Dates & location
   - Registration deadline
   - Signup button (if not registered)

3. Past Expos (table)
   - Historical reference
```

## User Flow - Signing Up for Expo

```
/dashboard/calendar/
    ↓
Click "Kayıt Ol / Bizi Kiralayın" on an expo
    ↓
/expo/<id>/signup/
    ↓
Fill form:
1. Product Count (required)
   └─ How many products to send

2. Product Selection Method:
   
   Option A: Check "Made in İzmir'de listelenen ürünlerimden seçmek istiyorum"
   └─ Dropdown appears
   └─ Select products from your listed products
   
   Option B: Leave unchecked
   └─ Text area appears
   └─ Describe products in free text

3. Notes (optional)
   └─ Additional information
    ↓
Submit
    ↓
Validation:
- Check if already signed up → Error
- Check if deadline passed → Error
- Check product selection → Error if invalid
    ↓
Success!
    ↓
Redirect to /dashboard/calendar/
    ↓
See registration in "Kayıt Olduğunuz Fuarlar" section
```

## Data Flow

```
User submits signup form
    ↓
ExpoSignup object created:
- expo: Foreign key to Expo
- user: Foreign key to User
- product_count: Integer
- uses_listed_products: Boolean
- IF uses_listed_products = True:
    └─ selected_products: Many-to-Many with Product
- IF uses_listed_products = False:
    └─ product_description: Text
- notes: Text
- status: 'pending' (default)
    ↓
Admin can view in:
Django Admin → Fuar Kayıtları (ExpoSignup)
    ↓
Admin can change status:
- pending → confirmed
- pending → cancelled
    ↓
User sees updated status in dashboard
```

## Database Relationships

```
User ──┬─── ExpoSignup ─── Expo
       │         │
       │         └─── Product (Many-to-Many, optional)
       │
       └─── Product (as producer)
```

## URL Structure

```
Public:
/calendar/                          → View all expos (public)

Authenticated:
/dashboard/calendar/                → Dashboard calendar with signup
/expo/<expo_id>/signup/            → Signup form for specific expo

Admin:
/admin/main/expo/                   → Manage expos
/admin/main/exposignup/             → Manage signups
```

## Form Validation Logic

```python
if uses_listed_products == True:
    if selected_products.count() == 0:
        → Error: "Lütfen en az bir ürün seçin."
else:
    if product_description is empty:
        → Error: "Lütfen ürün açıklaması girin."

if product_count < 1:
    → Error: Invalid value

if user already signed up for this expo:
    → Error: "Bu fuara zaten kayıt oldunuz."

if registration_deadline has passed:
    → Error: "Bu fuar için kayıt süresi dolmuştur."
```

## Status Flow

```
ExpoSignup created
    ↓
status = 'pending'
    ↓
Admin reviews in admin panel
    ↓
Admin can set:
- 'confirmed' → User sees green badge
- 'cancelled' → User sees red badge
```
