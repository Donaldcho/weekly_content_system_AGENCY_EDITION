from .base_agent import BaseAgent
import json

class ReviewerAgent(BaseAgent):
    def review_draft(self, draft, brand_voice):
        prompt = f"""
        You are the **Editor-in-Chief**.
        
        Brand Voice Settings: {brand_voice}
        
        Draft to Review:
        {draft}
        
        Task: Critique the draft.
        1. Score it (0-10) based on alignment with Brand Voice.
        2. Provide specific feedback if Score < 10.
        
        Output JSON:
        {{
            "score": 8,
            "critique": "Good, but too many emojis."
        }}
        """
        raw = self.generate(prompt, json_mode=True)
        return self._clean_json(raw)

    def _clean_json(self, raw_text):
        try:
           clean = raw_text.replace("```json", "").replace("```", "").strip()
           return json.loads(clean)
        except:
           return {}
