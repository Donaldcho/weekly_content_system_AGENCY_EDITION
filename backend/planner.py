import google.generativeai as genai
import json
import os
from project_config import Config

class ContentPlanner:
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def generate_weekly_plan(self, topic, brand_voice, target_audience):
        """
        Generates a 7-day content plan based on the topic and company context.
        """
        prompt = f"""
        You are a social media expert for a company.
        
        **Brand Voice:** {brand_voice}
        **Target Audience:** {target_audience}
        **Weekly Focus Topic:** {topic}
        
        Generate a 7-day content plan (Monday to Sunday).
        For each day, provide:
        1. A LinkedIn post draft key 'linkedin_draft'.
        2. A Facebook post draft key 'facebook_draft'.
        3. A detailed image generation prompt for the visual key 'image_prompt'.
        
        Output **exclusively** valid JSON in the following format:
        [
            {{
                "day": "Monday",
                "linkedin_draft": "...",
                "facebook_draft": "...",
                "image_prompt": "..."
            }},
            ...
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response if it contains markdown formatting
            text = response.text.replace('```json', '').replace('```', '').strip()
            plan = json.loads(text)
            return plan
        except Exception as e:
            print(f"Error generating plan: {e}")
            return []

if __name__ == "__main__":
    # Test run
    Config.validate()
    planner = ContentPlanner()
    plan = planner.generate_weekly_plan("AI Agents", "Professional, Innovative", "Tech Leaders")
    print(json.dumps(plan, indent=2))
