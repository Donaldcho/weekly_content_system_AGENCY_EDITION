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
        
    # --- STRATEGY TEST ---
    print(f"\nTesting Strategy Creation for: '{topic}'")
    brand = {
        "name": "BeanBloom",
        "mission": "Deliver freshly roasted, ethically sourced coffee to remote workers.",
        "target_audience": "Digital Nomads, 25-35"
    }
    strategy = agency.create_strategy(topic, brand)
    print("\nStrategy Results (Snippet):")
    print(json.dumps(strategy, indent=2)[:500] + "...")
    
    if strategy.get("strategy_analysis"):
        print("\n[PASS] Agency successfully created Personas & SWOT.")
    else:
        print("\n[FAIL] No domains returned.")

if __name__ == "__main__":
    test_marketing_agency()
