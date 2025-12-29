from google import genai
import sys

print(f"Python Version: {sys.version}")
try:
    print(f"GenAI Version: {genai.__version__}")
except:
    pass

try:
    client = genai.Client(api_key="TEST_KEY")
    print("\nDir(client):")
    print(dir(client))
    
    print("\nDir(client.models):")
    print(dir(client.models))
    
    if hasattr(client, 'imagen'):
        print("\nDir(client.imagen):")
        print(dir(client.imagen))
except Exception as e:
    print(f"Error inspecting client: {e}")
