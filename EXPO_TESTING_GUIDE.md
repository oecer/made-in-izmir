# Quick Start Guide - Testing Expo Calendar

## Step 1: Create a Superuser (if not already done)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your choice)
```

## Step 2: Access Admin Panel
1. Navigate to: `http://localhost:8000/admin/`
2. Login with superuser credentials

## Step 3: Create a Test Expo
1. In admin panel, click on **"Fuarlar" (Expos)**
2. Click **"Add Expo"** button
3. Fill in the form:

### Turkish Information:
- **Fuar Başlığı (TR)**: İzmir Uluslararası Gıda Fuarı 2026
- **Fuar Açıklaması (TR)**: İzmir'in en büyük gıda ve içecek fuarı. Dünya çapında alıcılar ve üreticiler buluşuyor.
- **Konum (TR)**: İzmir Fuar Merkezi, Türkiye

### English Information:
- **Fuar Başlığı (EN)**: Izmir International Food Fair 2026
- **Fuar Açıklaması (EN)**: Izmir's largest food and beverage fair. Buyers and producers from around the world meet.
- **Konum (EN)**: Izmir Fair Center, Turkey

### Dates:
- **Başlangıç Tarihi**: Choose a date 60 days from today
- **Bitiş Tarihi**: Choose a date 65 days from today
- **Kayıt Son Tarihi**: Choose a date 30 days from today

### Image (Optional):
- Upload any relevant image

### Status:
- ✅ Check **"Aktif"** (Active)

4. Click **"Save"**

## Step 4: View Public Calendar
1. Navigate to: `http://localhost:8000/calendar/`
2. You should see your expo listed under "Yaklaşan Fuarlar" (Upcoming Expos)

## Step 5: Login as a User
1. If you don't have a regular user account:
   - Go to `http://localhost:8000/signup/`
   - Fill out the signup form
   - Go to admin panel and approve the signup request
2. Login at `http://localhost:8000/login/`

## Step 6: Access Dashboard Calendar
1. After login, go to your dashboard:
   - For producers: `http://localhost:8000/dashboard/producer/`
   - For buyers: `http://localhost:8000/dashboard/buyer/`
2. Click the **"Fuar Takvimi"** button
3. Or directly navigate to: `http://localhost:8000/dashboard/calendar/`

## Step 7: Sign Up for the Expo
1. On the dashboard calendar page, find your expo
2. Click **"Kayıt Ol / Bizi Kiralayın"** button
3. Fill out the signup form:

### Option A: Using Listed Products (for producers with products)
- **Ürün Sayısı**: Enter a number (e.g., 5)
- ✅ Check **"Made in İzmir'de listelenen ürünlerimden seçmek istiyorum"**
- Select products from the dropdown (hold Ctrl to select multiple)
- Add any notes (optional)

### Option B: Using Free Text Description
- **Ürün Sayısı**: Enter a number (e.g., 3)
- ⬜ Leave checkbox unchecked
- **Ürün Açıklaması**: Describe your products (e.g., "Zeytinyağı, zeytin, peynir")
- Add any notes (optional)

4. Click **"Kayıt Ol"** (Sign Up)

## Step 8: Verify Registration
1. You should be redirected back to `/dashboard/calendar/`
2. You should see a success message
3. Your registration should appear in the **"Kayıt Olduğunuz Fuarlar"** section
4. The expo card should now show **"Kayıt Oldunuz"** button (disabled)

## Step 9: View Registration in Admin Panel
1. Go back to admin panel
2. Click on **"Fuar Kayıtları" (ExpoSignup)**
3. You should see your registration with:
   - User name
   - Company name
   - Expo name
   - Product count
   - Status: Beklemede (Pending)

## Step 10: Update Registration Status (Admin)
1. Click on the registration to edit
2. Change **"Durum"** (Status) from "Beklemede" to "Onaylandı"
3. Save
4. Go back to user dashboard calendar
5. Refresh the page
6. The status badge should now show green "Onaylandı" (Confirmed)

## Testing Edge Cases

### Test 1: Duplicate Signup Prevention
1. Try to sign up for the same expo again
2. You should see: "Bu fuara zaten kayıt oldunuz."

### Test 2: Expired Registration
1. Create another expo with registration deadline in the past
2. Try to sign up
3. You should see: "Bu fuar için kayıt süresi dolmuştur."

### Test 3: Form Validation
1. Try to submit form with:
   - Checkbox checked but no products selected → Error
   - Checkbox unchecked but no description → Error
   - Product count = 0 → Error

## Quick Test Script

You can also use the test script to create a sample expo:

```bash
python manage.py shell < test_expo_creation.py
```

This will create a sample expo with proper dates automatically.

## Troubleshooting

### Issue: "No such table: main_expo"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Issue: "Expo doesn't appear on calendar"
**Solution**: Check that:
- Expo is marked as "Aktif" (Active)
- Dates are set correctly
- You're viewing the right page

### Issue: "Can't see signup button"
**Solution**: Make sure you're logged in and viewing `/dashboard/calendar/` not `/calendar/`

### Issue: "No products in dropdown"
**Solution**: 
- Make sure you're logged in as a producer
- Add products first through `/products/add/`
- Products must be approved by admin

## Expected Results

✅ Public calendar shows all active expos
✅ Dashboard calendar shows signup functionality
✅ Users can sign up with either listed products or free text
✅ Duplicate signups are prevented
✅ Expired registrations are blocked
✅ Admin can view and manage all signups
✅ Status updates reflect in user dashboard

## Next Steps

After testing, you can:
1. Create real expos with actual dates
2. Upload professional expo images
3. Customize the templates to match your branding
4. Add email notifications (future enhancement)
5. Export signup data for event planning
