import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend.database import Database

def render_dashboard():
    st.markdown("## 🚀 Command Center")
    st.markdown("Welcome back, Commander. Systems are online.")
    
    # Ensure DB
    if 'db' not in st.session_state:
        st.session_state.db = Database()

    # --- TIER 1: HUD METRICS ---
    # Fetch Real Data
    all_posts = st.session_state.db.get_all_posts()
    vault_assets = st.session_state.db.get_vault_assets()
    
    # Calc Metrics
    scheduled_count = len([p for p in all_posts if p.get('status') == 'scheduled'])
    vault_count = len(vault_assets)
    # Mock credit/streak for now (not in DB yet)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📅 Scheduled", value=str(scheduled_count), delta="Active")
    with col2:
        st.metric(label="🎨 Vault Assets", value=str(vault_count), delta=f"+{len(vault_assets[-5:])} recent" if vault_assets else "0")
    with col3:
        st.metric(label="🤖 Credits", value="92%", delta="Optimal")
    with col4:
        st.metric(label="🔥 Streak", value="14 Days", delta="Keep it up!")

    st.divider()

    # --- TIER 2: ACTION & HEALTH ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("⚡ Quick Actions")
        # Using a container for a "Card" look
        with st.container(border=True):
            ac1, ac2 = st.columns(2)
            with ac1:
                # Navigation logic handled via session_state keys in app.py
                st.button("✨ New Campaign", use_container_width=True, type="primary", 
                          on_click=lambda: st.session_state.update(main_nav="✨ Content Studio"))
                st.caption("Ignite a full weekly plan.")
            
            with ac2:
                st.button("🎨 Open Studio", use_container_width=True,
                          on_click=lambda: st.session_state.update(main_nav="🎨 Visual Editor"))
                st.caption("Create a quick visual.")

    with c2:
        st.subheader("📡 System Status")
        with st.container(border=True):
            st.markdown("**🟢 Gemini 1.5 Pro:** Online")
            st.markdown("**🟢 Nano Banana:** Online")
            st.markdown("**🟡 Social APIs:** Standby")
            st.progress(92, text="System Integrity")

    st.divider()

    # --- TIER 3: AIR TRAFFIC CONTROL (Next Up) ---
    st.subheader("📡 On Deck (Next 48 Hours)")
    
    # Filter for 'Scheduled' posts in the future
    # Basic logic: take top 3 scheduled
    upcoming = [p for p in all_posts if p.get('status') == 'scheduled'][:3]
    
    if not upcoming:
        # Fallback Mock if empty so UI looks good
        st.info("No immediate flight plan. Showing simulator data:")
        upcoming_data = [
            {"scheduled_time": "Today, 14:00", "platform": "LinkedIn", "topic": "The Future of Agents", "status": "Ready"},
            {"scheduled_time": "Tomorrow, 09:00", "platform": "Twitter", "topic": "Python Tips Thread", "status": "Drafting"},
        ]
    else:
        upcoming_data = upcoming

    for post in upcoming_data:
        # Normalize Data
        topic = post.get('topic') or post.get('linkedin_draft', '')[:30] or "Untitled Post"
        time_str = post.get('scheduled_time', 'TBD').replace('T', ' ')
        platform = post.get('platform', 'Multi')
        status = post.get('status', 'Scheduled').title()
        
        # Logic to choose color based on status
        if status in ["Ready", "Scheduled", "Posted"]:
            status_color = "#00CC96" # Green
        elif status in ["Drafting", "Draft"]:
            status_color = "#3498DB" # Blue
        else:
            status_color = "#FF4B4B" # Red

        border_color = status_color

        # Custom HTML Card for the Feed
        st.markdown(
            f"""
            <div style="
                background-color: #262730;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 4px solid {border_color};
                display: flex;
                justify_content: space-between;
                align-items: center;
            ">
                <div>
                    <div style="font-weight: bold; font-size: 1.1em; color: #FAFAFA;">{topic}</div>
                    <div style="color: #979797; font-size: 0.9em;">{platform} • {time_str}</div>
                </div>
                <div style="
                    background-color: {status_color}33;
                    color: {status_color};
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-size: 0.8em;
                    font-weight: bold;
                ">
                    {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )



    st.button("View Full Calendar", 
              on_click=lambda: st.session_state.update(main_nav="📅 Operations"))

    st.divider()
    
    # --- TIER 4: COST INTELLIGENCE ---
    st.subheader("💸 Cost Intelligence (Token Burn)")
    
    logs = st.session_state.db.get_api_usage()
    total_cost = st.session_state.db.get_total_cost()
    total_tokens = sum([l['input_tokens'] + l['output_tokens'] for l in logs]) if logs else 0
    
    # Kpi Cards
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Spend (All Time)", f"${total_cost:.4f}")
    k2.metric("Tokens Burned (Last 100 Req)", f"{total_tokens:,}")
    k3.metric("Avg Cost / Request", f"${(total_cost/len(logs)):.5f}" if logs else "$0.00")
    
    if logs:
        # Mini Chart
        df = pd.DataFrame(logs)
        # Group by Agent
        agent_cost = df.groupby('agent_name')['cost_usd'].sum().reset_index()
        st.bar_chart(agent_cost, x='agent_name', y='cost_usd', color="#FF4B4B")
        
        with st.expander("View Detailed Logs"):
            st.dataframe(df[['timestamp', 'agent_name', 'model', 'input_tokens', 'cost_usd']], use_container_width=True)
    else:
        st.info("No API logs recorded yet. Start using Agents to generate data.")
