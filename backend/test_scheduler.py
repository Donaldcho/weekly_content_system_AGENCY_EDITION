import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scheduler import SocialScheduler
from project_config import Config

def test_scheduler():
    print("--- Testing SocialScheduler ---")
    scheduler = SocialScheduler()
    
    # Mock data
    plan = [
        {"day": "Monday", "linkedin_draft": "Post 1", "facebook_draft": "FB Post 1", "image_path": "visuals/day_1.png"},
        {"day": "Tuesday", "linkedin_draft": "Post 2", "facebook_draft": "FB Post 2", "image_path": None} # Missing image
    ]
    
    print(f"Launching plan with {len(plan)} days...")
    results = scheduler.schedule_week(plan)
    print("Results:", results)
    
    # Verify History
    print("\nVerifying history.json...")
    if os.path.exists(Config.HISTORY_PATH):
        with open(Config.HISTORY_PATH, 'r') as f:
            history = json.load(f)
            print(f"History count: {len(history)}")
            # Show last entry
            if history:
                print("Last entry:", history[-1])
    else:
        print("ERROR: history.json not found!")

if __name__ == "__main__":
    test_scheduler()
