"""
Utility functions for the main app
"""
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


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
