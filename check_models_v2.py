from google import genai
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project_config import Config

def list_models_v2():
    if not Config.GOOGLE_API_KEY:
        print("API Key missing.")
        return

    client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    print("Listing available models (v2/Client)...")
    try:
        # Pager object
        pager = client.models.list()
        for m in pager:
            print(f"Name: {m.name} | Capabilities: {m.supported_actions}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models_v2()
