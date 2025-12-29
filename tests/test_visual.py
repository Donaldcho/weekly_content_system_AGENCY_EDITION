import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adk.main import MarketingAgency
import json

def test_visual_agent():
    print("Initializing Agency...")
    agency = MarketingAgency()
    
    brand = {
        "name": "NeuroFlow",
        "colors": ["#00F0FF", "#121212"],
        "tone": "Futuristic, Analytical"
    }
    
    # Test Cases
    scenarios = [
        ("AI Trends 2025", "The Future is Agentic", "Cyberpunk"),
        ("Mindfulness at Work", "Breathe Deep", "Organic"),
        ("Q3 Revenue Report", "Growth Spurt", "Corporate")
    ]
    
    print("\n--- TESTING VISUAL PROMPTS ---")
    for topic, title, style in scenarios:
        print(f"\n[Scenario] {style} | {title}")
        try:
            res = agency.generate_visual(topic, title, style, brand)
            prompt = res.get('image_prompt', '')
            reason = res.get('reasoning', '')
            
            print(f"Prompt: {prompt[:100]}...")
            print(f"Reason: {reason}")
            
            # Validation Check
            if title in prompt:
                print("Title found in prompt.")
            else:
                print("Warning: Title NOT found in prompt (Agent failed instruction).")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_visual_agent()
