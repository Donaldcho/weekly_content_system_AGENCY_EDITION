import requests
import os
import streamlit as st
from backend.database import Database

def get_active_fb_token():
    """Retrieves the Facebook Page token and Page ID from the DB."""
    db = st.session_state.db if 'db' in st.session_state else Database()
    token_data = db.get_token("Facebook")
    if token_data:
        return token_data.get('access_token'), token_data.get('user_id') # user_id is Page ID here
    return None, None

def post_to_facebook(text_content, image_path=None):
    """
    Posts text (and optional image) to a Facebook Page.
    """
    access_token, page_id = get_active_fb_token()
    if not access_token or not page_id:
        return False, "No active Facebook connection found."

    # Handle Demo Mode
    if access_token == "FB_DEMO":
        print("[DEMO] Facebook post simulated.")
        return True, "fb_demo_id_123"

    try:
        if image_path and os.path.exists(image_path):
            # Image Post
            url = f"https://graph.facebook.com/v22.0/{page_id}/photos"
            files = {
                'source': open(image_path, 'rb')
            }
            data = {
                'message': text_content,
                'access_token': access_token
            }
            response = requests.post(url, files=files, data=data, timeout=15)
        else:
            # Text only
            url = f"https://graph.facebook.com/v22.0/{page_id}/feed"
            data = {
                'message': text_content,
                'access_token': access_token
            }
            response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            return True, response.json().get('id') or response.json().get('post_id')
        else:
            return False, response.text

    except Exception as e:
        return False, str(e)
