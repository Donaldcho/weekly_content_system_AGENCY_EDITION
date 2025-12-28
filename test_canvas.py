from backend.canvas_engine import CanvasEngine
import os

# Create dummy assets
if not os.path.exists("test_bg.png"):
    from PIL import Image
    Image.new('RGB', (100, 100), color = 'red').save("test_bg.png")

engine = CanvasEngine()
engine.set_background_image("test_bg.png")

# Add Text
engine.add_text_layer("Hello World", x=10, y=10, font_size=20, color="#FFFFFF")

# Render
try:
    path = engine.save("test_output.png")
    print(f"Saved to {path}")
    if os.path.exists(path):
        print("Verification Successful")
    else:
        print("Verification Failed: File not created")
except Exception as e:
    print(f"Verification Failed: {e}")

# Cleanup
if os.path.exists("test_bg.png"): os.remove("test_bg.png")
# if os.path.exists("test_output.png"): os.remove("test_output.png")
