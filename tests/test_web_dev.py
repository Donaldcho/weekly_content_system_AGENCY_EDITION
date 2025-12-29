import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adk.main import MarketingAgency
import json

def test_web_dev_agent():
    print("Initializing Agency...")
    agency = MarketingAgency()
    
    topic = "High-Performance Gaming Router"
    brand = {
        "name": "VelocityNet",
        "colors": ["#0F172A", "#6366F1"], # Dark Blue & Indigo
        "tone": "Bold, Energetic, Tech-Native",
        "mission": "Kill Lag. Win More."
    }
    
    # Mock Strategy (usually comes from Strategist)
    strategy = {
        "strategy_analysis": {
            "personas": [{
                "name": "Hardcore Gamer",
                "pain_points": ["High Ping", "Lag Spikes", "Packet Loss"]
            }]
        }
    }
    
    print(f"Designing Landing Page for '{topic}'...")
    result = agency.build_website(strategy, brand, topic)
    
    # Save output
    output_dir = "build_test"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    html = result.get('html', '')
    css = result.get('css', '')
    
    if html:
        with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved HTML to {output_dir}/index.html")
    else:
        print("Failed to generate HTML.")
        
    if css:
        with open(f"{output_dir}/style.css", "w", encoding="utf-8") as f:
            f.write(css)
        print(f"Saved CSS to {output_dir}/style.css")

if __name__ == "__main__":
    test_web_dev_agent()
