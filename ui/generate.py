import streamlit as st
import os
import uuid
from datetime import datetime
from project_config import Config
from backend.content_generator import ContentGenerator
from backend.nano_banana import NanoBanana
from backend.ui_utils import st_image_robust
from ui.preview import render_mobile_preview
from backend.linkedin_poster import post_to_linkedin
from backend.linkedin_poster import post_to_linkedin
from backend.facebook_poster import post_to_facebook
from backend.compliance_guard import ComplianceGuard

def render_generate_page():
    st.header("✨ Weekly Content Generator")
    
    # Initialize Backends
    if 'content_gen' not in st.session_state:
        st.session_state.content_gen = ContentGenerator()
    if 'image_gen' not in st.session_state:
        st.session_state.image_gen = NanoBanana()
    if 'compliance_guard' not in st.session_state:
        st.session_state.compliance_guard = ComplianceGuard()
    
    # Update Generator with current Sidebar settings
    st.session_state.content_gen.company_info = st.session_state.brand_info
    
    # --- LOAD SAVED DRAFT UI ---
    with st.expander("📂 Load Saved Project", expanded=False):
        drafts = st.session_state.db.get_drafts()
        if drafts:
            # Display as a table-like structure
            for draft in drafts:
                c1, c2, c3 = st.columns([3, 1.5, 1])
                c1.markdown(f"**{draft['name']}**")
                c2.caption(f"Updated: {draft['updated_at']}")
                if c3.button("📂 Load", key=f"load_{draft['id']}"):
                    loaded_data = st.session_state.db.load_draft(draft['id'])
                    if loaded_data:
                        st.session_state.generated_plan = loaded_data
                        st.session_state.current_draft_id = draft['id'] # Track current loaded ID
                        st.toast(f"Project '{draft['name']}' Loaded!")
                        st.rerun()
                
                # Delete option
                if c3.button("🗑️", key=f"del_d_{draft['id']}"):
                    st.session_state.db.delete_draft(draft['id'])
                    st.rerun()
        else:
            st.info("No saved drafts found.")

    # --- SIDEBAR SETTINGS ---
    # Model Selection
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'gemini-2.0-flash-exp'
        
    with st.sidebar:
        st.markdown("### 🧠 AI Brain")
        selected_model = st.selectbox(
            "Content Model",
            options=["gemini-2.0-flash-exp", "gemini-flash-latest", "gemini-3-pro-preview"],
            index=0,
            key="model_selector",
            help="Flash for Speed. Pro for Reasoning."
        )
        st.session_state.model_name = selected_model
    
    # --- COMMAND BAR (Input) ---
    trends = "" # Default context
    use_rag = True # Default RAG state
    
    with st.container():
        st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
        c_mode, c_topic, c_btn = st.columns([1, 2, 0.8])
        
        with c_mode:
            campaign_type = st.selectbox("Campaign Strategy", ["Weekly Routine", "Product Launch", "Webinar Promo"], index=0, label_visibility="collapsed")
            use_rag = st.checkbox("Use RAG", value=True)
        
        with c_topic:
            core_topic = st.text_input("Topic", placeholder="Topic of the Week e.g. 'AI Trends'", label_visibility="collapsed")
            
        with c_btn:
            ignite_btn = st.button("✨ Ignite", type="primary", use_container_width=True)
        
        st.caption(f"⚡ Model: {st.session_state.model_name} | 📚 RAG: {'Active' if use_rag else 'Off'}")
        st.markdown('</div>', unsafe_allow_html=True)

        if ignite_btn:
            if not core_topic:
                st.warning("Please enter a core topic.")
            else:
                # Use st.status for real-time visibility
                with st.status("🚀 Agents Initializing...", expanded=True) as status:
                    st.write("📡 Connecting to AI Brain...")
                    
                    def update_status(msg):
                        status.write(msg)
                        # Optional: Log to console/terminal safely
                        try:
                            print(msg)
                        except UnicodeEncodeError:
                            print(msg.encode('ascii', 'ignore').decode('ascii'))

                    plan = st.session_state.content_gen.generate_weekly_plan(
                        core_topic, 
                        trends, 
                        model_name=st.session_state.model_name,
                        use_rag=use_rag,
                        campaign_type=campaign_type,
                        progress_callback=update_status
                    )
                    
                    status.update(label="✅ Mission Accomplished!", state="complete", expanded=False)
                
                st.session_state.generated_plan = plan
                # New generation clears current draft ID to ensure "Save" creates new or asks
                if 'current_draft_id' in st.session_state: del st.session_state.current_draft_id 
                st.toast("Weekly Plan Generated!", icon="🚀")
                st.success("Drafts generated successfully!")
    
    # Display Results
    if 'generated_plan' in st.session_state:
        
        # --- SAVE PROJECT UI ---
        col_s1, col_s2 = st.columns([3, 1])
        with col_s2:
            with st.popover("💾 Save Project"):
                save_name = st.text_input("Project Name", value=core_topic if core_topic else "New Project")
                if st.button("Confirm Save"):
                    # Use existing ID if updating, else new
                    d_id = st.session_state.get('current_draft_id', str(uuid.uuid4()))
                    
                    st.session_state.db.save_draft(
                        d_id,
                        save_name,
                        core_topic,
                        st.session_state.generated_plan
                    )
                    st.session_state.current_draft_id = d_id
                    st.toast("Project Saved!")
                    st.success(f"Saved as '{save_name}'")
        st.markdown("---")
        st.subheader("🗓️ Review & Edit Drafts")
        
        plan = st.session_state.generated_plan
        
        # SAFETY: Ensure plan is a list of dicts (Handle double-encoding or string storage bugs)
        if isinstance(plan, str):
            try:
                import json
                plan = json.loads(plan)
            except:
                st.error("Failed to parse plan data.")
                plan = []
        
        if isinstance(plan, list):
            # Check if items are strings (double encoded JSON inside list)
            new_plan = []
            for item in plan:
                if isinstance(item, str):
                    try:
                        import json
                        new_plan.append(json.loads(item))
                    except:
                        new_plan.append({"day": "Error", "linkedin_draft": "Data Error"})
                elif isinstance(item, dict):
                    new_plan.append(item)
            plan = new_plan
            st.session_state.generated_plan = plan # Update session state with clean data
        else:
            plan = [] 

        
        if not plan:
            st.info("No content plan available. Please generate one above.")
        else:
            # Tabs for each day
            tabs = st.tabs([d.get('day', f"Day {i+1}") for i, d in enumerate(plan)])
            
            for i, tab in enumerate(tabs):
                day_data = plan[i]
                with tab:

                    # Top Level Layout: Editor vs Preview
                    col_editor, col_preview = st.columns([1.5, 1])
                    
                    # --- LEFT: EDITOR ---
                    with col_editor:
                        st.markdown("### 🛠️ Content Studio")
                        
                        # Carousel Toggle
                        is_carousel = st.checkbox("🔄 Carousel Mode", key=f"car_mode_{i}", value=day_data.get('is_carousel', False))
                    day_data['is_carousel'] = is_carousel
                    
                    # 1. TEXT SECTION (Channel Toggles)
                    st.markdown("#### 📝 Content Workbench")
                    
                    # --- AGENT FEEDBACK ---
                    score = day_data.get('quality_score', 0)
                    if score > 0:
                        q_col1, q_col2 = st.columns([1, 4])
                        with q_col1:
                            st.metric("QA Score", f"{score}/10")
                        with q_col2:
                            if score < 10:
                                st.info(f"💡 **Editor's Critique**: {day_data.get('critique', 'No comments')}")
                            else:
                                st.success("🌟 Perfect score via Brand Voice!")
                    # ----------------------
                    
                    if not is_carousel:
                        # Channel Selector
                        channel = st.radio("Channel", ["LinkedIn", "Facebook"], horizontal=True, key=f"chan_{i}", label_visibility="collapsed")
                        
                        if channel == "LinkedIn":
                            val = st.text_area("LinkedIn Draft", value=day_data.get('linkedin_draft', ''), height=250, key=f"li_{i}")
                            plan[i]['linkedin_draft'] = val
                        else:
                            val = st.text_area("Facebook Draft", value=day_data.get('facebook_draft', ''), height=250, key=f"fb_{i}")
                            plan[i]['facebook_draft'] = val
                        
                        # --- COMPLIANCE AGENT ---
                        if st.button("🛡️ Scan Compliance", key=f"comp_check_{i}"):
                             # Determine content to scan
                             scan_txt = plan[i].get('linkedin_draft', '') if channel == "LinkedIn" else plan[i].get('facebook_draft', '')
                             if scan_txt:
                                 with st.spinner("🕵️ Compliance Agent is auditing your post..."):
                                    # Fetch DNA
                                    dna = st.session_state.db.get_brand_settings()
                                    report = st.session_state.compliance_guard.scan_post(scan_txt, dna)
                                    
                                    # Show Result
                                    if report['status'] == 'PASS':
                                        st.success(f"✅ Compliant (Score: {report['score']}/100)")
                                    elif report['status'] == 'WARN':
                                        st.warning(f"⚠️ Warning (Score: {report['score']}/100)")
                                    else:
                                        st.error(f"❌ COMPLIANCE FAIL (Score: {report['score']}/100)")
                                    
                                    # Details
                                    if report['issues']:
                                        with st.expander("Risk Report", expanded=True):
                                            for issue in report['issues']:
                                                st.write(f"- {issue}")
                             else:
                                 st.warning("Draft is empty.")
                            
                    else:
                        # Carousel Mode
                        if 'carousel_slides' not in day_data:
                            if st.button("⚡ Generate Carousel Slides", key=f"gen_car_{i}"):
                                with st.spinner("Slicing content into slides..."):
                                    slides = st.session_state.content_gen.generate_carousel_content(
                                        day_data['day'], 
                                        day_data.get('linkedin_draft', '')
                                    )
                                    day_data['carousel_slides'] = slides
                                    st.toast("Slides Sliced & Diced!", icon="🔪")
                                    st.rerun()
                            st.info("Click generate to convert draft to slides.")
                        else:
                            # Render Slides Editors
                            slides = day_data['carousel_slides']
                            for idx, slide in enumerate(slides):
                                with st.expander(f"Slide {idx+1}", expanded=True):
                                    slide['text'] = st.text_area("Text", value=slide['text'], height=80, key=f"s_txt_{i}_{idx}")
                                    slide['image_prompt'] = st.text_area("Prompt", value=slide['image_prompt'], height=60, key=f"s_prm_{i}_{idx}")

                    # 2. VISUAL SECTION
                    st.markdown("---")
                    st.markdown("#### 🍌 Nano Banana Vision")
                    
                    # Visual Source Selection
                    visual_source = st.radio(
                        "Source", 
                        ["Generate (Prompt)", "Vault (Saved Designs)", "Upload File (Bypass)", "Style Reference"],
                        horizontal=True,
                        key=f"viz_src_{i}"
                    )
                    
                    final_prompt = day_data.get('image_prompt', '')
                    ref_image_path = None
                    bypass_generation = False
                    
                    if visual_source == "Generate (Prompt)":
                        final_prompt = st.text_area("Prompt", value=final_prompt, height=80, key=f"img_p_{i}")
                    
                    elif visual_source == "Vault (Saved Designs)":
                        bypass_generation = True
                        from backend.vault import VaultManager
                        vault = VaultManager(Config().ASSETS_DIR + "/vault")
                        assets = vault.get_assets("image")
                        
                        if assets:
                            # Show grid or selectbox? Selectbox is easier for now
                            v_sel = st.selectbox("Select Design", [a['filename'] for a in assets], key=f"v_sel_{i}")
                            # Find path
                            for a in assets:
                                if a['filename'] == v_sel:
                                    day_data['image_path'] = a['path']
                                    st_image_robust(a['path'], width=200)
                                    break
                        else:
                            st.warning("Vault is empty. Go to Studio to create designs!")

                    elif visual_source == "Upload File (Bypass)":
                         # ... (Existing Upload Logic)
                        uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], key=f"up_{i}")
                        if uploaded_file:
                            # Save logic
                            save_dir = os.path.join(Config().ASSETS_DIR, "uploads")
                            os.makedirs(save_dir, exist_ok=True)
                            save_path = os.path.join(save_dir, uploaded_file.name)
                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            bypass_generation = True
                            day_data['image_path'] = save_path
                            st.toast(f"Uploaded: {uploaded_file.name}", icon="📁")
                            st.success(f"Uploaded: {uploaded_file.name}")

                    elif visual_source == "Style Reference":
                        final_prompt = st.text_area("Prompt (Modified by style)", value=final_prompt, height=80, key=f"img_p_ref_{i}")
                        
                        style_mode = st.radio("Reference Source", ["Select from Gallery", "Upload New"], horizontal=True, key=f"s_mode_{i}")
                        
                        if style_mode == "Select from Gallery":
                            # Load styles
                            from backend.vault import VaultManager
                            vault_styles = VaultManager(Config().ASSETS_DIR + "/vault")
                            styles = vault_styles.get_styles()
                            if styles:
                                selected_style = st.selectbox("Choose Style", styles, key=f"sel_sty_{i}")
                                ref_image_path = vault_styles.get_style_path(selected_style)
                                st_image_robust(ref_image_path, width=200)
                            else:
                                st.warning("No saved styles in Brand Center.")
                        else:
                            # Original Upload Logic
                            ref_file = st.file_uploader("Upload Style/Structure Ref", type=['png', 'jpg', 'jpeg'], key=f"up_ref_{i}")
                            if ref_file:
                                 # Save temp
                                save_dir = os.path.join(Config().ASSETS_DIR, "temp_refs")
                                os.makedirs(save_dir, exist_ok=True)
                                ref_image_path = os.path.join(save_dir, ref_file.name)
                                with open(ref_image_path, "wb") as f:
                                    f.write(ref_file.getbuffer())
                                st.caption("Reference loaded.")

                    # The Summon Button
                    if not bypass_generation:
                        # Label Logic
                        has_existing = False
                        if is_carousel and 'carousel_slides' in day_data:
                            has_existing = any(s.get('image_path') for s in day_data['carousel_slides'])
                        else:
                            has_existing = bool(day_data.get('image_path'))
                        
                        default_label = "✨ Design Carousel Visuals" if is_carousel else "✨ Summon Nano Banana"
                        regen_label = "🎲 Re-roll Visuals" if is_carousel else "🎲 Re-roll Visual"
                        btn_label = regen_label if has_existing else default_label
                        
                        if st.button(btn_label, key=f"btn_img_{i}", type="primary" if not has_existing else "secondary"):
                            with st.spinner("🎨 Nano Banana is painting..."):
                                if is_carousel and 'carousel_slides' in day_data:
                                    for idx, slide in enumerate(day_data['carousel_slides']):
                                        p_text = slide.get('image_prompt', '')
                                        img_path = st.session_state.image_gen.generate_image(p_text, reference_image_path=ref_image_path)
                                        if img_path: slide['image_path'] = img_path
                                    st.toast("Carousel Visuals Created!", icon="🍌")
                                    st.rerun()
                                else:
                                    img_path = st.session_state.image_gen.generate_image(final_prompt, reference_image_path=ref_image_path)
                                    if img_path: 
                                        day_data['image_path'] = img_path
                                        st.toast("Visual Masterpiece Created!", icon="🍌")
                                        st.rerun() 
                    else:
                        if st.button("🔄 Clear Upload", key=f"clr_up_{i}"):
                            day_data['image_path'] = None
                            st.rerun()

                # --- RIGHT: PREVIEW ---
                with col_preview:
                    st.markdown("### 📱 Mobile Preview")
                    
                    # Preview Controls
                    preview_platform = st.selectbox("Platform", ["LinkedIn", "Facebook"], key=f"prev_plat_{i}")
                    
                    # Prepare Data for Preview
                    prev_content = day_data.get('linkedin_draft', '') if preview_platform == "LinkedIn" else day_data.get('facebook_draft', '')
                    prev_img_path = day_data.get('image_path')
                    prev_slides = day_data.get('carousel_slides')
                    
                    # Extract Name safely
                    b_info = st.session_state.brand_info
                    b_name = b_info.get("name", "Deviceterra") if isinstance(b_info, dict) else b_info.split("\\n")[0].replace("Brand Name:", "").strip()

                    preview_html = render_mobile_preview(
                        platform=preview_platform,
                        brand_name=b_name,
                        content=prev_content,
                        image_path=prev_img_path,
                        is_carousel=is_carousel,
                        slides=prev_slides
                    )
                    
                    st.components.v1.html(preview_html, height=600, scrolling=True) 
                    
                    # --- INSTANT POSTING ACTION ---
                    st.markdown("---")
                    
                    # RBAC CHECK
                    current_role = st.session_state.get('current_user', {}).get('role', 'admin')
                    can_post = current_role in ['admin', 'editor']
                    
                    if can_post:
                        if preview_platform == "LinkedIn":
                            if st.button("🚀 Post Now to LinkedIn", key=f"post_btn_li_{i}", use_container_width=True):
                                with st.status("Posting to LinkedIn...", expanded=True) as status:
                                    success, result = post_to_linkedin(prev_content, image_path=prev_img_path)
                                    if success:
                                        status.update(label="✅ Posted Successfully!", state="complete")
                                        # Track in DB for analytics
                                        post_id = str(uuid.uuid4())
                                        new_post = {
                                            "id": post_id,
                                            "platform": "LinkedIn",
                                            "content": prev_content,
                                            "image_path": prev_img_path,
                                            "status": "posted",
                                            "topic": day_data.get('topic', 'Instant Post'),
                                            "scheduled_time": datetime.now().isoformat()
                                        }
                                        st.session_state.db.add_scheduled_post(new_post)
                                        st.session_state.db.mark_as_posted(post_id, social_id=result)
                                        st.success(f"Successfully posted! ID: {result}")
                                    else:
                                        status.update(label="❌ Posting Failed", state="error")
                                        st.error(f"Error: {result}")
                        else:
                             if st.button("🚀 Post Now to Facebook", key=f"post_btn_fb_{i}", use_container_width=True):
                                with st.status("Posting to Facebook Page...", expanded=True) as status:
                                    success, result = post_to_facebook(prev_content, image_path=prev_img_path)
                                    if success:
                                        status.update(label="✅ Posted to Facebook!", state="complete")
                                        post_id = str(uuid.uuid4())
                                        new_post = {
                                            "id": post_id,
                                            "platform": "Facebook",
                                            "content": prev_content,
                                            "image_path": prev_img_path,
                                            "status": "posted",
                                            "topic": day_data.get('topic', 'Instant Post'),
                                            "scheduled_time": datetime.now().isoformat()
                                        }
                                        st.session_state.db.add_scheduled_post(new_post)
                                        st.session_state.db.mark_as_posted(post_id, social_id=result)
                                        st.success(f"Successfully posted! ID: {result}")
                                    else:
                                        status.update(label="❌ Facebook Posting Failed", state="error")
                                        st.error(f"Error: {result}")
                    else:
                        st.info("🔒 Posting restricted to Editors/Admins. Please submit for review.")


        # Final Action Bar
        st.markdown("---")
        col_actions = st.columns([3, 1])
        with col_actions[1]:
            # Default to Multi (All connected platforms)
            target_platform = st.selectbox("Platform Target", ["Multi", "LinkedIn", "Facebook"], key="target_plat_bulk")
            
            # Button Label Logic
            c_role = st.session_state.get('current_user', {}).get('role', 'admin')
            btn_label = "📤 Submit for Review" if c_role == 'writer' else "📤 Send to Scheduler"
            
            if st.button(btn_label):
                for day_data in plan:
                    # Create a unique ID for each post
                    post_id = str(uuid.uuid4())
                    
                    # Prepare data object for DB
                    # If target is Facebook, use facebook_draft if available
                    content = day_data.get('linkedin_draft', '') 
                    if target_platform == "Facebook":
                        content = day_data.get('facebook_draft') or content

                    post_item = {
                        "id": post_id,
                        "platform": target_platform,
                        "status": "draft",
                        "topic": day_data.get('topic', 'Topic'),
                        "linkedin_draft": day_data.get('linkedin_draft', ''),
                        "facebook_draft": day_data.get('facebook_draft', ''),
                        "content": content, # Primary display content for scheduler preview
                        "image_path": day_data.get('image_path', ''),
                        "scheduled_time": None, # TBD in scheduler UI
                        "client_id": st.session_state.get('current_client_id', 1)
                    }
                    st.session_state.db.add_scheduled_post(post_item)
                    
                st.success(f"Drafts ({target_platform}) pushed to Scheduler! Go there to launch.")
