import json
from .base_agent import BaseAgent

class CreatorAgent(BaseAgent):
    def draft_content(self, day_plan, brand_settings):
        """
        Updated to use Deep Brand DNA.
        brand_settings: The full dict from DB (not just a tone string).
        """
        # Extract the deep DNA
        mission = brand_settings.get('mission', '')
        tone_guide = brand_settings.get('tone', 'Professional')
        
        # safely get nested keys if they exist (from our new analyzer)
        voice_profile = brand_settings.get('voice_profile', {})
        anti_patterns = brand_settings.get('anti_patterns', [])
        golden_sample = brand_settings.get('golden_samples', [])
        
        # Construct the "Style Mimicry" block
        style_instruction = f"""
        ### 🧬 BRAND DNA (STRICT ADHERENCE)
        - **Mission**: {mission}
        - **Tone**: {tone_guide}
        - **Sentence Structure**: {voice_profile.get('sentence_structure', 'Standard')}
        - **Vocabulary**: {voice_profile.get('vocabulary_level', 'Standard')}
        - **Formatting**: {voice_profile.get('formatting_quirks', 'Standard')}
        
        ### 🚫 ANTI-PATTERNS (DO NOT DO THIS)
        {", ".join(anti_patterns) if anti_patterns else "None defined."}
        
        ### 🏆 GOLDEN REFERENCE (MIMIC THIS STYLE)
        "{golden_sample[0] if golden_sample else 'N/A'}"
        """

        prompt = f"""
        You are the **Creative Copywriter**.
        
        {style_instruction}
        
        ---
        **CURRENT ASSIGNMENT**
        Day: {day_plan.get('day')}
        Focus: {day_plan.get('focus')}
        Angle: {day_plan.get('angle')}
        
        Task: Write TWO distinct drafts.
        
        1. LinkedIn Post:
           - Use the formatting quirks defined above.
           - Ensure the voice matches the Golden Reference.
        
        2. Facebook Post:
           - More casual, but keep the core brand voice.
        
        Output JSON:
        {{
            "linkedin_draft": "...",
            "facebook_draft": "..."
        }}
        """
        # Using a smarter model for writing if possible
        # self.model = genai.GenerativeModel('gemini-3-pro-preview') 
        
        raw = self.generate(prompt, json_mode=True)
        return self._clean_json(raw)

    def _clean_json(self, raw_text):
        try:
           clean = raw_text.replace("```json", "").replace("```", "").strip()
           return json.loads(clean)
        except:
           return {}
