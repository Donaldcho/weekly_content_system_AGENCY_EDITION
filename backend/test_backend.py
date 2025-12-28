import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.content_generator import ContentGenerator
from backend.nano_banana import NanoBanana

def test_backend():
    print("--- Testing ContentGenerator ---")
    cg = ContentGenerator()
    
    print("Generating single post...")
    post = cg.generate_post("LinkedIn", "The Future of Coding Agents", "Rise of AI tooling")
    print(f"Result:\n{post}\n")
    
    print("Generating weekly plan...")
    plan = cg.generate_weekly_plan("Python Automation", "Libraries to watch in 2025")
    for day in plan:
        print(f"Day: {day['day']}, LinkedIn: {len(day['linkedin_draft'])} chars")
    
    print("\n--- Testing NanoBanana ---")
    nb = NanoBanana()
    img_path = nb.generate_image("A futuristic workspace with code holograms in cyberpunk style")
    print(f"Image Path: {img_path}")

if __name__ == "__main__":
    test_backend()
