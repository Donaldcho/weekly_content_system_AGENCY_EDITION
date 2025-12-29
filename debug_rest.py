
import requests
import json
import os
import sys

# Load Config
sys.path.append(os.getcwd())
from project_config import Config
conf = Config()
api_key = conf.GOOGLE_API_KEY

print(f"Testing REST API with Key: {api_key[:5]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
headers = {"Content-Type": "application/json"}
data = {
    "instances": [
        {"prompt": "A futuristic banana with cybernetic implants"}
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1"
    }
}

try:
    print("Sending request...")
    resp = requests.post(url, headers=headers, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
    
    if resp.status_code == 200:
        print("SUCCESS! We can use REST.")
    else:
        print("REST Failed.")

except Exception as e:
    print(f"Exception: {e}")
