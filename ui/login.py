import streamlit as st
import time

def render_login():
    # Centered Layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Deviceterra Enterprise</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Please sign in to access the workspace.</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g., Admin User")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                # Initialize DB if needed (auth happens before main app init sometimes)
                from backend.database import Database
                if 'db' not in st.session_state:
                    st.session_state.db = Database()
                
                # Try Auth
                user = st.session_state.db.authenticate_user(username, password)
                
                # --- MIGRATION FALLBACK ---
                # If user exists but has no password set, allow "password" as default
                if not user:
                    # Check if user exists but has no hash
                    # This requires a direct check helper or we assume 'authenticate_user' handled it.
                    # My implementations of authenticate_user returns None if no match.
                    # Let's handle the "First Login" case:
                    # If I enter "Admin User" and "password", valid?
                    # My DB logic for verify returned False if no hash. 
                    # Let's fix this by updating the user ON THE FLY if they match a legacy account? 
                    # No, that's insecure.
                    # Instead, I'll rely on the Admin creating new accounts or just update the DB via ad-hoc script? 
                    # Ideally, I should display "Login Failed".
                    pass

                if user:
                    st.success(f"Welcome back, {user['username']}!")
                    st.session_state.is_authenticated = True
                    st.session_state.current_user = user
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    # Tip for migration
                    st.info("💡 First time? Ask your admin for credentials.")

        st.markdown("---")
        st.caption("Protected by **Deviceterra Security Guard**")
