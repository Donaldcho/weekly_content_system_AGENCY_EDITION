import streamlit as st
import pandas as pd
from backend.crm_agent import CRMAgent

def render_crm_page():
    if 'crm_agent' not in st.session_state:
        st.session_state.crm_agent = CRMAgent()
        
    st.title("💰 CRM & ROI Nexus")
    st.caption("Closing the loop: From 'Content' to 'Cash'.")

    # --- 1. KPI ROW ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pipeline Value", "$42,500", "+$15k")
    k2.metric("Warm Leads", "18", "+3")
    k3.metric("Cost per Lead", "$45.20", "-12%")
    k4.metric("ROI (30d)", "420%", "🚀")
    
    st.divider()

    # --- 2. PIPELINE VIEW (Kanban Style) ---
    st.subheader("🔥 Lead Scoring Agents (Live)")
    st.info("The Agent monitors comments/DMs and assigns scores based on intent signals.")
    
    leads = st.session_state.crm_agent.get_pipeline_data()
    
    col_cold, col_warm, col_hot = st.columns(3)
    
    with col_cold:
        st.markdown("### ❄️ Cold (0-30)")
        for l in leads:
            if l['status'] == 'Cold':
                _render_lead_card(l)

    with col_warm:
        st.markdown("### 🔥 Warm (31-70)")
        for l in leads:
            if l['status'] == 'Warm':
                _render_lead_card(l)

    with col_hot:
        st.markdown("### 💰 Hot (71+)")
        for l in leads:
            if l['status'] == 'Hot':
                _render_lead_card(l)

    st.divider()
    
    # --- 3. ATTRIBUTION GRAPH ---
    st.subheader("📈 Attribution Modeling")
    st.caption("Simulated view of Content Costs vs. Generated Revenue")
    
    roi_data = st.session_state.crm_agent.get_roi_data()
    st.line_chart(roi_data.set_index("Date"))


def _render_lead_card(lead):
    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        c1.write(lead['avatar'])
        c2.markdown(f"**{lead['name']}**")
        c2.caption(lead.get('role', 'User'))
        
        st.progress(lead['score'] / 100, f"Score: {lead['score']}")
        st.caption(f"Signal: {lead['last_action']}")
        
        if lead.get('value'):
            st.markdown(f"**Potential: {lead['value']}**")
            if st.button("Close Deal", key=f"close_{lead['name']}"):
                st.balloons()
                st.toast(f"Deal Closed! Revenue booked.")
