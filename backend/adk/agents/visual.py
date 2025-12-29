from .base import BaseAdkAgent
import json

class VisualDesignAgent(BaseAdkAgent):
    """
    Agent responsible for generating high-fidelity image prompts 
    that incorporate specific text and style.
    """
    
    STYLE_PRESETS = {
        "Minimalist": "Ultra-clean infographic or conceptual illustration, flat vector design, ample negative space, plain off-white or soft gradient background. Monochrome or restricted palette (slate blue, soft teal, light grey). Modern, tech-focused, geometric but simple.",
        "Cyberpunk": "Neon lights, dark background, glitch effect, futuristic grid, vibrant cyan and magenta.",
        "Editorial": "High-fashion magazine style, bold serif typography overlay, muted elegant color palette, grain texture.",
        "Organic": "Earth tones, natural textures (paper, leaf), soft shadows, hand-drawn elements.",
        "Corporate": "Professional blue/grey palette, geometric shapes, clean glassmorphism, trustworthy vibe."
    }

    def generate_social_visual(self, topic, title, style_preset, brand_info):
        """
        Generates a detailed image prompt for a text-overlay social post.
        """
        # 1. Custom Brand Style (Priority)
        custom_styles = brand_info.get('visual_styles', {})
        if style_preset in custom_styles:
            val = custom_styles[style_preset]
            if isinstance(val, dict):
                style_desc = val.get("prompt", "")
            else:
                style_desc = str(val)
        else:
            # 2. Built-in Preset (Fallback)
            style_desc = self.STYLE_PRESETS.get(style_preset, self.STYLE_PRESETS['Minimalist'])
            
        brand_colors = ", ".join(brand_info.get('colors', []))
        brand_name = brand_info.get('name', 'Brand')
        
        # --- PROMPT REGISTRY INTEGRATION ---
        try:
            from backend.prompt_registry import PromptRegistry
            registry = PromptRegistry()
            
            prompt = registry.get(
                "visual_agent_system",
                topic=topic,
                title=title,
                style_preset=style_preset,
                style_desc=style_desc,
                brand_colors=brand_colors,
                brand_name=brand_name # Added this key to JSON logic
            )
        except Exception as e:
            print(f"Prompt Registry Error: {e}, falling back to hardcoded.")
            # Fallback (Mini version) if JSON fails
            prompt = f"Create a DALL-E prompt for {topic} with title '{title}' in style {style_preset}."
            
        # raw = self.generate(prompt, json_mode=True) # Old line follows below

        
        raw = self.generate(prompt, json_mode=True)
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            
            # Safety: If model returned a list, take first item
            if isinstance(data, list):
                if data:
                    data = data[0]
                else:
                    data = {}
            
            # Safety: Ensure dict
            if not isinstance(data, dict):
                data = {}
                
            return data
        except Exception as e:
            print(f"[VisualAgent] Error parsing: {e}")
            return {
                "image_prompt": f"A professional {style_preset} social media graphic with the text '{title}' in the center. {style_desc}",
                "reasoning": "Fallback generation due to parse error."
            }
