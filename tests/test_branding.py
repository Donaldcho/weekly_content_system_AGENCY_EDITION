from backend.post_processing import ImageBrander
from PIL import Image, ImageDraw
import os

# Setup dummy files
test_img_path = "test_gen_image.png"
test_logo_path = "test_logo_brand.png"

# Create dummy image (1024x1024 blue)
img = Image.new('RGB', (1024, 1024), color = (0, 0, 255))
img.save(test_img_path)

# Create dummy logo (100x100 red circle)
logo = Image.new('RGBA', (200, 200), color = (0, 0, 0, 0))
d = ImageDraw.Draw(logo)
d.ellipse([0,0,200,200], fill=(255, 0, 0, 255))
logo.save(test_logo_path)

# Run Brander
try:
    print("Running ImageBrander...")
    brander = ImageBrander(logo_path=test_logo_path)
    final_path = brander.apply_branding(test_img_path)
    print(f"Success! Output at: {final_path}")
    
    # Verify result exists
    if os.path.exists(final_path):
        print("Verified file exists.")
    else:
        print("File missing after branding.")
        
except Exception as e:
    print(f"FAILED: {e}")

# Cleanup
# os.remove(test_img_path)
# os.remove(test_logo_path)
