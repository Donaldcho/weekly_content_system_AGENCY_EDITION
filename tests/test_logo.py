import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adk.main import MarketingAgency
import json

def test_logo_agent():
    print("Initializing Agency...")
    agency = MarketingAgency()
    
    brand = {
        "name": "VelocityNet",
        "industry": "Gaming Hardware",
        "colors": ["#000000", "#6366F1"], # Black, Indigo
        "tone": "Futuristic, Bold, Minimalist",
        "mission": "Fastest Routers on Earth."
    }
    
    print(f"Designing Logo for '{brand['name']}'...")
    result = agency.design_logo(brand)
    
    reasoning = result.get('reasoning', 'No reasoning provided.')
    svg_code = result.get('svg', '')
    
    print(f"Reasoning: {reasoning}")
    
    # Save output
    output_dir = "build_test"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    if svg_code and "<svg" in svg_code:
        with open(f"{output_dir}/logo.svg", "w", encoding="utf-8") as f:
            f.write(svg_code)
        print(f"Saved SVG to {output_dir}/logo.svg")
        # Also save a small HTML wrapper to view it easily if svg viewer is not available
        with open(f"{output_dir}/logo_preview.html", "w", encoding="utf-8") as f:
            f.write(f"<html><body style='background:#eee; display:flex; justify-content:center; align-items:center; height:100vh;'>{svg_code}</body></html>")
    else:
        print("Failed to generate valid SVG.")
        print(f"Raw Output: {svg_code[:100]}...")

if __name__ == "__main__":
    test_logo_agent()
