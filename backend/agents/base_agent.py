import google.generativeai as genai
import sys
import os

# Add parent dir to path to find project_config if needed, though usually handled by app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from project_config import Config
from backend.database import Database

class BaseAgent:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.model_name = model_name
        conf = Config()
        if not conf.GOOGLE_API_KEY:
             raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=conf.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)
        self.db = Database()

    def generate(self, prompt, json_mode=False):
        """
        Generic generation wrapper.
        """
        try:
            # If JSON mode is requested, we can append instruction or use generation config if available
            # For now, we'll just append a strong instruction if json_mode is True
            if json_mode:
                prompt += "\n\nOutput strictly as valid JSON key-value pairs. No Markdown code blocks."
            
            response = self.model.generate_content(prompt)
            
            # --- COST LOGGING ---
            try:
                usage = response.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name=self.__class__.__name__,
                        model=self.model_name,
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except Exception as e:
                print(f"Failed to log usage: {e}")

            return response.text
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {e}")
            return f"Error: {str(e)}"
