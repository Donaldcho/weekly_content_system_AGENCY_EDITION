from .base import BaseAdkAgent
import json
import re

class LogoDesignAgent(BaseAdkAgent):
    def design_brand_logo(self, brand_info):
        """
        Generates an SVG logo based on brand identity.
        Returns Dict with 'svg' and 'reasoning'.
        """
        brand_name = brand_info.get('name', 'Brand')
        tone = brand_info.get('tone', 'Modern')
        colors = brand_info.get('colors', ['#000000'])
        industry = brand_info.get('industry', 'Technology')
        mission = brand_info.get('mission', '')

        prompt = f"""
        You are a **Senior Brand Designer** specializing in Vector Graphics (SVG).
        
        ### PROJECT
        **Brand**: {brand_name}
        **Industry**: {industry}
        **Tone**: {tone}
        **Mission**: {mission}
        **Primary Colors**: {", ".join(colors)}
        
        ### TASK
        Create a **Minimalist, Professional Logo** in SVG format.
        
        ### DESIGN RULES
        1. **Iconography**: Create a geometric abstract mark or stylized initial that represents the brand's mission (e.g., 'Velocity' -> arrow/bolt).
        2. **Layout**: Icon on the left, Brand Name (Text) on the right.
        3. **Scalability**: Use standard SVG elements (rect, circle, path, text).
        4. **Colors**: Use the specific brand colors provided.
        5. **Canvas**: viewBox="0 0 300 100".
        
        ### OUTPUT FORMAT
        Return a JSON object with:
        - "reasoning": Brief explanation of the design choice (1 sentence).
        - "svg": The complete, valid `<svg ...> ... </svg>` code string.
        
        JSON Structure:
        {{
            "reasoning": "...",
            "svg": "..."
        }}
        """
        
        raw = self.generate(prompt, json_mode=True)
        try:
            # Clean potential markdown wrapping
            clean = raw.replace("```json", "").replace("```", "").strip()
            # Some models might wrap the SVG in xml tags in the JSON string, which is fine as long as valid JSON string
            data = json.loads(clean)
            
            # Extra safety: Ensure SVG tag exists
            if "<svg" not in data.get("svg", ""):
                 # Fallback if model failed to produce SVG code
                 data["svg"] = f'<svg viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg"><text x="50" y="50" font-family="Arial" font-size="24">{brand_name}</text></svg>'
            
            return data
        except Exception as e:
            print(f"[LogoAgent] Error: {e}")
            return {
                "reasoning": "Generation failed.", 
                "svg": f'<svg viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg"><text x="20" y="60" font-family="Arial" font-size="40">{brand_name}</text></svg>'
            }
