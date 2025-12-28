import random
import pandas as pd
from datetime import datetime, timedelta

class CRMAgent:
    """
    The CRM Agent closes the loop between Content and Revenue.
    In the Enterprise Demo, it simulates Lead Scoring and Attribution.
    """
    
    def __init__(self):
        # Simulation Data Seeds
        self.users = [
            "Sarah_Marketing_VP", "TechBuyer2025", "StartupFounder_X", 
            "Enterprise_采购", "AgencyOwner_Mike", "GrowthHacker_99"
        ]
    
    def get_pipeline_data(self):
        """
        Returns simulated leads categorized by 'Temperature' (Lead Score).
        """
        leads = []
        
        # COLDS (Score 0-30) - Just engaging casually
        for _ in range(3):
            leads.append({
                "name": f"User_{random.randint(100,999)}",
                "role": "Unknown",
                "score": random.randint(5, 25),
                "status": "Cold",
                "last_action": "Liked '5 AI Tips'",
                "avatar": "❄️"
            })
            
        # WARMS (Score 31-70) - Asking questions, frequent likes
        leads.append({
            "name": "StartupFounder_X",
            "role": "CEO",
            "score": 55,
            "status": "Warm",
            "last_action": "Commented: 'Pricing?'",
            "avatar": "🔥"
        })
        leads.append({
             "name": "AgencyOwner_Mike",
             "role": "Founder",
             "score": 62,
             "status": "Warm",
             "last_action": "Shared post to Story",
             "avatar": "🔥"
        })

        # HOTS (Score 71+) - High intent signals
        leads.append({
            "name": "Sarah_Marketing_VP",
            "role": "VP Marketing",
            "score": 92,
            "status": "Hot",
            "last_action": "DM: 'Demo Request'",
            "value": "$15,000",
            "avatar": "💰"
        })
        
        return leads

    def get_roi_data(self):
        """
        Generates a DataFrame simulating Content Spend vs Revenue over time.
        """
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
        data = []
        
        cumulative_spend = 0
        cumulative_revenue = 0
        
        for d in dates:
            # Simulate daily ad spend / production cost
            daily_spend = random.randint(50, 200)
            cumulative_spend += daily_spend
            
            # Simulate revenue spikes attributed to content
            # Occasional big deals
            daily_rev = random.randint(0, 100)
            if random.random() < 0.1: # 10% chance of a deal
                daily_rev += random.randint(1000, 5000)
                
            cumulative_revenue += daily_rev
            
            data.append({
                "Date": d,
                "Content Cost ($)": cumulative_spend,
                "Attributed Revenue ($)": cumulative_revenue
            })
            
        return pd.DataFrame(data)

    def calculate_score(self, interactions):
        """
        Utility to calculate score based on real inputs (if we had them).
        """
        score = 0
        weights = {
            "like": 1,
            "comment": 5,
            "share": 10,
            "save": 10,
            "dm": 25
        }
        for action, count in interactions.items():
            score += weights.get(action, 0) * count
        return score
