import google.generativeai as genai
import json
import os
import uuid
from project_config import Config
from backend.nano_banana import NanoBanana
from backend.database import Database

class VideoDirector:
    """
    The Video Director Agent handles the Pre-Production pipeline for short-form video:
    1. Scripting (Hook -> Value -> CTA)
    2. Storyboarding (Visualizing scenes with AI images)
    """
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.artist = NanoBanana()
        self.db = Database()

    def generate_script(self, topic, platform="TikTok", target_duration="30s"):
        """
        Generates a viral-style script structure using Gemini.
        """
        prompt = f"""
        Act as a professional Viral Video Director.
        Write a script for a {target_duration} {platform} video about: "{topic}".
        
        The script MUST follow this structure:
        1. HOOK (0-3s): Grab attention immediately.
        2. PROBLEM/VALUE (3-20s): Deliver the core insight or entertainment.
        3. CTA (20-30s): Call to action.

        Return strictly valid JSON:
        {{
            "title": "Video Title",
            "estimated_duration": "30s",
            "hook_text": "Text on screen for hook",
            "scenes": [
                {{
                    "id": 1,
                    "section": "Hook",
                    "visual_description": "Detailed visual description for an AI image generator. Cyberpunk style.",
                    "audio_voiceover": "Spoken words",
                    "screen_text": "Overlay text"
                }},
                ... (3-5 scenes total)
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # --- COST INTELLIGENCE ---
            try:
                usage = response.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name="VideoDirector",
                        model="gemini-2.0-flash-exp",
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except Exception as log_err:
                print(f"Warning: Could not log usage: {log_err}")
                
            data = self._clean_json(response.text)
            if isinstance(data, list):
                return {"title": f"{topic} Video", "scenes": data}
            return data
        except Exception as e:
            print(f"Script Gen Error: {e}")
            return None

    def generate_storyboard(self, script_data):
        """
        Takes the script JSON and generates AI images for each scene using NanoBanana.
        """
        scenes = script_data.get('scenes', [])
        
        print(f"Director: Visualizing {len(scenes)} scenes...")
        
        for scene in scenes:
            desc = scene.get('visual_description', '')
            if desc:
                # Add style modifiers for consistency
                prompt = f"{desc}, cinematic lighting, photorealistic, 8k, aspect ratio 9:16 vertical"
                
                # Generate
                filename = f"sb_{uuid.uuid4()}.png"
                path = self.artist.generate_image(prompt, output_filename=filename)
                
                # Attach to scene object
                scene['image_path'] = path
                
        return script_data

    def _clean_json(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        try:
            return json.loads(text)
        except:
             return {}
