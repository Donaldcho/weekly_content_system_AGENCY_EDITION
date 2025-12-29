from .base import BaseAdkAgent
import json

class StrategistAgent(BaseAdkAgent):
    def plan_marketing_campaign(self, topic, brand_info, context=""):
        """
        Generates a comprehensive marketing strategy including Personas, SWOT, and Content Plan.
        """
        # 1. PERSONA & SWOT ANALYSIS
        analysis_prompt = f"""
        You are the **Lead Marketing Strategist** for {brand_info.get('name', 'Client')}.
        
        Mission: {brand_info.get('mission', 'Growth')}
        Target Audience Description: {brand_info.get('target_audience', 'General Public')}
        Topic: {topic}
        Context: {context}
        
        TASK: Perform a foundational analysis.
        1. Define 2 Detailed User Personas (Name, Age, Pain Points, Values).
        2. Conduct a mini-SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) relative to this topic.
        
        Return JSON Key: "analysis_data" (Object containing personas and swot)
        """
        analysis_raw = self.generate(analysis_prompt, json_mode=True)
        try:
            analysis_data = json.loads(analysis_raw).get("analysis_data", {})
        except:
            analysis_data = {}

        # 2. WEEKLY CONTENT PLAN (Using the Analysis)
        plan_prompt = f"""
        Based on this Strategic Analysis:
        {json.dumps(analysis_data, indent=2)}
        
        Create a 7-Day Content Plan for '{topic}'.
        Each day must target one of the Personas defined above.
        
        Output JSON List of objects:
        [
            {{
                "day": "Monday",
                "focus": "Product Spotlight",
                "angle": "...",
                "target_persona": "Persona Name",
                "platform_intent": "IG: Visuals, LinkedIn: Professional"
            }},
            ...
        ]
        """
        plan_raw = self.generate(plan_prompt, json_mode=True)
        try:
            week_plan = json.loads(plan_raw)
            if isinstance(week_plan, dict): week_plan = week_plan.get("plan", []) # Handle wrapped responses
        except:
            week_plan = []

        return {
            "strategy_analysis": analysis_data,
            "week_plan": week_plan
        }
