"""
Manual test of the approval logic
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from main.models import SignupRequest, UserProfile

# Get the signup request
sr = SignupRequest.objects.filter(username='test').first()

if not sr:
    print("No signup request found for 'test'")
else:
    print(f"Found request: {sr.username}")
    print(f"Current status: {sr.status}")
    print(f"Email: {sr.email}")
    print(f"Password hash: {sr.password_hash[:50]}...")
    
    # Reset to pending
    sr.status = 'pending'
    sr.reviewed_by = None
    sr.reviewed_at = None
    sr.save()
    print("\nReset to pending")
    
    # Try to create user manually
    print("\n=== ATTEMPTING USER CREATION ===")
    try:
        with transaction.atomic():
            print(f"Creating user: {sr.username}")
            user = User.objects.create(
                username=sr.username,
                email=sr.email,
                first_name=sr.first_name,
                last_name=sr.last_name,
                password=sr.password_hash
            )
            print(f"✓ User created: {user}")
            
            print(f"Creating profile...")
            profile = UserProfile.objects.create(
                user=user,
                company_name=sr.company_name,
                phone_number=sr.phone_number,
                country=sr.country,
                city=sr.city,
                is_buyer=sr.is_buyer,
                is_producer=sr.is_producer,
                buyer_quarterly_volume=sr.buyer_quarterly_volume,
                producer_quarterly_sales=sr.producer_quarterly_sales,
                producer_product_count=sr.producer_product_count
            )
            print(f"✓ Profile created: {profile}")
            
            # Add sectors
            if sr.buyer_interested_sectors_ids:
                print(f"Adding buyer sectors: {sr.buyer_interested_sectors_ids}")
                buyer_sectors = sr.get_buyer_sectors()
                print(f"Found {buyer_sectors.count()} buyer sectors")
                if buyer_sectors.exists():
                    profile.buyer_interested_sectors.set(buyer_sectors)
                    print(f"✓ Buyer sectors added")
            
            if sr.producer_sectors_ids:
                print(f"Adding producer sectors: {sr.producer_sectors_ids}")
                producer_sectors = sr.get_producer_sectors()
                print(f"Found {producer_sectors.count()} producer sectors")
                if producer_sectors.exists():
                    profile.producer_sectors.set(producer_sectors)
                    print(f"✓ Producer sectors added")
            
            # Update status
            sr.status = 'approved'
            sr.reviewed_at = timezone.now()
            sr.save()
            print(f"✓ Status updated to approved")
            
            print("\n✓✓✓ SUCCESS! User created successfully!")
            
    except Exception as e:
        print(f"\n✗✗✗ ERROR: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
    
    # Verify
    print("\n=== VERIFICATION ===")
    user_exists = User.objects.filter(username='test').exists()
    print(f"User 'test' exists: {user_exists}")
    sr.refresh_from_db()
    print(f"Request status: {sr.status}")
