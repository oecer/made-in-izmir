"""
Test script to verify signup approval workflow
Run with: python manage.py shell < test_approval.py
"""

from django.contrib.auth.models import User
from main.models import SignupRequest, UserProfile

print("\n" + "="*60)
print("TESTING SIGNUP APPROVAL WORKFLOW")
print("="*60)

# Get the first pending signup request
signup_request = SignupRequest.objects.filter(status='pending').first()

if not signup_request:
    print("\n❌ No pending signup requests found!")
    print("Please submit a signup form first.")
else:
    print(f"\n📋 Found pending request:")
    print(f"   Username: {signup_request.username}")
    print(f"   Email: {signup_request.email}")
    print(f"   Company: {signup_request.company_name}")
    print(f"   Status: {signup_request.status}")
    
    # Check if user already exists
    if User.objects.filter(username=signup_request.username).exists():
        print(f"\n⚠️  WARNING: User '{signup_request.username}' already exists!")
        print("   This request was probably already approved.")
    else:
        print(f"\n✓ Username '{signup_request.username}' is available")
    
    # Check if email already exists
    if User.objects.filter(email=signup_request.email).exists():
        print(f"⚠️  WARNING: Email '{signup_request.email}' already exists!")
    else:
        print(f"✓ Email '{signup_request.email}' is available")
    
    print("\n" + "-"*60)
    print("To approve this request:")
    print("1. Go to http://localhost:8000/admin")
    print("2. Navigate to 'Kayıt Talepleri' (Signup Requests)")
    print("3. Select the pending request")
    print("4. Choose 'Approve selected signup requests' from Actions")
    print("5. Click 'Go'")
    print("-"*60)

# Show all users
print(f"\n👥 Current users in database:")
for user in User.objects.all():
    has_profile = hasattr(user, 'profile')
    print(f"   - {user.username} ({user.email}) - Profile: {has_profile}")

# Show all signup requests
print(f"\n📝 All signup requests:")
for req in SignupRequest.objects.all():
    print(f"   - {req.username} ({req.email}) - Status: {req.status}")

print("\n" + "="*60)
