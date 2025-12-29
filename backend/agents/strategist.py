from .base_agent import BaseAgent
import json

class StrategistAgent(BaseAgent):
    def plan_week(self, topic, company_info, context="", campaign_type="Weekly Routine"):
        prompt = f"""
        You are the **Lead Strategist** for {company_info.get('name', 'Client')}.
        
        Mission: {company_info.get('mission', 'Grow brand')}
        Target Audience: {company_info.get('target_audience', 'General')}
        
        Goal: Create a high-level 7-day content strategy for the topic: '{topic}'.
        Campaign Type: {campaign_type}
        
        Context/Trends: 
        {context}
        
        Output a JSON List of objects (one for each day Mon-Sun).
        CRITICAL: You MUST include all 7 days (Monday through Sunday). Do not skip any days.
        Format:
        [
            {{
                "day": "Monday",
                "focus": "Motivation / Insight",
                "angle": "Brief description of the angle/hook for this day",
                "platform_intent": "LinkedIn: Thought Leadership, FB: Community"
            }},
            ...
        ]
        """
        raw = self.generate(prompt, json_mode=True)
        return self._clean_json(raw)
        
    def _clean_json(self, raw_text):
        try:
           clean = raw_text.replace("```json", "").replace("```", "").strip()
           return json.loads(clean)
        except:
           return []
