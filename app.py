import streamlit as st
import os
from ui.styles import CUSTOM_CSS
# Force Reload Fix
from ui.generate import render_generate_page
from ui.scheduler import render_scheduler_page
from ui.vault import render_vault_page
from ui.brand import render_brand_page
from ui.dashboard import render_dashboard

from backend.database import Database

# Page Config
# Import the new Login Module
from ui.login import render_login

# Page Config
st.set_page_config(
    page_title="Deviceterra | Enterprise",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Styles
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SECURITY GATEKEEPER ---
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if not st.session_state.is_authenticated:
    render_login()
    st.stop()  # STOPS all execution here until logged in

# ==============================================
# 🚀 AUTHORIZED ZONE (The App Loads Below)
# ==============================================

# Initialize DB
if 'db' not in st.session_state:
    st.session_state.db = Database()
elif not hasattr(st.session_state.db, 'log_usage'):
    # Force reload if instance is stale (missing new methods)
    print("Detected stale DB instance. Reloading...")
    st.session_state.db = Database()

# Helper to load/save brand settings
if 'brand_info' not in st.session_state:
    st.session_state.brand_info = st.session_state.db.get_brand_settings()

# Initialize Marketing Agency (ADK)
if 'agency' not in st.session_state:
    from backend.adk.main import MarketingAgency
    print("Initializing Marketing Agency...")
    st.session_state.agency = MarketingAgency()

# --- SIDEBAR NAV ---
with st.sidebar:
    # --- RBAC USER SWITCHER ---
    users = st.session_state.db.get_users()
    if not users: users = [{"username": "Default", "role": "admin"}]
    
    user_names = [u['username'] for u in users]
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = users[0]
        
    selected_user_name = st.selectbox("👤 User Role (Simulated)", user_names, index=0)
    
    # Update state if changed
    if selected_user_name != st.session_state.current_user['username']:
        st.session_state.current_user = next((u for u in users if u['username'] == selected_user_name), users[0])
        st.rerun()
        
    curr_role = st.session_state.current_user['role'].upper()
    role_color = "#E74C3C" if curr_role == 'ADMIN' else "#F39C12" if curr_role == 'EDITOR' else "#3498DB"

    # Profile Header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, {role_color}, #2C3E50); border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
            { '🦸‍♂️' if curr_role == 'ADMIN' else '🕵️' if curr_role == 'EDITOR' else '✍️' }
        </div>
        <h3 style="margin:0; padding:0;">{st.session_state.current_user['username']}</h3>
        <span class="status-pill" style="background: {role_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">{curr_role}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- AGENCY CONTEXT BADGE ---
    if 'current_client_id' not in st.session_state:
        st.session_state.current_client_id = 1 # Default
        st.session_state.current_client_name = "Default Agency"
        
    st.info(f"🏢 Workspace: **{st.session_state.get('current_client_name', 'Unknown')}**")

    # --- NAVIGATION SYSTEM ---
    
    # 1. Define Structure
    NAV_STRUCTURE = {
        "🏢 Headquarters": [
            "📊 Dashboard",
            "💰 CRM & ROI",
            "📡 The Sentinel"
        ],
        "🎨 Creative Studio": [
            "🚀 Launchpad",
            "✨ Content Studio",
            "🎬 AI Video Director",
            "🎨 Visual Editor",
            "🚀 Multiplier"
        ],
        "⚡ Operations": [
            "📅 Scheduler",
            "💬 Community Central"
        ],
        "⚙️ Settings": [
            "🧬 Brand Identity",
            "🔌 Connections"
        ]
    }
    
    # Dynamic Admin Injection
    if st.session_state.current_user['role'] == 'admin':
        NAV_STRUCTURE["🏢 Headquarters"].insert(0, "🏢 Command Center") # Agency Dashboard
        NAV_STRUCTURE["⚙️ Settings"].insert(0, "👥 User Management")
    
    # 2. State Management for Nav
    if "current_department" not in st.session_state:
        st.session_state.current_department = "🏢 Headquarters"
    if "main_nav" not in st.session_state:
        st.session_state.main_nav = "📊 Dashboard"

    st.markdown("---")
    
    # 3. Department Switcher (Top Level)
    selected_dept = st.selectbox(
        "Department",
        list(NAV_STRUCTURE.keys()),
        index=list(NAV_STRUCTURE.keys()).index(st.session_state.current_department),
        label_visibility="collapsed"
    )
    st.session_state.current_department = selected_dept
    
    # 4. Tool Switcher (Second Level)
    # We filter options based on Dept
    available_tools = NAV_STRUCTURE[selected_dept]
    
    # Ensure current selection is valid for this dept, otherwise default to first
    try:
        current_index = available_tools.index(st.session_state.main_nav)
    except ValueError:
        current_index = 0
        st.session_state.main_nav = available_tools[0] # Auto-switch if Dept changed
        
    selected_tool = st.radio(
        "Tool",
        available_tools,
        index=current_index,
        label_visibility="collapsed",
        key="nav_radio"
    )
    
    # Sync selection
    if selected_tool != st.session_state.main_nav:
        st.session_state.main_nav = selected_tool
        st.rerun()

    # Capture for routing below
    selected_page = st.session_state.main_nav
    
    st.markdown("---")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.is_authenticated = False
        st.rerun()

# --- PAGE ROUTING ---
if selected_page == "🏢 Command Center":
    from ui.agency_dashboard import render_agency_dashboard
    render_agency_dashboard()

elif selected_page == "📊 Dashboard":
    render_dashboard()
    
elif selected_page == "📡 The Sentinel":
    from ui.sentinel import render_sentinel_page
    render_sentinel_page()

elif selected_page == "🎬 AI Video Director":
    from ui.video_studio import render_video_studio_page
    render_video_studio_page()

elif selected_page == "💰 CRM & ROI":
    from ui.crm_dashboard import render_crm_page
    render_crm_page()

elif selected_page == "💬 Community Central":
    from ui.inbox import render_inbox_page
    render_inbox_page()

elif selected_page == "🚀 Launchpad":
    from ui.launchpad import render_launchpad_page
    render_launchpad_page()

elif selected_page == "✨ Content Studio": 
    render_generate_page()

elif selected_page == "🚀 Multiplier":
    from ui.repurpose import render_repurpose_page
    render_repurpose_page()

elif selected_page == "🎨 Visual Editor":
    from ui.editor import render_editor_page
    render_editor_page()

elif selected_page == "🧬 Brand Identity":
    from ui.brand import render_brand_page
    render_brand_page()

elif selected_page == "📅 Scheduler":
    from ui.scheduler import render_scheduler_page
    render_scheduler_page()
    
elif selected_page == "🔌 Connections":
    from ui.connections import render_connections_page
    render_connections_page()

elif selected_page == "👥 User Management":
    from ui.admin_panel import render_admin_panel
    render_admin_panel()
