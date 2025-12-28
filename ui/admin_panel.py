import streamlit as st
import pandas as pd

def render_admin_panel():
    st.header("👥 User Management")
    st.markdown("Manage access to the Enterprise Edition.")
    
    # 1. Add New User
    with st.expander("➕ Add New User", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            new_username = st.text_input("Username", placeholder="e.g. Jane Doe")
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Required")
        with col3:
            new_role = st.selectbox("Role", ["admin", "editor", "writer"])
        with col4:
            st.write("") # Spacer
            st.write("")
            if st.button("Create Account", use_container_width=True):
                if new_username and new_password:
                    success = st.session_state.db.add_user(new_username, new_role, new_password)
                    if success:
                        st.success(f"User '{new_username}' created!")
                        st.rerun()
                    else:
                        st.error("Username already exists.")
                else:
                    st.warning("Username and Password required.")

    st.divider()

    # 2. List Users
    users = st.session_state.db.get_users()
    
    if users:
        # Convert to DataFrame for cleaner display, though we'll use columns for actions
        st.subheader(f"Active Users ({len(users)})")
        
        for user in users:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{user['username']}**")
            with c2:
                role_color = "red" if user['role'] == 'admin' else "orange" if user['role'] == 'editor' else "blue"
                st.markdown(f":{role_color}[{user['role'].upper()}]")
            with c3:
                # Don't allow deleting yourself
                if user['username'] != st.session_state.current_user['username']:
                    if st.button("🗑️", key=f"del_{user['username']}", help="Delete User"):
                        st.session_state.db.delete_user(user['username'])
                        st.rerun()
                else:
                    st.caption("(You)")
                    
    else:
        st.info("No users found.")
