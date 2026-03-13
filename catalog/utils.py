"""
Utility functions for the catalog app
"""
import uuid
import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class product_photo_upload_to:
    """
    Serializable callable for ImageField upload_to.

    Generates a standardized, human-readable filename:
        products/tenant-{id}_photo{n}_{short_uuid}.jpg
    Example:
        products/tenant-42_photo1_a3f9b2c1.jpg

    Implemented as a class (not a closure) so Django's migration framework
    can serialize and deconstruct it correctly.
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower() or '.jpg'
        short_id = uuid.uuid4().hex[:8]

        tenant_id = None
        if hasattr(instance, 'tenant') and instance.tenant_id:
            tenant_id = instance.tenant_id
        elif hasattr(instance, 'producer') and instance.producer_id:
            tenant_id = f'user{instance.producer_id}'

        prefix = f'{tenant_id}' if tenant_id else 'unknown'
        return f'products/{prefix}_product_{short_id}{ext}'

    def deconstruct(self):
        """Required for Django migration serialization."""
        return (
            'catalog.utils.product_photo_upload_to',
            [self.field_name],
            {},
        )

    def __eq__(self, other):
        return isinstance(other, product_photo_upload_to) and self.field_name == other.field_name

    def __hash__(self):
        return hash(self.field_name)


def compress_image(image_file, max_size=(1920, 1920), quality=85):
    """
    Compress and optimize an uploaded image file.

    Args:
        image_file: Django UploadedFile object
        max_size: Tuple of (width, height) for maximum dimensions
        quality: JPEG quality (1-100, default 85)

    Returns:
        InMemoryUploadedFile: Compressed image file
    """
    if not image_file:
        return None

    try:
        # Open the image
        img = Image.open(image_file)

        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if image is larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to BytesIO object
        output = BytesIO()

        # Save as JPEG with optimization
        img.save(
            output,
            format='JPEG',
            quality=quality,
            optimize=True,
            progressive=True
        )

        output.seek(0)

        # Get the original filename and change extension to .jpg
        original_name = image_file.name
        name_parts = original_name.rsplit('.', 1)
        new_name = f"{name_parts[0]}.jpg"

        # Create a new InMemoryUploadedFile
        compressed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )

        return compressed_file

    except Exception as e:
        # If compression fails, return the original file
        print(f"Image compression failed: {e}")
        return image_file
