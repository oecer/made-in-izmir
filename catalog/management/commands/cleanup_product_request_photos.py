"""
Management command to clean up legacy product_requests/ photo files.

This resolves the duplication that existed before the photo storage refactoring:
  - Approved requests: the file now lives in products/ (owned by Product).
    The product_requests/ copy is a stale duplicate — delete it.
  - Pending requests: files were uploaded to product_requests/ under the old logic.
    Move them to products/ and update DB paths.
  - Rejected requests: files are orphaned — delete them.

Usage:
    python manage.py cleanup_product_request_photos --dry-run   # preview only
    python manage.py cleanup_product_request_photos             # apply changes
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from catalog.models import ProductRequest, Product


class Command(BaseCommand):
    help = "Clean up legacy product_requests/ photo files after storage refactoring"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would happen without making any changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = settings.MEDIA_ROOT

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be made.\n"))

        stats = {
            'deleted': 0,
            'moved': 0,
            'skipped': 0,
            'errors': 0,
        }

        # ----------------------------------------------------------------
        # 1. Approved requests — delete the old product_requests/ copies
        #    (the canonical copy is in products/, owned by the Product record)
        # ----------------------------------------------------------------
        self.stdout.write("Scanning approved ProductRequests...")
        for pr in ProductRequest.objects.filter(status='approved'):
            for field_name in ('photo1', 'photo2', 'photo3'):
                field = getattr(pr, field_name)
                if field and field.name and field.name.startswith('product_requests/'):
                    abs_path = os.path.join(media_root, field.name)
                    if os.path.exists(abs_path):
                        self.stdout.write(f"  [DELETE stale copy] {field.name}")
                        if not dry_run:
                            try:
                                os.remove(abs_path)
                                # Clear the DB field too
                                setattr(pr, field_name, None)
                                stats['deleted'] += 1
                            except Exception as e:
                                self.stderr.write(f"  ERROR deleting {abs_path}: {e}")
                                stats['errors'] += 1
                    else:
                        self.stdout.write(f"  [SKIP — already gone] {field.name}")
                        stats['skipped'] += 1

            if not dry_run:
                pr.save()

        # ----------------------------------------------------------------
        # 2. Pending requests — move files from product_requests/ to products/
        # ----------------------------------------------------------------
        self.stdout.write("\nScanning pending ProductRequests...")
        products_dir = os.path.join(media_root, 'products')
        os.makedirs(products_dir, exist_ok=True)

        for pr in ProductRequest.objects.filter(status='pending'):
            changed = False
            for field_name in ('photo1', 'photo2', 'photo3'):
                field = getattr(pr, field_name)
                if field and field.name and field.name.startswith('product_requests/'):
                    old_abs = os.path.join(media_root, field.name)
                    filename = os.path.basename(field.name)
                    new_rel = f'products/{filename}'
                    new_abs = os.path.join(media_root, new_rel)

                    # Avoid overwriting if a file with same name already exists
                    if os.path.exists(new_abs):
                        base, ext = os.path.splitext(filename)
                        new_rel = f'products/{base}_migrated{ext}'
                        new_abs = os.path.join(media_root, new_rel)

                    self.stdout.write(f"  [MOVE] {field.name}  →  {new_rel}")
                    if not dry_run:
                        try:
                            shutil.move(old_abs, new_abs)
                            setattr(pr, field_name, new_rel)
                            changed = True
                            stats['moved'] += 1
                        except Exception as e:
                            self.stderr.write(f"  ERROR moving {old_abs}: {e}")
                            stats['errors'] += 1

            if changed and not dry_run:
                pr.save()

        # ----------------------------------------------------------------
        # 3. Rejected requests — delete orphaned files
        # ----------------------------------------------------------------
        self.stdout.write("\nScanning rejected ProductRequests...")
        for pr in ProductRequest.objects.filter(status='rejected'):
            changed = False
            for field_name in ('photo1', 'photo2', 'photo3'):
                field = getattr(pr, field_name)
                if field and field.name:
                    abs_path = os.path.join(media_root, field.name)
                    if os.path.exists(abs_path):
                        self.stdout.write(f"  [DELETE orphan] {field.name}")
                        if not dry_run:
                            try:
                                os.remove(abs_path)
                                setattr(pr, field_name, None)
                                changed = True
                                stats['deleted'] += 1
                            except Exception as e:
                                self.stderr.write(f"  ERROR deleting {abs_path}: {e}")
                                stats['errors'] += 1

            if changed and not dry_run:
                pr.save()

        # ----------------------------------------------------------------
        # Summary
        # ----------------------------------------------------------------
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("Cleanup complete!"))
        self.stdout.write(f"  Files deleted : {stats['deleted']}")
        self.stdout.write(f"  Files moved   : {stats['moved']}")
        self.stdout.write(f"  Skipped       : {stats['skipped']}")
        self.stdout.write(f"  Errors        : {stats['errors']}")
        if dry_run:
            self.stdout.write(self.style.WARNING("\n(Dry run — no changes were applied)"))
