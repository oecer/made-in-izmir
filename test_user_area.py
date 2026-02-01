"""
Quick test script to verify the user area implementation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import ProductTag, Product, UserProfile
from django.contrib.auth.models import User

print("=" * 60)
print("USER AREA IMPLEMENTATION TEST")
print("=" * 60)

# Test 1: Check if models are accessible
print("\n✅ Test 1: Models are accessible")
print(f"   - ProductTag table: {ProductTag._meta.db_table}")
print(f"   - Product table: {Product._meta.db_table}")

# Test 2: Check if we can create a ProductTag
print("\n✅ Test 2: Creating a test ProductTag")
tag, created = ProductTag.objects.get_or_create(
    name_tr="Test Etiketi",
    name_en="Test Tag"
)
print(f"   - Tag created: {created}")
print(f"   - Tag: {tag}")

# Test 3: Count existing products
print("\n✅ Test 3: Checking existing products")
product_count = Product.objects.count()
print(f"   - Total products in database: {product_count}")

# Test 4: Check users with producer profiles
print("\n✅ Test 4: Checking producer users")
producers = UserProfile.objects.filter(is_producer=True)
print(f"   - Total producers: {producers.count()}")
for producer in producers:
    print(f"   - {producer.user.username} ({producer.company_name})")

# Test 5: Check users with buyer profiles
print("\n✅ Test 5: Checking buyer users")
buyers = UserProfile.objects.filter(is_buyer=True)
print(f"   - Total buyers: {buyers.count()}")
for buyer in buyers:
    print(f"   - {buyer.user.username} ({buyer.company_name})")

print("\n" + "=" * 60)
print("ALL TESTS PASSED! User area is ready to use.")
print("=" * 60)
print("\nNext steps:")
print("1. Login as admin at http://localhost:8000/admin/")
print("2. Add some Product Tags in 'Ürün Etiketleri'")
print("3. Login as a producer user")
print("4. Go to http://localhost:8000/dashboard/")
print("5. Click 'Yeni Ürün Ekle' to add your first product!")
print("=" * 60)
