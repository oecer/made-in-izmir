#!/usr/bin/env python
"""
Script to add sectors to the Made in Izmir database.
Run this script on the server to populate the Sector table with initial data.

Usage:
    python add_sectors.py
"""

import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Sector

# Define sectors with Turkish and English names
SECTORS = [
    {
        'name_tr': 'Tekstil',
        'name_en': 'Textiles'
    },
    {
        'name_tr': 'Gıda',
        'name_en': 'Food'
    },
    {
        'name_tr': 'Mermer & Doğaltaş',
        'name_en': 'Marble & Natural Stone'
    },
    {
        'name_tr': 'Otomotiv Yedek Parça',
        'name_en': 'Automotive Parts'
    },
    {
        'name_tr': 'Mobilya',
        'name_en': 'Furniture'
    },
    {
        'name_tr': 'Kimya',
        'name_en': 'Chemicals'
    },
    {
        'name_tr': 'Makine',
        'name_en': 'Machinery'
    },
    {
        'name_tr': 'Elektrik & Elektronik',
        'name_en': 'Electrical & Electronics'
    },
    {
        'name_tr': 'Plastik & Kauçuk',
        'name_en': 'Plastics & Rubber'
    },
    {
        'name_tr': 'Metal İşleme',
        'name_en': 'Metal Processing'
    },
    {
        'name_tr': 'Ambalaj',
        'name_en': 'Packaging'
    },
    {
        'name_tr': 'Kozmetik',
        'name_en': 'Cosmetics'
    },
    {
        'name_tr': 'Temizlik Ürünleri',
        'name_en': 'Cleaning Products'
    },
    {
        'name_tr': 'İnşaat Malzemeleri',
        'name_en': 'Construction Materials'
    },
    {
        'name_tr': 'Cam & Seramik',
        'name_en': 'Glass & Ceramics'
    },
    {
        'name_tr': 'Kağıt & Karton',
        'name_en': 'Paper & Cardboard'
    },
    {
        'name_tr': 'Deri & Ayakkabı',
        'name_en': 'Leather & Footwear'
    },
    {
        'name_tr': 'Ev Tekstili',
        'name_en': 'Home Textiles'
    },
    {
        'name_tr': 'Medikal Ürünler',
        'name_en': 'Medical Products'
    },
    {
        'name_tr': 'Tarım Ürünleri',
        'name_en': 'Agricultural Products'
    },
]


def add_sectors():
    """Add sectors to the database."""
    print("Starting sector addition process...")
    print(f"Total sectors to add: {len(SECTORS)}")
    print("-" * 50)
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for sector_data in SECTORS:
        name_tr = sector_data['name_tr']
        name_en = sector_data['name_en']
        
        # Check if sector already exists (by Turkish name)
        existing_sector = Sector.objects.filter(name_tr=name_tr).first()
        
        if existing_sector:
            # Update if English name is different
            if existing_sector.name_en != name_en:
                existing_sector.name_en = name_en
                existing_sector.save()
                print(f"✓ Updated: {name_tr} / {name_en}")
                updated_count += 1
            else:
                print(f"○ Skipped (already exists): {name_tr} / {name_en}")
                skipped_count += 1
        else:
            # Create new sector
            Sector.objects.create(
                name_tr=name_tr,
                name_en=name_en
            )
            print(f"✓ Added: {name_tr} / {name_en}")
            added_count += 1
    
    print("-" * 50)
    print(f"\nSummary:")
    print(f"  Added: {added_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(SECTORS)}")
    print("\n✓ Sector addition process completed successfully!")
    
    # Display all sectors
    print("\n" + "=" * 50)
    print("All sectors in database:")
    print("=" * 50)
    all_sectors = Sector.objects.all().order_by('name_tr')
    for idx, sector in enumerate(all_sectors, 1):
        print(f"{idx:2d}. {sector.name_tr:30s} | {sector.name_en}")
    print("=" * 50)


if __name__ == '__main__':
    try:
        add_sectors()
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
