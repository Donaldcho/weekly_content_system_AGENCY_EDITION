from backend.adk.tools import Toolbox
import google.generativeai as genai

class BaseAdkAgent:
    def __init__(self, name, model="gemini-2.0-flash-exp"):
        self.name = name
        self.model_name = model
        self.tools = Toolbox()
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt, json_mode=True):
        """
        Standard generation wrapper with JSON enforcement.
        """
        try:
            config = genai.GenerationConfig(response_mime_type="application/json") if json_mode else None
            response = self.model.generate_content(prompt, generation_config=config)
            return response.text
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return "{}"
