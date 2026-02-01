# Expo Calendar Feature

## Overview
The Expo Calendar feature allows administrators to add trade fairs/expos to the system, and users can view and sign up for these expos.

## Features

### 1. Admin Panel
- **Expo Management**: Admins can add, edit, and delete expos through the Django admin panel
- **Expo Signup Management**: Admins can view and manage user signups for expos

### 2. Public Calendar (`/calendar`)
- Displays all active expos to everyone (authenticated or not)
- Shows upcoming and past expos separately
- Authenticated users see a link to the dashboard calendar for signup

### 3. Dashboard Calendar (`/dashboard/calendar`)
- **For authenticated users only**
- Shows all active expos with signup functionality
- Displays user's current expo registrations with status
- Users can sign up for expos by clicking "Kayıt Ol / Bizi Kiralayın" button

### 4. Expo Signup Form
When users click the signup button, they fill out a form with:
- **Product Count**: How many products they want to send
- **Product Selection**: Two options:
  - **Option 1**: Check "Made in İzmir'de listelenen ürünlerimden seçmek istiyorum"
    - A dropdown appears showing their products listed in Made in Izmir
    - They can select multiple products
  - **Option 2**: Leave the checkbox unchecked
    - A free text area appears where they can describe their products
- **Notes**: Optional additional notes

## Models

### Expo
- `title_tr`, `title_en`: Expo title in Turkish and English
- `description_tr`, `description_en`: Expo description
- `location_tr`, `location_en`: Location
- `start_date`, `end_date`: Expo dates
- `registration_deadline`: Last date to register
- `image`: Expo image (optional)
- `is_active`: Whether the expo is active

### ExpoSignup
- `expo`: Foreign key to Expo
- `user`: Foreign key to User
- `product_count`: Number of products
- `uses_listed_products`: Boolean - whether user selected from listed products
- `selected_products`: Many-to-many relationship with Product (if uses_listed_products is True)
- `product_description`: Free text description (if uses_listed_products is False)
- `notes`: Additional notes
- `status`: pending/confirmed/cancelled

## URLs
- `/calendar/` - Public calendar view
- `/dashboard/calendar/` - Dashboard calendar view (authenticated users)
- `/expo/<expo_id>/signup/` - Expo signup form

## Usage

### For Admins
1. Go to Django admin panel
2. Navigate to "Fuarlar" (Expos)
3. Click "Add Expo" to create a new expo
4. Fill in all required fields (Turkish and English titles, descriptions, locations, dates)
5. Upload an image (optional)
6. Set the expo as active
7. Save

### For Users
1. Navigate to `/dashboard/calendar/`
2. Browse available expos
3. Click "Kayıt Ol / Bizi Kiralayın" on an expo
4. Fill out the signup form:
   - Enter the number of products
   - Choose whether to select from listed products or provide a description
   - Add any additional notes
5. Submit the form
6. View your registrations in the "Kayıt Olduğunuz Fuarlar" section

## Validation
- Users cannot sign up for the same expo twice
- Registration must be before the deadline
- If using listed products, at least one product must be selected
- If not using listed products, a description must be provided
- Product count must be at least 1
