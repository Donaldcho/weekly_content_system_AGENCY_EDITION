import google.generativeai as genai
import os
import sys

# Add parent directory to path to import project_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config

def test_link():
    conf = Config()
    if not conf.GOOGLE_API_KEY:
        print("❌ No API Key found.")
        return

    print(f"🔑 API Key found: {conf.GOOGLE_API_KEY[:5]}...")
    genai.configure(api_key=conf.GOOGLE_API_KEY)

    models_to_test = [
        "gemini-3-pro-image-preview",   # Nano Pro
        "gemini-2.5-flash-image",       # Nano
        "imagen-3.0-generate-001"       # Legacy
    ]

    print("\n--- Testing Model Availability (Stable SDK) ---")
    
    for m_name in models_to_test:
        print(f"\n📡 Pinging: {m_name}")
        try:
            model = genai.ImageGenerationModel(m_name)
            # Try a dry run / minimal generation
            response = model.generate_images(
                prompt="A small red dot.",
                number_of_images=1
            )
            print(f"✅ SUCCESS: {m_name} is ALIVE and generated an image.")
        except Exception as e:
            print(f"❌ FAILURE: {m_name} failed.")
            print(f"   Error: {str(e)}")

if __name__ == "__main__":
    test_link()
