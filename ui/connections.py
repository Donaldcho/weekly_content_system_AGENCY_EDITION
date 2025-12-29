import streamlit as st
import os
import sys

# Add parent directory to path to allow imports if module resolution fails
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth_manager import (
    get_linkedin_auth_url, exchange_linkedin_code,
    get_facebook_auth_url, exchange_facebook_code
)
from backend.database import Database
from project_config import Config

def render_connections_page():
    # --- MAGIC BRIDGE (Auto-Redirect Handler) ---
    # Check if we were redirected back from LinkedIn with a code
    if "code" in st.query_params:
        code = st.query_params["code"]
        
        # Avoid re-processing if we already processed this code (simple session check)
        if "last_processed_code" not in st.session_state or st.session_state.last_processed_code != code:
            with st.spinner("🔗 Completing connection..."):
                # 1. First, check the 'state' parameter (the new reliable way)
                raw_state = st.query_params.get("state")
                current_client_id = st.session_state.get('current_client_id', 1)
                
                # Handle cases where it might be a list or a string
                platform = raw_state[0] if isinstance(raw_state, list) else raw_state
                
                if platform == "linkedin":
                    success, msg = exchange_linkedin_code(code, client_id=current_client_id)
                elif platform == "facebook":
                    success, msg = exchange_facebook_code(code, client_id=current_client_id)
                else:
                    # 2. Fallback to 'AQ' check for backward compatibility/legacy flow
                    if isinstance(code, str) and code.startswith("AQ"):
                        platform = "linkedin (fallback)"
                        success, msg = exchange_linkedin_code(code)
                    else:
                        platform = "facebook (fallback)"
                        success, msg = exchange_facebook_code(code)
                    
                if success:
                    if msg == "SELECT_PAGE":
                        st.session_state.last_processed_code = code
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.success(msg)
                        st.session_state.last_processed_code = code
                        # Clear params to clean URL
                        st.query_params.clear()
                        st.rerun()
                else:
                    st.error(f"Connection failed ({platform}): {msg}")
                    # Even on failure, we should clear the code from URL 
                    # so the user doesn't keep retrying an expired single-use code
                    if "code" in st.query_params:
                        st.session_state.last_processed_code = code
                        st.query_params.clear()
                        st.info("The single-use verification code has been cleared. Please try connecting again.")
    
    # Check for error from LinkedIn
    if "error" in st.query_params:
         st.error(f"LinkedIn Error: {st.query_params.get('error_description', 'Unknown Error')}")
         st.query_params.clear()

    st.title("🔌 Platform Connections")
    st.markdown("Link your social accounts and manage your system API keys.")

    if 'db' not in st.session_state:
        st.session_state.db = Database()

    # --- SYSTEM SETTINGS (NEW) ---
    with st.expander("🛠️ System Settings (API Keys)", expanded=not Config().GOOGLE_API_KEY):
        st.subheader("Global Credentials")
        st.info("These keys are required for the core AI functionality of Deviceterra.")
        
        conf = Config()
        g_key = conf.GOOGLE_API_KEY or ""
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_google_key = st.text_input(
                "Google Gemini API Key", 
                value=g_key, 
                type="password", 
                help="Get your key from https://aistudio.google.com/"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Save Google Key", use_container_width=True):
                if new_google_key:
                    st.session_state.db.save_system_setting("google_api_key", new_google_key)
                    st.success("Google API Key saved!")
                    st.rerun()
                else:
                    st.warning("Please enter a key.")

    st.divider()

    # --- LINKEDIN CARD ---
    with st.container(border=True):
        col_logo, col_status, col_action = st.columns([1, 3, 2])
        
        with col_logo:
            # Simple Text Logo/Icon placeholder for now or URL
            st.markdown("## 🟦") 
            st.caption("LinkedIn")
            
        with col_status:
            st.subheader("LinkedIn")
            # Check DB or Env
            token_data = st.session_state.db.get_token("LinkedIn")
            is_connected = token_data is not None
            
            # Fallback to .env check (Only if not forcibly disconnected)
            if not is_connected and not st.session_state.get('force_disconnect') and Config().LINKEDIN_ACCESS_TOKEN:
                is_connected = True
                token_data = {"user_id": Config().LINKEDIN_PERSON_URN or "EnvUser"}
            
            if is_connected:
                st.success(f"● Active (Connected as {token_data.get('user_id', 'User')})")
            else:
                st.caption("Not Connected")

        with col_action:
            if not is_connected:
                # TABS for simplicity
                tab_simple, tab_advanced = st.tabs(["✨ One-Click Demo", "🔧 Real Connection"])
                
                with tab_simple:
                    st.caption("Testing the app? Use this to simulate a connection without API keys.")
                    if st.button("Activate Demo Mode", key="demo_li"):
                         # Save a fake token calling save_token correctly
                         st.session_state.db.save_token(
                             "LinkedIn", 
                             "DEMO_TOKEN_123", 
                             "REFRESH_DEMO", 
                             3600, 
                             "Demo User"
                         )
                         st.success("Demo Connected!")
                         st.rerun()

                with tab_advanced:
                    # Check for Credentials
                    from backend.auth_manager import get_linkedin_credentials
                    c_id, c_secret = get_linkedin_credentials()

                    if not c_id or "PASTE_YOUR" in c_id or not c_secret or "PASTE_YOUR" in c_secret:
                        st.warning("⚠️ Missing App Configuration")
                        st.markdown("To connect internally, please enter your **LinkedIn Developer App** keys.")
                        

                        
                        # Direct inputs (No Form) for better responsiveness
                        new_cid = st.text_input("Client ID", key="input_cid")
                        new_sec = st.text_input("Client Secret", type="password", key="input_sec")
                        
                        if st.button("Save & Continue", type="primary"):
                            print(f"DEBUG: Save clicked. CID={bool(new_cid)}, SEC={bool(new_sec)}")
                            if new_cid and new_sec:
                                # Validation Step
                                from backend.auth_manager import verify_linkedin_app_credentials
                                is_valid, v_msg = verify_linkedin_app_credentials(new_cid, new_sec)
                                
                                if is_valid:
                                    try:
                                        st.session_state.db.save_system_setting("linkedin_client_id", new_cid)
                                        st.session_state.db.save_system_setting("linkedin_client_secret", new_sec)
                                        print("DEBUG: Saved to DB.")
                                        st.success("Validated & Saved! Reloading...")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Save Failed: {e}")
                                        print(f"DEBUG: Save Exception: {e}")
                                else:
                                    st.error(f"Validation Failed: {v_msg}")
                            else:
                                st.warning("Both fields are required.")
                    else:
                        st.caption("Ready to connect with your App.")
                        # 1. Get the Auth Link
                        auth_url = get_linkedin_auth_url()
                        
                        if auth_url:
                            # DEBUG: Show the user what we are using to prove it's correct
                            st.caption("Verify this URL uses your correct Client ID:")
                            st.code(auth_url, language="text")
                            
                            # 2. Show the "Connect" Button (Opens in new tab)
                            st.link_button("1. Connect with LinkedIn", auth_url)
                            st.caption("You will be redirected back automatically.")
                        else:
                            st.error("Configuration Error: Unable to generate auth URL.")

                        # 3. Fallback for manual code
                        with st.expander("Or enter verification code manually"):
                            st.markdown("**Enter Code** (if auto-redirect fails)")
                            code_input = st.text_input("Paste URL code here:", label_visibility="collapsed", placeholder="AQQ...")
                            
                            if st.button("Verify & Link", type="primary"):
                                if not code_input:
                                    st.warning("Please paste the code first.")
                                else:
                                    success, msg = exchange_linkedin_code(code_input)
                                    if success:
                                        st.success("Linked!")
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                        
                        # Settings
                        st.markdown("---")
                        with st.expander("⚙️ App Settings"):
                            st.caption(f"Client ID: {c_id[:4]}...{c_id[-4:] if len(c_id)>8 else ''}")
                            if st.button("Change Credentials"):
                                st.session_state.db.save_system_setting("linkedin_client_id", "")
                                st.session_state.db.save_system_setting("linkedin_client_secret", "")
                                st.rerun()
                            
                            st.markdown("---")
                            with st.expander("🛠️ Developer Debug Info"):
                                if token_data:
                                    st.caption("Use this to verify permissions granted by LinkedIn.")
                                    st.text(f"Stored URN: {token_data.get('user_id')}")
                                    st.text(f"Scopes: {token_data.get('scopes', 'Unknown (Re-connect to view)')}")
                                    if token_data.get('id_token'):
                                        st.success("✅ ID Token (OIDC) is captured.")
                                    else:
                                        st.warning("⚠️ No ID Token captured.")
                                else:
                                    st.info("No active token metadata to debug. Please connect first.")
            else:
                if st.button("Disconnect", key="disc_li"):
                    st.session_state.db.delete_token("LinkedIn")
                    st.session_state.force_disconnect = True
                    st.rerun()
                
                # Allow switching to Demo Mode even if connected (e.g. via Env)
                if token_data.get("access_token") != "DEMO_TOKEN_123":
                    st.markdown("---")
                    st.caption("Want to test functionality?")
                    if st.button("Switch to Demo Mode", key="switch_demo"):
                         st.session_state.db.save_token(
                             "LinkedIn", 
                             "DEMO_TOKEN_123", 
                             "REFRESH_DEMO", 
                             3600, 
                             "Demo User"
                         )
                         st.rerun()

    # --- FACEBOOK CARD ---
    with st.container(border=True):
        col_logo, col_status, col_action = st.columns([1, 3, 2])
        
        with col_logo:
            st.markdown("## 🔵") 
            st.caption("Facebook")
            
        with col_status:
            st.subheader("Facebook Page")
            fb_token_data = st.session_state.db.get_token("Facebook")
            is_fb_connected = fb_token_data is not None
            
            if is_fb_connected:
                # We stored Page Name in id_token
                page_name = fb_token_data.get('id_token', 'Unknown Page')
                st.success(f"● Active (Connected to {page_name})")
            elif "fb_pending_pages" in st.session_state:
                st.warning("● Action Required: Select Page")
            else:
                st.caption("Not Connected")

        with col_action:
            if not is_fb_connected:
                fb_tab_std, fb_tab_adv, fb_tab_demo = st.tabs(["⚡ Quick Connect", "⚙️ Advanced Setup", "✨ Demo"])
                
                with fb_tab_std:
                     if "fb_pending_pages" in st.session_state:
                        st.markdown("**Action Required:** Select your Facebook Page")
                        pages = st.session_state.fb_pending_pages
                        page_map = {f"{p.get('name')} (ID: {p.get('id')})": p for p in pages}
                        
                        selected_label = st.selectbox("Choose the Page to connect:", options=list(page_map.keys()), key="fb_page_sel_box")
                        
                        if st.button("Finalize Selection", type="primary", key="save_fb_final_btn"):
                            p = page_map[selected_label]
                            st.session_state.db.save_token(
                                "Facebook", 
                                p.get('access_token'), 
                                st.session_state.fb_ll_user_token, 
                                st.session_state.fb_expiry_date, 
                                p.get('id'), 
                                id_token=p.get('name'),
                                scopes="pages_manage_posts"
                            )
                            # Cleanup
                            del st.session_state.fb_pending_pages
                            del st.session_state.fb_ll_user_token
                            del st.session_state.fb_expiry_date
                            st.success(f"Connected to {p.get('name')}!")
                            st.rerun()
                     else:
                        from backend.auth_manager import get_facebook_credentials, get_facebook_auth_url
                        fb_id, fb_sec = get_facebook_credentials()
                        if not fb_id or not fb_sec:
                            st.warning("⚠️ App Setup Required")
                            st.caption("Please configure your App ID in the 'Advanced Setup' tab first.")
                        else:
                            fb_auth_url = get_facebook_auth_url()
                            if fb_auth_url:
                                st.link_button("🔵 Connect Facebook Account", fb_auth_url)
                                st.caption("After logging in, you will choose your Page here.")
                            else:
                                st.error("Auth URL generation failed.")

                with fb_tab_adv:
                    st.markdown("**Developer Settings**")
                    from backend.auth_manager import get_facebook_credentials
                    curr_fb_id, curr_fb_sec = get_facebook_credentials()
                    
                    new_fb_id = st.text_input("Facebook App ID", value=curr_fb_id if curr_fb_id else "", key="fb_id_inp")
                    new_fb_sec = st.text_input("Facebook App Secret", value=curr_fb_sec if curr_fb_sec else "", type="password", key="fb_sec_inp")
                    
                    if st.button("Save Facebook keys", key="save_fb_keys_btn"):
                        if new_fb_id and new_fb_sec:
                            st.session_state.db.save_system_setting("facebook_client_id", new_fb_id)
                            st.session_state.db.save_system_setting("facebook_client_secret", new_fb_sec)
                            st.success("Keys saved! You can now use 'Quick Connect'.")
                            st.rerun()
                        else:
                            st.error("Both fields are required.")
                    
                    from backend.auth_manager import REDIRECT_URI_FACEBOOK
                    st.divider()
                    st.caption(f"Required Redirect URI: `{REDIRECT_URI_FACEBOOK}`")

                with fb_tab_demo:
                    st.markdown("Test the dashboard without real keys.")
                    if st.button("Enter Demo Mode", key="activate_fb_demo_btn"):
                        st.session_state.db.save_token("Facebook", "FB_DEMO", "FB_REF", 3600, "123456789", "DeviceterraSM Demo Page")
                        st.rerun()
            else:
                if st.button("Disconnect Facebook", key="disc_fb"):
                    st.session_state.db.delete_token("Facebook")
                    st.rerun()
                
                if fb_token_data.get("access_token") != "FB_DEMO":
                    if st.button("Switch to Demo Mode", key="fb_to_demo_toggle"):
                         st.session_state.db.save_token("Facebook", "FB_DEMO", "FB_REF", 3600, "123456789", "DeviceterraSM Demo Page")
                         st.rerun()
