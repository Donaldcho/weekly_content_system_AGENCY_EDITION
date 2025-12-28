import streamlit as st
from backend.community_agent import CommunityAgent

def render_inbox_page():
    if 'community_agent' not in st.session_state:
        st.session_state.community_agent = CommunityAgent()
        
    st.title("💬 Community Central")
    st.caption("Unified Inbox (LinkedIn, X, IG)")
    
    # Init State for selected message
    if 'selected_msg_id' not in st.session_state:
        st.session_state.selected_msg_id = None
        
    # --- LAYOUT Grid ---
    # Col 1: Folders (Narrow)
    # Col 2: Message List (Medium)
    # Col 3: Thread / Reply (Wide)
    c_blue, c_list, c_detail = st.columns([1, 2, 4])
    
    # === 1. FOLDERS ===
    with c_blue:
        st.markdown("### 🗂️")
        folder = st.radio("Folder", ["📥 Inbox", "✅ Done", "🚫 Spam"], label_visibility="collapsed")
        # Map folder name to key
        f_key = "inbox" if "Inbox" in folder else "done" if "Done" in folder else "spam"
    
    # === 2. MESSAGE LIST ===
    with c_list:
        st.markdown(f"### {folder}")
        msgs = st.session_state.community_agent.fetch_messages(f_key)
        
        if not msgs:
            st.caption("All caught up! 🎉")
        
        for m in msgs:
            # Highlight selected
            is_sel = st.session_state.selected_msg_id == m['id']
            border_col = "#7D3C98" if is_sel else None
            
            # Message Card
            if st.button(f"{m['avatar']} {m['author']}\n{m['preview']}", key=f"msg_{m['id']}", use_container_width=True):
                st.session_state.selected_msg_id = m['id']
                st.session_state.community_agent.mark_as_read(m['id'])
                st.rerun()

    # === 3. THREAD VIEW ===
    with c_detail:
        sel_id = st.session_state.selected_msg_id
        if sel_id:
            msg = next((x for x in msgs if x['id'] == sel_id), None)
            if not msg:
                 # Look in other folders if moved? Or just reset
                 msg = next((x for x in st.session_state.community_agent.messages if x['id'] == sel_id), None)
            
            if msg:
                with st.container(border=True):
                    # Header
                    h1, h2 = st.columns([1, 4])
                    h1.markdown(f"## {msg['avatar']}")
                    h2.markdown(f"**{msg['author']}** via {msg['platform']}")
                    h2.caption(msg['timestamp'])
                    
                    st.divider()
                    st.write(msg['full_text'])
                    
                st.markdown("### ↩️ Reply")
                
                # --- AI ASSISTANT ---
                if st.button("✨ Auto-Draft Smart Replies"):
                    with st.spinner("Brainstorming..."):
                        replies = st.session_state.community_agent.generate_smart_reply(msg)
                        st.session_state.smart_drafts = replies
                
                # Show Draft Options
                reply_text = ""
                if 'smart_drafts' in st.session_state:
                    cols = st.columns(3)
                    for i, r in enumerate(st.session_state.smart_drafts):
                        with cols[i]:
                            if st.button(f"Option {i+1}", help=r):
                                st.session_state.draft_choice = r
                    
                    if 'draft_choice' in st.session_state:
                        reply_text = st.session_state.draft_choice
                
                # Edit Box
                final_reply = st.text_area("Draft", value=reply_text, height=150)
                
                # Send Button
                if st.button("✈️ Send Reply", type="primary"):
                    st.session_state.community_agent.send_reply(msg['id'], final_reply)
                    st.toast("Sent!")
                    # Clear selection and rerun to update list
                    st.session_state.selected_msg_id = None
                    if 'smart_drafts' in st.session_state: del st.session_state.smart_drafts
                    if 'draft_choice' in st.session_state: del st.session_state.draft_choice
                    st.rerun()
                    
            else:
                st.info("Message not found (might be moved).")
        else:
            st.info("Select a message to view the thread.")
