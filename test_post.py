from backend.linkedin_poster import post_to_linkedin
import os

# 1. Define a dummy image (make sure this file exists!)
img = "assets/test_image.png" 
# Create a dummy image if it doesn't exist for testing
if not os.path.exists("assets"):
    os.makedirs("assets")

# Simple red square png byte signature
if not os.path.exists(img):
    with open(img, "wb") as f:
        # Minimal 1x1 RED PNG
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8e\x00\x00\x00\x00IEND\xaeB`\x82')

# 2. Run
print("[TEST] Attempting to post...")
try:
    success, msg = post_to_linkedin(
        text_content="Hello LinkedIn! This is my first autonomous post from DeviceterraSM. 🤖 #AI #Python",
        image_path=img,
        is_company_post=False # Set to True if you have Organization permissions
    )
    print(f"Result: {success} - {msg}")
except Exception as e:
    print(f"FAILED: {e}")
