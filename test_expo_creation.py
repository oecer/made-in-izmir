"""
Quick test script to create a sample expo
Run this with: python manage.py shell < test_expo_creation.py
"""

from main.models import Expo
from datetime import date, timedelta

# Create a sample expo
expo = Expo.objects.create(
    title_tr="İzmir Uluslararası Fuar 2026",
    title_en="Izmir International Fair 2026",
    description_tr="İzmir'in en büyük uluslararası ticaret fuarı. Dünya çapında alıcılar ve üreticiler bir araya geliyor.",
    description_en="Izmir's largest international trade fair. Buyers and producers from around the world come together.",
    location_tr="İzmir Fuar Merkezi, Türkiye",
    location_en="Izmir Fair Center, Turkey",
    start_date=date.today() + timedelta(days=60),
    end_date=date.today() + timedelta(days=65),
    registration_deadline=date.today() + timedelta(days=30),
    is_active=True
)

print(f"✓ Created expo: {expo.title_tr}")
print(f"  - Start Date: {expo.start_date}")
print(f"  - End Date: {expo.end_date}")
print(f"  - Registration Deadline: {expo.registration_deadline}")
print(f"  - Registration Open: {expo.is_registration_open()}")
