import json
import os
import sys

# Add parent to path if needed (standard pattern in this codebase)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config

class PromptRegistry:
    def __init__(self):
        self.config = Config()
        self.prompts_path = os.path.join(self.config.ASSETS_DIR, "prompts.json")
        self._prompts = self._load_prompts()

    def _load_prompts(self):
        if not os.path.exists(self.prompts_path):
            print(f"Warning: prompts.json not found at {self.prompts_path}")
            return {}
        try:
            with open(self.prompts_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading prompts.json: {e}")
            return {}

    def get(self, key, **kwargs):
        """
        Retrieves a prompt template by key and formats it with kwargs.
        Returns the raw template string if formatting fails/missing args.
        """
        template = self._prompts.get(key, "")
        if not template:
            return f"[Missing Prompt: {key}]"
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Flexible formatting: If a key is missing, leave it (or warn)
            # For robustness, we might want to verify keys, but for now just return safe format
            # This is a basic implementation. Custom logic can handle partial formatting if needed.
            print(f"Prompt formatting warning (missing key): {e}")
            return template
        except Exception as e:
            print(f"Prompt formatting error: {e}")
            return template

    def update(self, key, new_template):
        self._prompts[key] = new_template
        self._save()

    def _save(self):
        try:
            with open(self.prompts_path, 'w', encoding='utf-8') as f:
                json.dump(self._prompts, f, indent=4)
        except Exception as e:
            print(f"Error saving prompts.json: {e}")
