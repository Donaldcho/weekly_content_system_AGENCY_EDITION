import requests
import urllib.parse
from datetime import datetime, timedelta
import streamlit as st
from backend.database import Database
from project_config import Config

# Configuration
# Ideally these should be in .env. We use Config from project_config.py
# If not present, we can fallback or handle gracefully.
# Configuration: Dynamic Fetch
REDIRECT_URI_LINKEDIN = "http://localhost:8501"
REDIRECT_URI_FACEBOOK = "http://localhost:8501/"

def get_linkedin_credentials():
    """
    Fetches credentials from:
    1. Streamlit Secrets (secrets.toml)
    2. Project Config (.env)
    3. Database (System Settings - UI Input)
    """
    c_id = None
    c_secret = None
    
    # 1. Try Secrets
    try:
        if "connections" in st.secrets and "linkedin" in st.secrets["connections"]:
            secrets_li = st.secrets["connections"]["linkedin"]
            c_id = secrets_li.get("CLIENT_ID")
            c_secret = secrets_li.get("CLIENT_SECRET")
    except FileNotFoundError:
        pass

    # 2. Try Config (Env) overrides if not found
    conf = Config()
    if not c_id and conf.LINKEDIN_CLIENT_ID:
        val = conf.LINKEDIN_CLIENT_ID
        if "YOUR_" not in val and "PASTE_" not in val:
            c_id = val
            
    if not c_secret and conf.LINKEDIN_CLIENT_SECRET:
        val = conf.LINKEDIN_CLIENT_SECRET
        if "YOUR_" not in val and "PASTE_" not in val and "WPL_AP1" not in val:
            c_secret = val

    # 3. Try Database (System Settings)
    if not c_id or not c_secret:
        try:
            # We instantiate DB here. Since this is called on-demand, it's safe.
            if 'db' in st.session_state:
                db = st.session_state.db
            else:
                db = Database()
                
            if not c_id:
                c_id = db.get_system_setting("linkedin_client_id")
                if c_id: print(f"DEBUG: Found CID in DB: {c_id[:5]}...")
            if not c_secret:
                c_secret = db.get_system_setting("linkedin_client_secret")
        except Exception as e:
            print(f"DEBUG: DB Fetch Error: {e}")
            pass 
            
    # VALIDATION: Filter out placeholders or partial edits
    if c_id and ("YOUR_" in c_id or "PASTE_" in c_id or "LINKEDIN_CLIENT_ID" in c_id):
        print(f"DEBUG: Rejected CID due to placeholder: {c_id}")
        c_id = None
        
    if c_secret and ("YOUR_" in c_secret or "PASTE_" in c_secret): 
        c_secret = None

    print(f"DEBUG: Final Credentials resolved: CID={bool(c_id)}, SEC={bool(c_secret)}")
    return c_id, c_secret

def get_linkedin_auth_url():
    """
    Step 1: Generate the link the user clicks to start the process.
    """
    client_id, _ = get_linkedin_credentials()
    
    if not client_id:
        return None # Caller handles this as "needs setup"

    base_url = "https://www.linkedin.com/oauth/v2/authorization"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI_LINKEDIN,
        "scope": "w_member_social openid profile email", 
        "state": "linkedin"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def exchange_linkedin_code(verification_code):
    """
    Step 3: Trade the code for a permanent Token.
    """
    client_id, client_secret = get_linkedin_credentials()
    
    if not client_id or not client_secret:
        return False, "Missing App Credentials (Client ID/Secret)"

    if not verification_code:
        return False, "No code provided."
        
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": verification_code,
        "redirect_uri": REDIRECT_URI_LINKEDIN,
        "client_id": client_id,
        "client_secret": client_secret
    }
    print(f"DEBUG: EXCHANGING CODE. CID={client_id[:5]}... Full CID match: {client_id}") # DEBUG
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            id_token = data.get('id_token')
            granted_scopes = data.get('scope') # LinkedIn returns 'scope' as space-separated string
            expires_in = data.get('expires_in', 5184000) # Default 60 days
            
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(seconds=expires_in)
            
            # Fetch User ID (URN)
            user_id = "Unknown"
            
            # PHASE 1: Try ID Token (OIDC) - Most reliable for modern apps
            if id_token:
                try:
                    # LinkedIn id_token is a JWT. We decode the payload without secret to get 'sub'
                    import base64
                    import json
                    payload_b64 = id_token.split('.')[1]
                    # Add padding if needed
                    payload_b64 += '=' * (4 - len(payload_b64) % 4)
                    payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
                    user_id = payload.get('sub')
                    if user_id: 
                         print(f"DEBUG: Found URN in id_token: {user_id}")
                         # Userinfo usually expects urn:li:person:ID
                         if not user_id.startswith("urn:li:"):
                              user_id = f"urn:li:person:{user_id}"
                except Exception as e:
                    print(f"DEBUG: id_token parse error: {e}")

            headers = {"Authorization": f"Bearer {token}"}
            # PHASE 2: Fallback to /userinfo if unknown
            if user_id == "Unknown":
                try:
                    # Basic profile fetch to get stats/ID
                    me_resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=5)
                    if me_resp.status_code == 200:
                         user_id = me_resp.json().get('sub', 'Unknown')
                except:
                    pass

            # PHASE 3: Fallback to /me if still unknown
            if user_id == "Unknown":
                 try:
                    me_resp = requests.get("https://api.linkedin.com/v2/me", headers=headers, timeout=5)
                    if me_resp.status_code == 200:
                         user_id = f"urn:li:person:{me_resp.json().get('id')}"
                 except:
                    pass

            # Save to DB
            if 'db' not in st.session_state:
                st.session_state.db = Database()

            # PRESERVATION LOGIC: If we got "Unknown" but already have a better URN in DB, keep the old one.
            final_user_id = user_id
            if user_id == "Unknown" or not user_id:
                 existing = st.session_state.db.get_token("LinkedIn")
                 if existing and existing.get('user_id') and "Unknown" not in existing.get('user_id'):
                      final_user_id = existing.get('user_id')
                      print(f"DEBUG: Preserving existing URN: {final_user_id}")
                
            st.session_state.db.save_token("LinkedIn", token, None, expiry_date, final_user_id, id_token, granted_scopes)
            return True, f"Connected successfully as {final_user_id}!"
        else:
            return False, f"LinkedIn Error ({response.status_code}): {response.text} (Used URI: {REDIRECT_URI_LINKEDIN})"
            
    except Exception as e:
        return False, f"Connection Failed: {str(e)}"

# ... (Previous V2 function skipped for brevity as it doesn't use standard constant) ...

def get_facebook_credentials():
    """
    Waterfall logic for Facebook credentials:
    1. Streamlit Secrets
    2. Project Config (Env)
    3. Database (System Settings)
    """
    c_id = None
    c_secret = None
    
    # 1. Try Secrets
    try:
        if "connections" in st.secrets and "facebook" in st.secrets["connections"]:
            secrets_fb = st.secrets["connections"]["facebook"]
            c_id = secrets_fb.get("PAGE_ID") # Page ID for FB? No, App ID
            c_id = secrets_fb.get("CLIENT_ID") or secrets_fb.get("APP_ID")
            c_secret = secrets_fb.get("CLIENT_SECRET") or secrets_fb.get("APP_SECRET")
    except FileNotFoundError:
        pass

    # 2. Try Config
    conf = Config()
    if not c_id and conf.FACEBOOK_CLIENT_ID:
        c_id = conf.FACEBOOK_CLIENT_ID
    if not c_secret and conf.FACEBOOK_CLIENT_SECRET:
        c_secret = conf.FACEBOOK_CLIENT_SECRET

    # 3. Try Database
    if not c_id or not c_secret:
        db = st.session_state.db if 'db' in st.session_state else Database()
        if not c_id: c_id = db.get_system_setting("facebook_client_id")
        if not c_secret: c_secret = db.get_system_setting("facebook_client_secret")

    # Placeholder Safety
    if c_id and ("YOUR_" in c_id or "PASTE_" in c_id): c_id = None
    if c_secret and ("YOUR_" in c_secret or "PASTE_" in c_secret): c_secret = None

    return c_id, c_secret

def get_facebook_auth_url():
    """
    Generates the Facebook Login URL.
    """
    client_id, _ = get_facebook_credentials()
    if not client_id: return None

    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI_FACEBOOK,
        "scope": "pages_show_list,pages_read_engagement,pages_manage_posts,public_profile",
        "response_type": "code",
        "state": "facebook",
        "auth_type": "rerequest" # Standard way to prompt for permissions again
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def exchange_facebook_code(verification_code):
    """
    Exchanges code for User Token, then User Token for Long-Lived Token, 
    then fetches Page list for UI selection.
    """
    client_id, client_secret = get_facebook_credentials()
    if not client_id or not client_secret:
        return False, "Missing Facebook App Credentials"

    # Step A: Get User Access Token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    payload = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI_FACEBOOK,
        "client_secret": client_secret,
        "code": verification_code,
    }

    try:
        # Step 1: Exchange code for short-lived User Token
        resp = requests.post(token_url, data=payload, timeout=10)
        if resp.status_code != 200:
            return False, f"FB Error (User Token): {resp.text} (Used URI: {REDIRECT_URI_FACEBOOK})"
        
        user_data = resp.json()
        short_user_token = user_data.get('access_token')

        # Step 2: Exchange for Long-Lived User Token
        ll_params = {
            "grant_type": "fb_exchange_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "fb_exchange_token": short_user_token
        }
        ll_resp = requests.get(token_url, params=ll_params, timeout=10)
        if ll_resp.status_code != 200:
            return False, f"FB Error (Long-Lived): {ll_resp.text}"
        
        ll_user_token = ll_resp.json().get('access_token')
        expires_in = ll_resp.json().get('expires_in', 5184000)
        expiry_date = datetime.now() + timedelta(seconds=expires_in)

        # Step 3: Get List of Pages
        pages_url = "https://graph.facebook.com/v18.0/me/accounts"
        pages_resp = requests.get(pages_url, params={"access_token": ll_user_token}, timeout=10)
        if pages_resp.status_code != 200:
            return False, f"FB Error (Pages): {pages_resp.text}"
        
        pages_data = pages_resp.json().get('data', [])
        if not pages_data:
            return False, "No Facebook Pages found for this user."

        # Pass to Session State for the UI 'SELECT_PAGE' flow
        st.session_state.fb_pending_pages = pages_data
        st.session_state.fb_ll_user_token = ll_user_token
        st.session_state.fb_expiry_date = expiry_date
        
        return True, "SELECT_PAGE"

    except Exception as e:
        return False, f"Facebook Connection Failed: {str(e)}"

# ...

def verify_facebook_app_credentials(client_id, client_secret):
    """Basic validation for FB App keys."""
    if not client_id or not client_secret: return False, "Missing keys."
    if "YOUR_" in client_id or "PASTE_" in client_id: return False, "Keys are placeholders."
    return True, "Form Valid"

def verify_linkedin_app_credentials(client_id, client_secret):
    # ...
    # 2. Network Check (Auth URL Probe)
    try:
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI_LINKEDIN,
            "scope": "w_member_social openid profile email", 
        }
# ...        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        
        if "invalid_client_id" in resp.text:
            return False, "LinkedIn says: Invalid Client ID (Does not exist)."
            
    except Exception:
        pass

    return True, "Valid"
