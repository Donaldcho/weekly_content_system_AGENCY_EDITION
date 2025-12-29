
import google.generativeai as genai
import os
import sys

print(f"Python Executable: {sys.executable}")
print(f"GenAI Version: {genai.__version__}")

try:
    if hasattr(genai, 'ImageGenerationModel'):
        print("SUCCESS: ImageGenerationModel found.")
        
        # Try to init (requires API key)
        # We assume standard env var or config setup
        sys.path.append(os.getcwd())
        from project_config import Config
        api_key = Config().GOOGLE_API_KEY
        if not api_key:
            print("WARNING: No API Key found in Config.")
            sys.exit(0)
            
        genai.configure(api_key=api_key)
        
        print("Attempting to instantiate model...")
        model = genai.ImageGenerationModel("imagen-3.0-generate-001")
        print("Model instantiated. Attempting dry run...")
        # We won't actually call generate to save quota/time unless strictly needed, 
        # but just instantiating is often enough to check basic library health.
        # Actually, let's try a tiny prompt.
        try:
            resp = model.generate_images(prompt="A small red dot", number_of_images=1)
            print("SUCCESS: Image generated!")
        except Exception as e:
            print(f"API ERROR during generation: {e}")

    else:
        print("FAILURE: ImageGenerationModel NOT found in this version.")
        print(f"Dir(genai): {dir(genai)}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
