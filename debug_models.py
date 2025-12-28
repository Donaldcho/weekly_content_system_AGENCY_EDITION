import google.generativeai as genai
import os
from project_config import Config

genai.configure(api_key=Config.GOOGLE_API_KEY)

print("List of available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
