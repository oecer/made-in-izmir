# Authentication System Documentation

## ✅ **Complete Authentication System Implemented!**

Your Django project now has a fully functional authentication system with user registration, login, logout, and profile management.

---

## 🎯 **Features**

### **1. User Registration (Signup)**
- **Dual Role Support**: Users can register as Buyers, Producers, or both
- **Comprehensive Profile**: Collects personal, company, and role-specific information
- **Conditional Fields**: Form dynamically shows/hides fields based on selected user type
- **Validation**: Server-side and client-side validation ensures data integrity
- **Bilingual**: Full Turkish and English support

### **2. User Login**
- Clean, modern login interface
- Username or email authentication
- Redirect to requested page after login
- Remember user session

### **3. User Profile**
- View all personal and company information
- See user type badges (Buyer/Producer)
- Conditional sections based on user roles
- Logout functionality

### **4. Navigation Integration**
- Dynamic navbar shows Login/Signup for guests
- Shows Profile link for authenticated users
- Seamless user experience

---

## 📋 **User Registration Fields**

### **Common Fields (Required for All Users)**
| Field | Type | Description |
|-------|------|-------------|
| First Name | Text | User's first name |
| Last Name | Text | User's last name |
| Email | Email | User's email address |
| Username | Text | Unique username for login |
| Password | Password | Secure password |
| Company Name | Text | Name of the company |
| Phone Number | Text | Phone with country code |
| Country | Text | Country of operation |
| City | Text | City of operation |
| User Type | Checkbox | Buyer and/or Producer |

### **Buyer-Specific Fields** (Required if "Buyer" is selected)
| Field | Type | Description |
|-------|------|-------------|
| Interested Sectors | Text | Comma-separated sectors (e.g., Textiles, Food) |
| Quarterly Purchase Volume | Number | Expected quarterly purchase volume in USD |

### **Producer-Specific Fields** (Required if "Producer" is selected)
| Field | Type | Description |
|-------|------|-------------|
| Sector | Text | Producer's industry sector |
| Quarterly Sales Volume | Number | Current quarterly sales volume in USD |
| Approximate Product Count | Number | Number of products in catalog |

---

## 🌐 **Available URLs**

| Page | URL | Description |
|------|-----|-------------|
| **Signup** | `/signup/` | User registration page |
| **Login** | `/login/` | User login page |
| **Profile** | `/profile/` | User profile (requires login) |
| **Logout** | `/logout/` | Logout (requires login) |

---

## 💻 **How to Use**

### **Creating a New Account**

1. Navigate to http://127.0.0.1:8000/signup/
2. Fill in personal information (name, email, username, password)
3. Fill in company information
4. Select user type:
   - ✅ Check "Alıcı" (Buyer) if you want to purchase products
   - ✅ Check "Üretici" (Producer) if you manufacture products
   - ✅ You can select both!
5. Fill in the conditional fields that appear based on your selection
6. Click "Kayıt Ol" (Sign Up)
7. You'll be automatically logged in and redirected to the home page

### **Logging In**

1. Navigate to http://127.0.0.1:8000/login/
2. Enter your username (or email) and password
3. Click "Giriş Yap" (Login)
4. You'll be redirected to the home page

### **Viewing Your Profile**

1. After logging in, click "Profilim" (My Profile) in the navigation
2. View all your information organized by sections
3. See your user type badges
4. Click "Çıkış Yap" (Logout) to log out

---

## 🎨 **User Interface Features**

### **Signup Form**
- **Conditional Fields**: Buyer and Producer fields appear/disappear dynamically
- **Smooth Animations**: Fields slide in with smooth transitions
- **Color-Coded Sections**: Different sections have distinct visual styling
- **Real-time Validation**: Instant feedback on form errors
- **Responsive Design**: Works on all screen sizes

### **Profile Page**
- **User Type Badges**: Visual badges showing Buyer/Producer status
- **Organized Sections**: Information grouped logically
- **Modern Card Design**: Clean, professional appearance
- **Conditional Display**: Only shows relevant sections based on user type

---

## 🔐 **Security Features**

1. **Password Hashing**: Passwords are securely hashed using Django's built-in system
2. **CSRF Protection**: All forms protected against Cross-Site Request Forgery
3. **Login Required**: Profile page requires authentication
4. **Session Management**: Secure session handling
5. **Form Validation**: Both client-side and server-side validation

---

## 🌍 **Bilingual Support**

All forms and pages support both Turkish and English:

### **Turkish (Default)**
- Kayıt Ol (Sign Up)
- Giriş Yap (Login)
- Profilim (My Profile)
- Alıcı (Buyer)
- Üretici (Producer)

### **English**
- Sign Up
- Login
- My Profile
- Buyer
- Producer

**Language switching** is automatic based on the language selector in the navigation bar.

---

## 📊 **Database Model**

### **UserProfile Model**

```python
class UserProfile(models.Model):
    user = OneToOneField(User)  # Links to Django User
    
    # Common fields
    company_name = CharField
    phone_number = CharField
    country = CharField
    city = CharField
    
    # User type
    is_buyer = BooleanField
    is_producer = BooleanField
    
    # Buyer fields
    buyer_interested_sectors = TextField
    buyer_quarterly_volume = DecimalField
    
    # Producer fields
    producer_sector = CharField
    producer_quarterly_sales = DecimalField
    producer_product_count = IntegerField
    
    # Timestamps
    created_at = DateTimeField
    updated_at = DateTimeField
```

---

## 🛠️ **Admin Panel**

User profiles can be managed through Django admin:

1. Navigate to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Go to "User Profiles" section
4. View, edit, or delete user profiles
5. Filter by user type, country, or creation date

**Admin Features:**
- List view with key information
- Filters for buyer/producer status
- Search by username, email, company name
- Organized fieldsets for easy editing

---

## ✅ **Testing the System**

### **Test Signup Flow**

1. Go to `/signup/`
2. Fill in all required fields
3. Select "Alıcı" (Buyer)
4. Notice buyer-specific fields appear
5. Fill in buyer information
6. Submit the form
7. Verify you're logged in and redirected

### **Test Login Flow**

1. Go to `/login/`
2. Enter credentials
3. Submit
4. Verify redirect to home page
5. Check navbar shows "Profilim" instead of "Giriş"

### **Test Profile Page**

1. While logged in, click "Profilim"
2. Verify all information is displayed correctly
3. Check user type badges appear
4. Verify conditional sections (buyer/producer) show correctly

---

## 🎯 **Key Implementation Details**

### **Form Validation**
- At least one user type must be selected
- If Buyer is selected, buyer fields are required
- If Producer is selected, producer fields are required
- Email must be unique
- Username must be unique

### **User Creation Process**
1. User fills out signup form
2. Form validates all fields
3. Django User object is created
4. UserProfile object is created and linked
5. User is automatically logged in
6. Redirect to home page with success message

### **Dynamic Field Display**
JavaScript in the signup template:
- Listens for checkbox changes
- Shows/hides conditional fields
- Adds smooth animations
- Maintains form state

---

## 📝 **Next Steps / Enhancements**

Potential future improvements:

1. **Email Verification**: Send confirmation email after signup
2. **Password Reset**: Allow users to reset forgotten passwords
3. **Profile Editing**: Allow users to update their information
4. **Avatar Upload**: Let users upload profile pictures
5. **Social Login**: Add Google/Facebook authentication
6. **Two-Factor Authentication**: Extra security layer
7. **Email Notifications**: Notify users of important events

---

## 🚀 **Your Authentication System is Ready!**

You now have a professional, fully-functional authentication system with:
- ✅ User registration with dual roles
- ✅ Secure login/logout
- ✅ User profiles
- ✅ Bilingual support (Turkish/English)
- ✅ Modern, responsive UI
- ✅ Form validation
- ✅ Admin panel integration

**All forms are working and ready to use!** 🎉
