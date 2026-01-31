# Signup Approval System

## Overview

The Made in İzmir platform now uses a **signup approval workflow** where new user registrations must be approved by a superuser before accounts are created. This ensures quality control and prevents spam registrations.

## How It Works

### For Users

1. **Submit Signup Request**: Users fill out the signup form with all required information
2. **Confirmation Message**: After submission, users see a message: *"Kayıt talebiniz alındı! Hesabınız yönetici onayından sonra aktif hale gelecektir."*
3. **Wait for Approval**: The user's request is stored in the database with a "pending" status
4. **Account Creation**: Once approved by an admin, the user account is automatically created
5. **Login**: Users can then login with their chosen username and password

### For Administrators

1. **Access Admin Panel**: Login to `/admin` with superuser credentials
2. **View Signup Requests**: Navigate to "Kayıt Talepleri" (Signup Requests)
3. **Review Details**: Click on any pending request to see all submitted information:
   - Personal information (name, email, username)
   - Company details
   - User type (Buyer/Producer)
   - Sector selections
   - Business volume/sales data
4. **Approve or Reject**:
   - **Approve**: Select request(s) and choose "Approve selected signup requests" from the Actions dropdown
   - **Reject**: Select request(s) and choose "Reject selected signup requests"
5. **Automatic Account Creation**: When approved, the system automatically:
   - Creates the User account
   - Creates the UserProfile with all submitted data
   - Links all selected sectors
   - Marks the request as "approved"

## Technical Implementation

### Models

#### SignupRequest Model
Located in `main/models.py`, this model stores all signup form data temporarily:

- **User Information**: username, email, first_name, last_name, password_hash
- **Company Information**: company_name, phone_number, country, city
- **User Type**: is_buyer, is_producer
- **Buyer Data**: buyer_interested_sectors_ids, buyer_quarterly_volume
- **Producer Data**: producer_sectors_ids, producer_quarterly_sales, producer_product_count
- **Status Tracking**: status (pending/approved/rejected), reviewed_by, reviewed_at, rejection_reason

### Forms

#### SignUpForm (main/forms.py)
Modified to create a `SignupRequest` instead of directly creating a `User`:

```python
def save(self, commit=True):
    # Creates SignupRequest with status='pending'
    # Password is hashed using make_password()
    # Sector IDs are stored as comma-separated strings
```

### Views

#### signup_view (main/views.py)
Updated to handle the new workflow:

```python
def signup_view(request):
    # Creates SignupRequest instead of User
    # Shows success message about pending approval
    # Does NOT log the user in
```

### Admin Interface

#### SignupRequestAdmin (main/admin.py)
Comprehensive admin interface with:

- **List View**: Shows all requests with status, user type, and company info
- **Detail View**: Displays all submitted information in organized fieldsets
- **Bulk Actions**:
  - `approve_signups`: Creates User and UserProfile for selected requests
  - `reject_signups`: Marks selected requests as rejected
- **Filters**: Status, user type, country, creation date
- **Search**: Username, email, company name, phone number

## Database Schema

### SignupRequest Table
```sql
- id (Primary Key)
- username (Unique)
- email
- first_name, last_name
- password_hash (Already hashed)
- company_name, phone_number, country, city
- is_buyer, is_producer
- buyer_interested_sectors_ids (Text: comma-separated IDs)
- buyer_quarterly_volume
- producer_sectors_ids (Text: comma-separated IDs)
- producer_quarterly_sales, producer_product_count
- status (pending/approved/rejected)
- reviewed_by (Foreign Key to User)
- reviewed_at
- rejection_reason
- created_at, updated_at
```

## Workflow Diagram

```
User Submits Form
       ↓
SignupRequest Created (status='pending')
       ↓
Admin Reviews in Admin Panel
       ↓
    Approve?
    /      \
  Yes       No
   ↓         ↓
Create User  Mark as Rejected
Create UserProfile
Link Sectors
Mark as Approved
   ↓
User Can Login
```

## Security Considerations

1. **Password Security**: Passwords are hashed using Django's `make_password()` before storage
2. **No Auto-Login**: Users cannot login until their account is approved
3. **Admin Only**: Only superusers can access the admin panel to approve requests
4. **Audit Trail**: All approvals/rejections are tracked with reviewer and timestamp

## Future Enhancements

Potential improvements to consider:

1. **Email Notifications**: Send emails to users when their request is approved/rejected
2. **Rejection Reasons**: Require admins to provide a reason when rejecting
3. **Auto-Expiry**: Automatically reject requests older than X days
4. **Bulk Import**: Allow admins to approve multiple requests at once
5. **User Dashboard**: Show pending request status to users who try to login

## Admin Quick Guide

### Approving a Single Request
1. Go to Admin Panel → Kayıt Talepleri
2. Click on the pending request
3. Review all information
4. Change Status to "Approved" and save
   OR
5. Use the "Approve selected signup requests" action

### Bulk Approval
1. Go to Admin Panel → Kayıt Talepleri
2. Filter by Status: Pending
3. Select multiple requests using checkboxes
4. Choose "Approve selected signup requests" from Actions dropdown
5. Click "Go"

### Rejecting Requests
1. Select the request(s)
2. Choose "Reject selected signup requests" from Actions dropdown
3. Optionally add a rejection reason in the detail view
4. Click "Go"

## Testing the System

1. **Test Signup**: Fill out the signup form as a new user
2. **Verify Request**: Check admin panel for the new pending request
3. **Test Approval**: Approve the request and verify User/UserProfile creation
4. **Test Login**: Login with the approved credentials
5. **Test Rejection**: Submit another request and reject it
6. **Verify No Login**: Ensure rejected users cannot login

## Troubleshooting

### Issue: Approved user cannot login
- Check that User was created in auth_user table
- Verify password_hash was correctly transferred
- Ensure UserProfile was created and linked

### Issue: Sectors not showing in profile
- Check that sector IDs were correctly stored as comma-separated values
- Verify sectors exist in the Sector table
- Ensure ManyToMany relationships were set during approval

### Issue: Admin action doesn't work
- Check for error messages in admin panel
- Verify superuser permissions
- Check server logs for exceptions
