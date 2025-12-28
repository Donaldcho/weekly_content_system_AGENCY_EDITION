import requests
from backend.database import Database

db = Database()
token_data = db.get_token("LinkedIn")
if not token_data:
    print("No token found.")
    exit()

token = token_data['access_token']
headers = {
    "Authorization": f"Bearer {token}",
    "LinkedIn-Version": "202306",
    "X-Restli-Protocol-Version": "2.0.0"
}

endpoints = [
    ("Userinfo (OpenID)", "https://api.linkedin.com/v2/userinfo"),
    ("Me (LiteProfile)", "https://api.linkedin.com/v2/me"),
    ("Organizational Access", "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee")
]

for name, url in endpoints:
    print(f"\n--- Probing {name} ---")
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")
