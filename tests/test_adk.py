import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adk.main import MarketingAgency
import json

def test_marketing_agency():
    print("Initializing Marketing Agency...")
    agency = MarketingAgency()
    
    topic = "organic coffee subscription"
    print(f"Testing Domain Search for: '{topic}'")
    
    # Run Agent
    results = agency.run_domain_search(topic)
    
    print("\nResults:")
    print(json.dumps(results, indent=2))
    
    if len(results) > 0:
        print("\n[PASS] Agency successfully ideated domains.")
    else:
        print("\n[FAIL] No domains returned.")

if __name__ == "__main__":
    test_marketing_agency()
