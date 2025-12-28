from .base_agent import BaseAgent
import json
from datetime import datetime, timedelta

class SchedulerAgent(BaseAgent):
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        super().__init__(model_name)
        self.role = "Chrono Strategist"
        self.goal = "Intelligently schedule social media content for maximum engagement and brand consistency."

    def suggest_slot(self, draft_content, occupied_slots, brand_voice="Professional"):
        """
        Suggests an optimal date and time for a post based on its content and existing calendar.
        
        occupied_slots: List of ISO strings already taken.
        """
        now = datetime.now()
        calendar_context = "\n".join([f"- {slot}" for slot in occupied_slots]) if occupied_slots else "Calendar is currently empty."
        
        prompt = f"""
        System: You are the {self.role}. {self.goal}
        
        Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
        Draft Content:
        \"\"\"{draft_content}\"\"\"
        
        Brand Voice: {brand_voice}
        
        Existing Calendar Occupancy (Already Scheduled):
        {calendar_context}
        
        Task:
        1. Analyze the draft content to determine its 'vibe' (e.g., Monday Motivation, Weekend Tips, midweek deep-dive).
        2. Find the earliest available date (starting from tomorrow) that is NOT in the occupied list.
        3. Suggest an optimal hour (e.g., 9:00 AM for business, 6:00 PM for community).
        4. Return a JSON object.
        
        Required Output Format:
        {{
            "suggested_timestamp": "YYYY-MM-DDTHH:MM:SS",
            "thought_process": "Describe your analysis of the content, audience behavior, and calendar constraints.",
            "reasoning": "A one-sentence executive summary of why this time was chosen."
        }}
        """
        
        response_text = self.generate(prompt, json_mode=True)
        try:
            # Clean possible markdown noise
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            # Fallback to a safe slot if AI fails
            tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%dT09:00:00')
            return {
                "suggested_timestamp": tomorrow,
                "thought_process": f"Analysis failed due to error: {str(e)}. Falling back to default business hours.",
                "reasoning": "Fallback to next business morning due to analysis error."
            }
