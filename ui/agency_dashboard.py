import streamlit as st
import pandas as pd

def render_agency_dashboard():
    st.title("🏢 Agency Command Center")
    st.markdown("Manage your client roster and switch workspaces.")
    
    # --- 1. Client Switcher (Context Manager) ---
    clients = st.session_state.db.get_clients()
    
    if not clients:
        st.warning("No clients found. System auto-repairing...")
        # Should have struck default in migration, but safe fallback
        st.session_state.db.add_client("Default Agency")
        st.rerun()

    # Current Context Display
    current_client_id = st.session_state.get('current_client_id', 1)
    current_client = next((c for c in clients if c['id'] == current_client_id), clients[0])
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Active Workspace", current_client['name'])
    with col_stat2:
        st.metric("Total Clients", len(clients))
    with col_stat3:
        st.metric("Agency Tier", "Enterprise")

    st.divider()

    # --- 2. Workspace Selector ---
    st.subheader("🔁 Switch Workspace")
    
    # Visual Grid of Clients
    cols = st.columns(3)
    for i, client in enumerate(clients):
        with cols[i % 3]:
            # Card-like
            with st.container(border=True):
                st.markdown(f"### {client['name']}")
                st.caption(f"Industry: {client['industry']}")
                
                is_active = (client['id'] == current_client_id)
                
                if is_active:
                    st.button("✅ Active", key=f"btn_act_{client['id']}", disabled=True, use_container_width=True)
                else:
                    if st.button("🚀 Switch", key=f"btn_switch_{client['id']}", use_container_width=True):
                        st.session_state.current_client_id = client['id']
                        st.session_state.current_client_name = client['name']
                        st.success(f"Switched to {client['name']}!")
                        st.rerun()

    st.divider()

    # --- 3. Add New Client ---
    with st.expander("➕ Onboard New Client"):
        with st.form("new_client_form"):
            c_name = st.text_input("Brand Name", placeholder="e.g. Acme Corp")
            c_industry = st.selectbox("Industry", ["Technology", "Retail", "Healthcare", "Food & Bev", "General"])
            
            if st.form_submit_button("Create Workspace"):
                if c_name:
                    new_id = st.session_state.db.add_client(c_name, c_industry)
                    if new_id:
                        st.success(f"Client '{c_name}' created!")
                        st.rerun()
                    else:
                        st.error("Client name already exists.")
                else:
                    st.warning("Name required.")
