import google.generativeai as genai
import json
import random
from datetime import datetime, timedelta
from project_config import Config
from backend.database import Database

class SentinelAgent:
    """
    The 'Sentinel' is an advanced Social Listening Agent.
    In the Enterprise Demo, it simulates high-frequency data streams 
    to demonstrate capabilities without requiring expensive live APIs.
    """
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.db = Database()

    # --- 1. COMPETITOR INTEL (SIMULATED) ---
    def monitor_competitors(self, competitors_list=None):
        """
        Simulates scanning competitor feeds for viral hits or new launches.
        """
        if not competitors_list or len(competitors_list) == 0:
            competitors_list = ["CompetitorX", "RivalCorp", "BigTech Inc"]
            
        alerts = []
        
        # 30% chance of a "High Alert" event per check
        if random.random() < 0.3:
            target = random.choice(competitors_list)
            events = [
                "launched a new AI feature",
                "is going viral for a controversial post",
                "just dropped their prices by 20%",
                "announced a partnership with OpenAI",
                "is running a massive ad campaign on LinkedIn"
            ]
            event = random.choice(events)
            
            alerts.append({
                "source": target,
                "event": event,
                "urgency": "HIGH",
                "timestamp": datetime.now().strftime("%H:%M"),
                "impact_score": random.randint(70, 95)
            })
            
        # Fill with some low-level noise
        for comp in competitors_list[:2]:
            alerts.append({
                "source": comp,
                "event": "posted generic content",
                "urgency": "LOW",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 120))).strftime("%H:%M"),
                "impact_score": random.randint(10, 40)
            })
            
        return sorted(alerts, key=lambda x: x['impact_score'], reverse=True)

    # --- 2. SENTIMENT ANALYSIS (LLM POWERED) ---
    def analyze_brand_mentions(self, brand_name="Deviceterra"):
        """
        Generates simulated user mentions and uses Gemini to classify sentiment.
        """
        # 1. Generate Fake Mentions
        mentions = self._generate_simulated_mentions(brand_name)
        
        # 2. Analyze with LLM (Batch)
        prompt = f"""
        Analyze these social media comments about {brand_name}.
        Classify each into: POSITIVE, NEUTRAL, or NEGATIVE.
        Also extract the main "Theme" (e.g. Pricing, UI, Bugs, Support).

        COMMENTS:
        {json.dumps(mentions)}

        Return JSON:
        [
            {{ "id": 1, "sentiment": "POSITIVE", "theme": "UI" }},
            ...
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # --- COST LOGGING ---
            try:
                usage = response.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name="SentinelAgent",
                        model="gemini-2.0-flash-exp",
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except Exception as e:
                print(f"Failed to log usage: {e}")

            analysis = self._clean_json(response.text)
            
            # Merge Analysis with Original Data
            results = []
            for i, m in enumerate(mentions):
                meta = next((a for a in analysis if a.get('id') == m['id']), {})
                m['sentiment'] = meta.get('sentiment', 'NEUTRAL')
                m['theme'] = meta.get('theme', 'General')
                results.append(m)
                
            return results
            
        except Exception as e:
            print(f"Sentinel AI Error: {e}")
            return mentions # Return raw if AI fails

    def _generate_simulated_mentions(self, brand_name):
        return [
            {"id": 1, "user": "@tech_guru_99", "text": f"Just tried {brand_name} and the AI is surprisingly good. Way better than the others.", "platform": "Twitter"},
            {"id": 2, "user": "SarahBiz", "text": f"Is anyone else having login issues with {brand_name} today? It's been down for an hour.", "platform": "LinkedIn"},
            {"id": 3, "user": "Mark_SaaS", "text": f"{brand_name} is too expensive for what it offers. Cancelling my sub.", "platform": "Reddit"},
            {"id": 4, "user": "Creativ_Studio", "text": f"The new visual editor in {brand_name} is a game changer for my agency!", "platform": "Instagram"},
            {"id": 5, "user": "AnonUser", "text": f"Meh, {brand_name} is okay but I prefer the old version.", "platform": "Twitter"}
        ]

    # --- 3. TREND RADAR ---
    def fetch_trends(self, industry="AI Marketing"):
        """
        Returns simulated trending topics to 'Trendjack'.
        """
        # In a real app, this would hit Google Trends or Twitter API
        return [
            {"topic": "Agents are the new Apps", "volume": "2.4M", "growth": "+450%", "relevance": "High"},
            {"topic": "AI Copyright Lawsuits", "volume": "850K", "growth": "+120%", "relevance": "Medium"},
            {"topic": "Video Gen Models", "volume": "5.1M", "growth": "+800%", "relevance": "High"},
            {"topic": "LinkedIn Algorithm Update", "volume": "300K", "growth": "+40%", "relevance": "High"}
        ]

    def _clean_json(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        try:
            return json.loads(text)
        except:
             return []
