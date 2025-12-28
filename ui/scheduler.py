import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar
from project_config import Config
from backend.database import Database
from backend.scheduler import get_calendar_events
from backend.ui_utils import st_image_robust
from backend.linkedin_poster import post_to_linkedin
from backend.facebook_poster import post_to_facebook, get_active_fb_token

# --- DIALOG: EVENT MANAGER ---
@st.dialog("Manage Post")
def show_event_manager(event_data):
    """
    A popup window to Edit, Force Publish, or Update Visuals for a post.
    """
    # Defensive check
    if 'extendedProps' not in event_data:
        st.error("Invalid event data")
        return

    props = event_data['extendedProps']
    # Fallback ID retrieval: resourceId (if resource view), id, publicId
    post_id = str(event_data.get('resourceId') or event_data.get('id') or event_data.get('publicId'))
    
    # Init Visual State for this Dialog
    if 'temp_visual_path' not in st.session_state:
        st.session_state.temp_visual_path = props.get('image')

    # 1. Header with Visuals
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        current_img = st.session_state.temp_visual_path
        if current_img:
            st_image_robust(current_img, caption="Current Visual", use_container_width=True)
        else:
            st.info("No Image")

        # --- AGENT INTELLIGENCE REPORT ---
        agent_thought = props.get('agent_thought')
        agent_reasoning = props.get('agent_reasoning')
        if agent_thought:
            with st.expander("🛡️ Agent Intelligence Report", expanded=False):
                st.markdown("**Executive Summary:**")
                st.info(agent_reasoning or "No summary available.")
                st.markdown("**Detailed Thinking:**")
                st.caption(agent_thought)
            
        # --- IMAGE MANAGER TOOLS ---
        with st.expander("🖼️ Change Visual", expanded=False):
            v_tab1, v_tab2, v_tab3 = st.tabs(["Upload", "Vault", "Gen"])
            
            # A. UPLOAD
            with v_tab1:
                up_file = st.file_uploader("New File", type=['png','jpg'], key=f"up_{post_id}")
                if up_file:
                    save_dir = os.path.join(Config().ASSETS_DIR, "vault")
                    os.makedirs(save_dir, exist_ok=True)
                    path = os.path.join(save_dir, up_file.name)
                    with open(path, "wb") as f: f.write(up_file.getbuffer())
                    st.session_state.db.save_asset(up_file.name, path, "upload", "manual_cal")
                    
                    if st.button("Set Upload", key=f"btn_up_{post_id}"):
                         st.session_state.temp_visual_path = path
                         st.rerun()

            # B. VAULT SELECT
            with v_tab2:
                assets = st.session_state.db.get_vault_assets()
                if assets:
                    # Simple Selectbox
                    opts = {a['filename']: a['file_path'] for a in assets}
                    sel = st.selectbox("Select Asset", list(opts.keys()), key=f"v_sel_{post_id}")
                    if st.button("Set Vault", key=f"btn_v_{post_id}"):
                        st.session_state.temp_visual_path = opts[sel]
                        st.rerun()
                else:
                     st.caption("Vault Empty")

            # C. GENERATE (Mock)
            with v_tab3:
                prompt = st.text_input("Prompt", key=f"p_{post_id}")
                if st.button("Generate", key=f"btn_g_{post_id}"):
                    # Mock Gen
                    st.session_state.temp_visual_path = "https://placehold.co/600x400/png?text=AI+Generated" 
                    # Note: We can't verify 'exists' on URL easily without request, so might break preview if logic is strict on os.path.exists
                    # Let's assume we mock save it properly in real app.
                    st.rerun()

    with c2:
        st.subheader(event_data['title'])
        st.caption(f"Status: {props.get('status')} | Scheduled: {event_data['start']}")
        
    st.divider()
    
    # 2. Tabs for Management
    is_posted = props.get('status') in ['Published', 'Posted']
    t_list = ["📝 Content & Visuals"]
    if is_posted: t_list.append("📊 Engagement & Community")
    
    tabs = st.tabs(t_list)
    
    # --- TAB 1: CONTENT ---
    with tabs[0]:
        current_text = props.get('content') or ""
        new_text = st.text_area("Edit Copy", value=current_text, height=250)
        
        st.divider()
        # ACTION ZONE (Moved inside tab)
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            if st.button("💾 Update Mission", type="primary"):
                post = next((p for p in st.session_state.db.get_all_posts() if str(p['id']) == post_id), None)
                if post:
                    if 'linkedin_draft' in post: post['linkedin_draft'] = new_text
                    else: post['content'] = new_text
                    if st.session_state.temp_visual_path: post['image_path'] = st.session_state.temp_visual_path
                    st.session_state.db.update_post(post_id, post)
                    if 'temp_visual_path' in st.session_state: del st.session_state.temp_visual_path
                    st.toast("Mission Updated!")
                    st.rerun()
        with col_act2:
            if not is_posted:
                if st.button("🚀 LAUNCH NOW"):
                    # Determine platform
                    post_full = next((p for p in st.session_state.db.get_all_posts() if str(p['id']) == post_id), None)
                    platform = post_full.get('platform', 'Multi') if post_full else 'Multi'
                    
                    with st.spinner(f"Publishing to {platform}..."):
                        content = props.get('content') or ""
                        image_path = props.get('image')
                        
                        success = False
                        result = "No platform selected"
                        
                        if platform == 'LinkedIn' or platform == 'Multi':
                            s, r = post_to_linkedin(content, image_path=image_path)
                            if s: success, result = s, r
                            else: result = f"LI Error: {r}"
                            
                        if platform == 'Facebook' or platform == 'Multi':
                            s, r = post_to_facebook(content, image_path=image_path)
                            if s: success, result = s, r
                            else: result = f"FB Error: {r}"

                        if success:
                            st.session_state.db.mark_as_posted(post_id, social_id=result)
                            st.success(f"Successfully Published! ID: {result}")
                            st.rerun()
                        else:
                            st.error(f"Failed to post: {result}")
            else:
                st.info("Already Published")
        with col_act3:
            if st.button("🗑️ Delete"):
                st.session_state.db.delete_post(post_id)
                st.rerun()

    # --- TAB 2: ENGAGEMENT (If Posted) ---
    if is_posted:
        with tabs[1]:
            from backend.analytics import AnalyticsSensor
            from backend.linkedin_poster import get_active_token
            
            post_full = next((p for p in st.session_state.db.get_all_posts() if str(p['id']) == post_id), None)
            social_id = post_full.get('social_id') if post_full else None
            token, _ = get_active_token()
            
            if social_id and token:
                sensor = AnalyticsSensor()
                m_col1, m_col2, m_col3 = st.columns(3)
                
                # Live Fetch
                likes, comments_count = sensor.fetch_linkedin_metrics(social_id, token)
                
                # Auto-Persist to DB (for Analytics Tab)
                # Mock impressions/ER calculation since we don't have real impressions via public API
                impressions = post_full.get('impressions', 0)
                if impressions == 0: impressions = 100 # Safe baseline
                er = round(((likes + comments_count * 2) / impressions) * 100, 2)
                st.session_state.db.update_post_metrics(post_id, likes, comments_count, impressions, er)

                m_col1.metric("Likes", likes)
                m_col2.metric("Comments", comments_count)
                m_col3.metric("Engagement (%)", er)
                
                st.markdown("#### 💬 Recent Comments")
                comments = sensor.get_comments(social_id, token)
                if comments:
                    for c in comments:
                        with st.container(border=True):
                            st.markdown(f"**{c['author']}**")
                            st.write(c['text'])
                    
                    st.divider()
                    reply_text = st.text_input("Quick Reply", placeholder="Write something...")
                    if st.button("Post Reply"):
                        from backend.linkedin_poster import post_comment
                        s, r = post_comment(social_id, reply_text)
                        if s:
                            st.toast("Reply sent!")
                            st.rerun()
                        else: st.error(r)
                else:
                    st.caption("No comments found yet.")
            else:
                st.info("Live data not available for this record.")


def render_scheduler_page():
    st.title("📅 Scheduler")
    st.markdown("Central Command for your Content Empire.")
    
    if 'db' not in st.session_state:
        st.session_state.db = Database()
        
    # --- TABS: The Two Brains ---
    tab_schedule, tab_vault, tab_analytics = st.tabs(["🗓️ Pro Calendar", "🔐 Asset Vault", "📈 Analytics"])

    # ==========================
    # TAB 1: PRO CALENDAR
    # ==========================
    with tab_schedule:
        # Layout: Sidebar (Queue) + Main (Calendar)
        col_queue, col_cal = st.columns([1, 4])
        
        # --- LEFT: THE DRAFT QUEUE ---
        with col_queue:
            st.subheader("Drafts")
            st.caption("Drag not supported yet, Click to Schedule.")
            
            # Fetch "Draft" status posts
            all_p = st.session_state.db.get_all_posts()
            drafts = [p for p in all_p if p.get('status', '').lower() == 'draft']
            
            if drafts:
                for d in drafts:
                    with st.container(border=True):
                        st.markdown(f"**{d.get('platform', 'Multi')}**")
                        # Better Title Logic: use 'topic' but fallback gracefully
                        topic = d.get('topic')
                        if not topic or topic == "Topic" or topic == "Instant Post":
                             # Try to get first line or first 30 chars
                             content = d.get('linkedin_draft') or d.get('content') or "New Draft"
                             topic = content.split('\n')[0][:30] + "..."
                        
                        st.markdown(f"**{topic}**")
                        
                        # Scheduling Actions
                        col_s1, col_s2 = st.columns([1, 1])
                        
                        # Manual Date
                        sch_date = col_s1.date_input("Date", value=datetime.now() + pd.Timedelta(days=1), key=f"date_{d['id']}", label_visibility="collapsed")
                        
                        if col_s1.button("🗓️ Set", key=f"sch_{d['id']}", help="Schedule for selected date"):
                            ts = sch_date.isoformat() + "T09:00:00"
                            st.session_state.db.update_post_date(d['id'], ts)
                            st.session_state.db.update_post_status(d['id'], 'scheduled')
                            st.toast(f"Scheduled for {sch_date}")
                            st.rerun()
                            
                        # Auto-Find Slot (Agent Powered)
                        if col_s2.button("✨ Auto", key=f"auto_{d['id']}", help="Let the Scheduling Agent decide"):
                            from backend.agents.scheduler_agent import SchedulerAgent
                            agent = SchedulerAgent()
                            
                            with st.spinner("Agent analyzing content..."):
                                drafts_content = d.get('linkedin_draft') or d.get('content') or ""
                                occupied = st.session_state.db.get_occupied_slots()
                                
                                # Get recommendation
                                recommendation = agent.suggest_slot(drafts_content, occupied)
                                ts = recommendation['suggested_timestamp']
                                reason = recommendation['reasoning']
                                thought = recommendation['thought_process']
                                
                                # Update post with date and agent metadata
                                d['scheduled_time'] = ts
                                d['status'] = 'scheduled'
                                d['agent_thought'] = thought
                                d['agent_reasoning'] = reason
                                
                                st.session_state.db.update_post(d['id'], d)
                                
                                st.info(f"🤖 Agent: {reason}")
                                st.toast(f"Scheduled for {ts[:10]}")
                                st.rerun()
            else:
                st.caption("Queue Empty")

        # --- RIGHT: THE PRO CALENDAR ---
        with col_cal:
            # 1. Fetch Events
            events = get_calendar_events()
            
            # 2. Configure Calendar Options (FullCalendar.js props)
            calendar_options = {
                "editable": True, # Allow drag and drop
                "navLinks": True,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,listWeek"
                },
                "initialView": "dayGridMonth",
                "selectable": True,
            }
            
            # 3. Specific CSS for "Blaze" Dark Mode
            custom_css = """
                .fc-event-past { opacity: 0.8; }
                .fc-event-time { font-style: italic; }
                .fc-event-title { font-weight: 700; }
                .fc-toolbar-title { font-size: 1.5em !important; color: #FAFAFA; }
                .fc-button { background-color: #262730 !important; border: 1px solid #444 !important; }
                .fc-button-active { background-color: #7D3C98 !important; }
            """

            # 4. Render Component
            state = calendar(
                events=events,
                options=calendar_options,
                custom_css=custom_css,
                key="pro_calendar"
            )

            # 5. Handle Interaction (Click)
            if state.get("eventClick"):
                clicked_event = state["eventClick"]["event"]
                show_event_manager(clicked_event)
                # clear event to avoid loop? Streamlit dialog handles it.

            # 6. Handle Drag & Drop (Rescheduling)
            if state.get("eventDrop"):
                dropped = state["eventDrop"]
                # FullCalendar returns localized string or ISO? Usually ISO
                # We need to be careful with Timezones.
                # event.start is string
                new_date = dropped["event"]["start"]
                r_id = dropped['event']['resourceId']
                
                # Update DB
                st.session_state.db.update_post_date(r_id, new_date)
                st.toast(f"Rescheduled.")


    # ==========================
    # TAB 2: THE VAULT (Preserved)
    # ==========================
    with tab_vault:
        st.subheader("🔐 Digital Asset Vault")
        
        # 1. Ingestion Area
        with st.expander("📤 Ingest New Asset"):
            up_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
            if up_file:
                if st.button("Save to Vault"):
                    # Save File
                    save_dir = os.path.join(Config().ASSETS_DIR, "vault")
                    os.makedirs(save_dir, exist_ok=True)
                    fn = up_file.name
                    path = os.path.join(save_dir, fn)
                    with open(path, "wb") as f:
                        f.write(up_file.getbuffer())
                        
                    # Save DB
                    st.session_state.db.save_asset(fn, path, "upload", "manual_upload")
                    st.success(f"Secured {fn} in Vault!")
                    st.rerun()

        # 2. Filter Bar
        f_col1, f_col2 = st.columns([4, 1])
        with f_col1:
            f_type = st.radio("Filter Class", ["All", "Generated", "Upload"], horizontal=True)
            
        # 3. Retrieve
        filter_arg = f_type.lower() if f_type != "All" else None
        assets = st.session_state.db.get_vault_assets(filter_arg)
        
        if assets:
            st.markdown(f"**{len(assets)} Secure Assets**")
            
            # Masonry Grid (4 Columns)
            cols = st.columns(4)
            for idx, asset in enumerate(assets):
                with cols[idx % 4]:
                    # Card
                    with st.container(border=True):
                        # Image
                        st_image_robust(asset['file_path'], use_container_width=True)
                            
                        st.caption(f"📄 {asset['filename']}")
                        
                        # Actions
                        b1, b2 = st.columns(2)
                        # Reuse connection logic...
                        if b2.button("🗑️", key=f"del_v_{asset['id']}"):
                            st.session_state.db.delete_asset(asset['id'])
                            st.rerun()
        else:
             st.info("Vault is empty. Generate visuals or upload files.")

    # ==========================
    # TAB 3: ANALYTICS
    # ==========================
    with tab_analytics:
        st.header("📈 Growth Engine")
        
        col_act, col_stat = st.columns([1, 3])
        
        with col_act:
            st.info("""
            💡 **Simulator Mode Active**
            
            To unlock **Real-Time LinkedIn Metrics** (Live Likes, Views, and Comments), your account needs:
            1. **LinkedIn Marketing Developer Platform** approval.
            2. **Verified Business identity** (Personal accounts are API-restricted for metrics).
            
            *Currently displaying simulated performance data.*
            """)
            
            if st.button("🔄 Sync Live Metrics", help="Fetch latest likes/views from APIs"):
                from backend.analytics import AnalyticsSensor
                with st.spinner("Connecting to LinkedIn & Meta..."):
                    sensor = AnalyticsSensor()
                    count = sensor.sync_daily_metrics()
                    st.success(f"Database Updated! {count} posts synced.")
                    st.rerun()
            
            if st.button("🚀 Run Scheduler Cycle", help="Force check for and publish due posts"):
                from backend.worker import run_worker_cycle
                with st.spinner("Checking for due posts..."):
                    count = run_worker_cycle()
                    if count > 0:
                        st.success(f"Successfully processed {count} scheduled posts!")
                    else:
                        st.info("No posts are due for publishing right now.")
                    st.rerun()

        with col_stat:
            st.subheader("What's Working?")
            # Fetch directly using pandas for easy display
            conn = st.session_state.db.get_connection()
            try:
                # 1. Summary Metrics
                df_sums = pd.read_sql_query("""
                    SELECT 
                        SUM(likes) as total_likes, 
                        SUM(comments) as total_comments,
                        COUNT(*) as post_count
                    FROM posts WHERE status='posted'
                """, conn)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Likes", int(df_sums['total_likes'].iloc[0] or 0))
                m2.metric("Total Comments", int(df_sums['total_comments'].iloc[0] or 0))
                m3.metric("Posts Live", int(df_sums['post_count'].iloc[0] or 0))
                
                st.divider()

                # 2. Performance Table
                df_top = pd.read_sql_query("""
                    SELECT 
                        COALESCE(NULLIF(json_extract(content, '$.topic'), 'Topic'), 
                                 SUBSTR(json_extract(content, '$.linkedin_draft'), 1, 30) || '...') as Topic, 
                        likes as Likes, 
                        comments as Comments, 
                        engagement_rate as 'Engagement (%)',
                        platform as Platform
                    FROM posts 
                    WHERE status='posted' 
                    ORDER BY engagement_rate DESC 
                    LIMIT 10
                """, conn)
                
                if not df_top.empty:
                    st.dataframe(df_top, hide_index=True, use_container_width=True)
                else:
                    st.info("No posted content data available yet. Click 'Sync Live Metrics' to refresh.")
            except Exception as e:
                st.error(f"Error fetching analytics: {e}")
            finally:
                conn.close()
