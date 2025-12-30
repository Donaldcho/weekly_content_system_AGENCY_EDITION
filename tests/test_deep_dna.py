
import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.brand_analyzer import BrandAnalyzer
from project_config import Config

def test_deep_dna():
    print("Initializing BrandAnalyzer...")
    try:
        analyzer = BrandAnalyzer()
    except Exception as e:
        print(f"FAILED to init analyzer: {e}")
        return

    sample_text = """
    🚀 Just crushed our Q3 goals! 
    The team is on fire. Big things coming. #TechLife #Growth
    
    Don't settle for average. Push the boundaries.
    """
    
    print("Testing analyze_style with sample text...")
    try:
        res = analyzer.analyze_style(sample_text)
        if "error" in res:
             print(f"FAILED: {res['error']}")
        else:
             print("SUCCESS! Captured DNA:")
             print(json.dumps(res, indent=2))
             
    except Exception as e:
        print(f"CRASHED: {e}")

if __name__ == "__main__":
    test_deep_dna()
