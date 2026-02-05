"""
Test script to verify image compression functionality
"""
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from main.utils import compress_image

def create_test_image(width=3000, height=2000, format='PNG'):
    """Create a test image"""
    img = Image.new('RGB', (width, height), color='red')
    output = BytesIO()
    img.save(output, format=format)
    output.seek(0)
    
    # Create an InMemoryUploadedFile
    test_file = InMemoryUploadedFile(
        output,
        'ImageField',
        f'test_image.{format.lower()}',
        f'image/{format.lower()}',
        sys.getsizeof(output),
        None
    )
    return test_file, output.getbuffer().nbytes

def test_compression():
    """Test the image compression function"""
    print("=" * 60)
    print("Testing Image Compression Functionality")
    print("=" * 60)
    
    # Test 1: Large PNG image
    print("\nTest 1: Large PNG image (3000x2000)")
    print("-" * 60)
    test_file, original_size = create_test_image(3000, 2000, 'PNG')
    print(f"Original size: {original_size:,} bytes")
    
    compressed = compress_image(test_file, max_size=(1920, 1920), quality=85)
    
    if compressed:
        # Get compressed size
        compressed.seek(0)
        compressed_data = compressed.read()
        compressed_size = len(compressed_data)
        
        # Open compressed image to check dimensions
        compressed.seek(0)
        img = Image.open(compressed)
        width, height = img.size
        
        print(f"Compressed size: {compressed_size:,} bytes")
        print(f"Compression ratio: {(1 - compressed_size/original_size) * 100:.1f}%")
        print(f"New dimensions: {width}x{height}")
        print(f"Format: {img.format}")
        print("✓ Test 1 PASSED")
    else:
        print("✗ Test 1 FAILED - No compressed image returned")
    
    # Test 2: Small JPEG image
    print("\nTest 2: Small JPEG image (800x600)")
    print("-" * 60)
    test_file2, original_size2 = create_test_image(800, 600, 'JPEG')
    print(f"Original size: {original_size2:,} bytes")
    
    compressed2 = compress_image(test_file2, max_size=(1920, 1920), quality=85)
    
    if compressed2:
        compressed2.seek(0)
        compressed_data2 = compressed2.read()
        compressed_size2 = len(compressed_data2)
        
        compressed2.seek(0)
        img2 = Image.open(compressed2)
        width2, height2 = img2.size
        
        print(f"Compressed size: {compressed_size2:,} bytes")
        print(f"Compression ratio: {(1 - compressed_size2/original_size2) * 100:.1f}%")
        print(f"New dimensions: {width2}x{height2}")
        print(f"Format: {img2.format}")
        print("✓ Test 2 PASSED")
    else:
        print("✗ Test 2 FAILED - No compressed image returned")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_compression()
