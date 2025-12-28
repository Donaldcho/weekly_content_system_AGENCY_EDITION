import streamlit as st
import time
import uuid
import os
from backend.video_director import VideoDirector

def render_video_studio_page():
    if 'video_director' not in st.session_state:
        st.session_state.video_director = VideoDirector()
        
    st.title("🎬 AI Video Director")
    st.caption("Short-Form Video Production: Script-to-Storyboard")
    
    # --- SIDEBAR: OPEN PROJECT ---
    with st.sidebar:
        st.divider()
        st.header("📂 Open Project")
        drafts = st.session_state.db.get_drafts()
        
        if drafts:
            # Format: "Topic (YYYY-MM-DD)"
            options = {f"{d['topic']} ({str(d['updated_at'])[:10]})": d['id'] for d in drafts}
            
            selected_label = st.selectbox("Select saved video", [""] + list(options.keys()))
            
            if selected_label and selected_label != "":
                draft_id = options[selected_label]
                if st.button("📂 Load Selected", use_container_width=True):
                    loaded_data = st.session_state.db.load_draft(draft_id)
                    if loaded_data:
                        st.session_state.current_script = loaded_data
                        st.success("Loaded project!")
                        time.sleep(0.5)
                        st.rerun()

                st.divider()
                if st.button("🗑️ Delete Project", type="primary", use_container_width=True):
                    st.session_state.db.delete_draft(draft_id)
                    st.success(f"Deleted project: {selected_label}")
                    
                    # Clear current if it matches
                    if 'current_script' in st.session_state and st.session_state.current_script.get('id') == draft_id:
                        del st.session_state.current_script
                        
                    time.sleep(1)
                    st.rerun()

        else:
            st.caption("No saved projects found.")
    
    # --- 1. INPUT ---
    with st.expander("📝 Project Setup", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input("Video Topic", "The Future of AI Marketing")
        with col2:
            platform = st.selectbox("Format", ["TikTok", "IG Reels", "YouTube Shorts"])
            
        if st.button("✨ Roll Camera (Generate Script)"):
            with st.spinner("Writing viral script..."):
                script = st.session_state.video_director.generate_script(topic, platform)
                st.session_state.current_script = script
                st.rerun()

    # --- 2. WORKSPACE ---
    if 'current_script' in st.session_state:
        script = st.session_state.current_script
        
        # SAFETY: Ensure script is a dict (LLM sometimes returns a list of scenes)
        if isinstance(script, list):
            script = {
                "title": "Generated Draft",
                "scenes": script
            }
            st.session_state.current_script = script

        
        st.divider()
        # Header with Actions
        c_head, c_act = st.columns([3, 1])
        with c_head:
            st.subheader(f"Project: {script.get('title', 'Untitled')}")
        with c_act:
            if st.button("💾 Save Project"):
                # 1. Ensure ID
                if 'id' not in script:
                    script['id'] = str(uuid.uuid4())[:8]
                
                # 2. Save Draft
                # Using the existing DB save_draft
                st.session_state.db.save_draft(
                    draft_id=script['id'],
                    name=script.get('title', 'Untitled Video'),
                    topic=topic, # from input scope, might need to persist in script obj
                    plan_data=script
                )
                
                # 3. Save Assets to Vault
                scenes = script.get('scenes', [])
                count_assets = 0
                for scene in scenes:
                    if 'image_path' in scene:
                        # Logic to avoid duplicates? Simple verify
                        # For now, just save. Vault is a log.
                        fname = os.path.basename(scene['image_path'])
                        st.session_state.db.save_asset(
                            filename=fname,
                            file_path=scene['image_path'],
                            asset_type="storyboard_frame",
                            tags=f"video_project:{script['id']}"
                        )
                        count_assets += 1
                
                st.success(f"Project saved! ({count_assets} assets vaulted)")
        
        tab_editor, tab_board = st.tabs(["📝 Script Editor", "🎨 Storyboard"])
        
        # --- TAB 1: EDITOR ---
        with tab_editor:
            st.caption("Edit your script, voiceovers, and visual prompts here. Changes are saved automatically when you click 'Save Project'.")
            
            for i, scene in enumerate(script.get('scenes', [])):
                with st.expander(f"Scene {scene.get('id')} ({scene.get('section')})", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        # Audio
                        new_audio = st.text_area(
                            "🔈 Audio / Voiceover", 
                            value=scene.get('audio_voiceover', ''),
                            key=f"audio_{i}",
                            height=100
                        )
                        scene['audio_voiceover'] = new_audio
                        
                        # Overlay
                        new_text = st.text_input(
                            "📝 Text Overlay", 
                            value=scene.get('screen_text', ''),
                            key=f"text_{i}"
                        )
                        scene['screen_text'] = new_text
                        
                    with c2:
                        # Visual Prompt
                        new_visual = st.text_area(
                            "👁️ Visual Prompt (Image Gen)", 
                            value=scene.get('visual_description', ''),
                            key=f"visual_{i}",
                            height=150,
                            help="Describe what the AI should generate for this scene."
                        )
                        scene['visual_description'] = new_visual

        # --- TAB 2: STORYBOARD ---
        with tab_board:
            st.caption("Visualize your script with AI-generated keyframes.")
            
            # Action Button
            col_actions, _ = st.columns([1, 2])
            with col_actions:
                if st.button("🎨 Visualize Scenes (Generate images)", type="primary", use_container_width=True):
                    with st.spinner("Director is sketching keyframes..."):
                        updated_script = st.session_state.video_director.generate_storyboard(script)
                        st.session_state.current_script = updated_script
                        st.rerun()

            st.divider()

            # Display Images
            scenes = script.get('scenes', [])
            has_images = any('image_path' in s for s in scenes)
            
            if has_images:
                # Grid Layout for Storyboard
                cols = st.columns(3)
                for i, s in enumerate(scenes):
                    with cols[i % 3]:
                        if 'image_path' in s:
                            st.image(s['image_path'], caption=f"Scene {s['id']}", use_container_width=True)
                        else:
                            st.info(f"Scene {s['id']}: No image yet")
                            
                st.divider()
                if st.button("🚀 Render Final Video (Simulation)", use_container_width=True):
                     with st.status("Rendering video...", expanded=True) as status:
                        st.write("Composing frames...")
                        time.sleep(1)
                        st.write("Synthesizing voiceover (ElevenLabs)...")
                        time.sleep(1)
                        st.write("Syncing audio...")
                        time.sleep(1)
                        status.update(label="✅ Render Complete!", state="complete")
                        st.success("Video exported to Vault!")
                        st.balloons()
            else:
                st.info("No images generated yet. Click 'Visualize Scenes' to start.")
