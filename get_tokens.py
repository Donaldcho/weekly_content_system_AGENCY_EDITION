import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import json
import os
import sys

# Configuration
PORT = 8501
REDIRECT_URI = f"http://localhost:{PORT}" # Removed trailing slash to match LinkedIn


# LinkedIn Config
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse query params
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if parsed_path.path == "/callback":
            if "code" in query_params:
                self.server.auth_code = query_params["code"][0]
                
                # Send a nice HTML response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <body style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
                        <h1 style='color: green;'>Success! code received.</h1>
                        <p>You can close this window and return to your terminal.</p>
                    </body>
                    </html>
                """)
            else:
                self.send_response(400)
                self.wfile.write(b"Error: No code found.")
        else:
            self.send_response(404)
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Silence server logs
        return

def get_linkedin_token():
    print("\n" + "="*50)
    print("🔵   LINKEDIN TOKEN WIZARD   🔵")
    print("="*50)
    print("1. Go to https://www.linkedin.com/developers/apps")
    print("2. Create an App (or select existing).")
    print("3. In 'Auth', add this Redirect URL: http://localhost:8000/callback")
    print(f"4. Under 'Products', ensure 'Sign In with LinkedIn' and 'Share on LinkedIn' are added.")
    print("-" * 50)
    
    client_id = input(">> Enter Client ID: ").strip()
    client_secret = input(">> Enter Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Error: Client ID and Secret are required.")
        return

    # 1. Build Authorization URL
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "state": "random_string_xyz",
        "scope": "openid profile w_member_social email" 
    }
    auth_url = f"{LINKEDIN_AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    print("\n[Action] Opening browser for you to approve access...")
    print(f"URL: {auth_url}")
    webbrowser.open(auth_url)
    
    # 2. Start Local Server to catch Callback
    print("[Waiting] Listening for callback on localhost:8000...")
    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        # Wait for one request
        httpd.handle_request()
        if hasattr(httpd, 'auth_code'):
            code = httpd.auth_code
            print(f"✅ Authorization Code captured!")
        else:
            print("❌ Failed to capture code.")
            return

    # 3. Exchange Code for Access Token
    print("[Action] Exchanging code for Access Token...")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(LINKEDIN_TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')
        
        print("\n" + "*"*50)
        print("🎉 SUCCESS! HERE IS YOUR TOKEN:")
        print("*"*50)
        print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
        print(f"(Token expires in {expires_in} seconds - approx {expires_in//86400} days)")
        
        # Determine URN (User ID)
        print("\n[Optional] Fetching Person URN...")
        headers = {"Authorization": f"Bearer {access_token}"}
        me_resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
        if me_resp.status_code == 200:
            user_data = me_resp.json()
            # userinfo returns 'sub' which is the URN ID usually
            print(f"LINKEDIN_PERSON_URN={user_data.get('sub')}")
        else:
            print("Could not automatically fetch URN. Check developer docs.")
            
        print("\n👉 COPY the validation variables above into your .env file.")
        
    except Exception as e:
        print(f"❌ Error exchanging token: {e}")
        try:
            print(response.text)
        except: pass

def get_facebook_token():
    print("\n\n" + "="*50)
    print("🔵   FACEBOOK / INSTAGRAM TOKEN GUIDE   🔵")
    print("="*50)
    print("Facebook's API is best handled via their 'Graph API Explorer' tool for developer tokens.")
    print("Since automating it requires a live HTTPS server, follow these steps manually:")
    print("-" * 50)
    
    steps = """
    1. Go to: https://developers.facebook.com/tools/explorer/
    2. Select your App in the "Meta App" dropdown.
    3. Under "User or Page", select "Get Page Access Token".
    4. Provide Permissions:
       - pages_show_list
       - pages_read_engagement
       - pages_manage_posts
    5. Click "Generate Access Token".
    6. Copy the string provided.
    
    This is your FACEBOOK_ACCESS_TOKEN.
    
    To get your Page ID:
    1. Use the explorer to run GET request: /me/accounts
    2. Find your page in the list.
    3. Copy the 'id'.
    """
    print(steps)
    print("="*50)

def main():
    print("Social Media Token Helper Tool v1.0")
    print("1. Get LinkedIn Token (Automated)")
    print("2. Get Facebook Token (Guide)")
    
    choice = input("\nSelect [1/2]: ").strip()
    
    if choice == "1":
        get_linkedin_token()
    elif choice == "2":
        get_facebook_token()
    else:
        print("Exiting.")

if __name__ == "__main__":
    main()
