import json
from .base_agent import BaseAgent

class ArtDirectorAgent(BaseAgent):
    def design_visuals(self, day, topic, post_content):
        prompt = f"""
        You are the **Art Director**.
        
        Context:
        - Topic: {topic}
        - Day/Focus: {day}
        - Post Content: {post_content[:500]}... (snippet)
        
        Task: Write a detailed Image Generation Prompt for this post.
        The image generator processes "Glassmorphism, Neon, Tech, Abstract" styles well.
        
        Output JSON:
        {{
            "image_prompt": "A futuristic 3D render of..."
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
