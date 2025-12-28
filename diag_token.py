import requests
from backend.database import Database

db = Database()
row = db.get_token("LinkedIn")
if not row:
    print("No token found.")
    exit()

token = row['access_token']
headers = {
    "Authorization": f"Bearer {token}",
    "LinkedIn-Version": "202306",
    "X-Restli-Protocol-Version": "2.0.0"
}

print(f"Token (start): {token[:15]}...")

endpoints = [
    ("Userinfo (OpenID)", "https://api.linkedin.com/v2/userinfo"),
    ("Me (LiteProfile)", "https://api.linkedin.com/v2/me"),
    ("Email (Email Scope)", "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))")
]

for name, url in endpoints:
    print(f"\n--- {name} ---")
    try:
        r = requests.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
