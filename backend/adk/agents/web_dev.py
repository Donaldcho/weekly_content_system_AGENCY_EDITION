from .base import BaseAdkAgent
import json

class WebDevAgent(BaseAdkAgent):
    def build_landing_page(self, strategy, brand_info, topic):
        """
        Generates a high-converting landing page based on strategy and brand.
        Returns Dict with 'index.html' and 'style.css'.
        """
        # Extract Strategy Context
        personas = strategy.get('strategy_analysis', {}).get('personas', [])
        target_persona = personas[0] if personas else {"name": "General Audience", "pain_points": ["Generic needs"]}
        
        # Brand Context
        brand_name = brand_info.get('name', 'Brand')
        colors = brand_info.get('colors', ['#000000', '#FFFFFF'])
        tone = brand_info.get('tone', 'Professional')
        
        prompt = f"""
        You are a **Senior Frontend Developer** & **Conversion Rate Optimization (CRO) Expert**.
        
        ### PROJECT BRIEF
        **Client**: {brand_name} (Tone: {tone})
        **Topic**: {topic}
        **Target Audience**: {target_persona.get('name')} (Needs: {", ".join(target_persona.get('pain_points', []))})
        
        ### TASK
        Build a SINGLE-PAGE Landing Page for this campaign.
        
        ### TECHNICAL SPECS
        1. **Framework**: Use Tailwind CSS (via CDN) for modern, responsive aesthetics.
        2. **Layout**:
           - **Hero Section**: Strong Headline (addressing pain point), Subheadline, CTA Button.
           - **Benefit Section**: 3 Cards explaining value.
           - **Social Proof**: Mock testimonial from the target persona type.
           - **CTA / Footer**: Final conversion push.
        3. **Copywriting**: Write actual persuasive copy based on the Persona's needs. Do NOT use "Lorem Ipsum".
        
        ### OUTPUT FORMAT
        Return a JSON object with strictly these keys:
        - "html": The full `<!DOCTYPE html>...` string (include Tailwind CDN script).
        - "css": Any custom CSS needed (e.g., specific brand color overrides not handled by Tailwind).
        
        JSON Structure:
        {{
            "html": "...",
            "css": "..."
        }}
        """
        
        raw = self.generate(prompt, json_mode=True)
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            return data
        except Exception as e:
            print(f"[WebDevAgent] Error parsing output: {e}")
            return {"html": "<!-- Prediction Failed -->", "css": ""}
