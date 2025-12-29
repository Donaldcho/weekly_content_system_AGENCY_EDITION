import streamlit as st
import json
import os
from backend.brand_analyzer import BrandAnalyzer
from backend.vault import VaultManager
from project_config import Config
from backend.ui_utils import st_image_robust
from backend.template_manager import TemplateManager
from backend.content_generator import ContentGenerator
from backend.adk.main import MarketingAgency # For Visual Agent
from backend.nano_banana import NanoBanana # For Preview Generation
import time # Ensure this is present for sleep calls

def render_brand_page():
    # --- SETUP & STATE ---
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = BrandAnalyzer()
    
    vault_styles = VaultManager(Config().ASSETS_DIR + "/vault")
    # Initialize Template Manager with DB
    template_manager = TemplateManager(st.session_state.db, vault_styles)
    
    st.header("🧬 Brand Identity & Knowledge Base")
    st.caption("Define your brand's DNA. The AI uses this to generate on-brand content.")
    
    # Client Context
    current_client_id = st.session_state.get('current_client_id', 1)

    # --- 1. LOAD DATA ---
    current_settings = st.session_state.db.get_brand_settings(client_id=current_client_id)
    if isinstance(current_settings, str): # Legacy fallback
         try: current_settings = json.loads(current_settings)
         except: current_settings = {}
         
    # --- 2. MAIN TABS ---
    # --- 2. MAIN TABS ---
    # Tabs are defined below to wrap the main content area

    
    # ... (Keep Tabs 1-4 existing logic - re-inserting simplified for replacement target matching if needed, 
    # but I will target specific blocks to avoid huge replacement)
    
    # actually I need to replace the whole beginning to inject the import properly, 
    # or I can use multi-replace.
    # Let's try replacing just the top imports and setup, then append the tab logic.
    # But the tabs are defined in a 'with' block usually? No, st.tabs returns list.
    
    # Wait, I need to see where 'tabs' variable is defined in the original file.
    # It was not shown in the previous view (lines 1-15).
    # I need to find the `tab_core, ... = st.tabs([...])` line.

    
    # Load settings with defaults
    current_client_id = st.session_state.get('current_client_id', 1)
    current_settings = st.session_state.db.get_brand_settings(client_id=current_client_id)
    if isinstance(current_settings, str): current_settings = {} # Handle legacy
    
    # Default Defaults
    defaults = {
        "name": "", "industry": "", "mission": "", "tone": "Professional",
        "s_formal": 50, "s_humor": 50, "s_edgy": 50, "s_concise": 50,
        "colors": ["#000000"], "visual_guidelines": "", "golden_samples": [],
        "anti_patterns": [], "voice_profile": {}
    }
    # Merge defaults
    for k, v in defaults.items():
        if k not in current_settings: current_settings[k] = v

    # --- TITLE & HEADER ---
    st.title("🧬 Brand Identity")
    st.caption("Teach the AI who you are. This 'DNA' controls every post generated.")

    # --- ⚡ QUICK START (AUTO-MAGIC) ---
    with st.expander("✨ Quick Start: Auto-Fill from Website or File", expanded=False):
        c_auto1, c_auto2 = st.columns(2)
        with c_auto1:
            st.markdown("##### 🌐 From Website")
            url_input = st.text_input("Website URL", placeholder="https://yourbrand.com")
            if st.button("🚀 Analyze Site", use_container_width=True):
                with st.spinner("Reading your digital mind..."):
                    res = st.session_state.analyzer.analyze_website(url_input)
                    if "error" not in res:
                        # Map results to settings
                        ident = res.get("identity", {})
                        voice_vec = res.get("voice", {}).get("tone_vectors", {})
                        
                        current_settings.update({
                            "name": ident.get("name", ""),
                            "mission": ident.get("mission", ""),
                            "industry": "Tech/AI", # Basic inference
                            "s_formal": int(voice_vec.get("formality", 0.5) * 100),
                            "s_humor": int(voice_vec.get("humor", 0.5) * 100),
                            "s_edgy": int(voice_vec.get("edginess", 0.5) * 100)
                        })
                        st.session_state.db.save_brand_settings(current_settings, client_id=current_client_id)
                        st.success("Brand extracted!")
                        st.rerun()
                    else:
                        st.error(res["error"])

        with c_auto2:
            st.markdown("##### 📄 From Document")
            up_doc = st.file_uploader("Upload Guidelines (PDF/TXT)", type=['pdf', 'txt', 'md'])
            if up_doc and st.button("🧠 Extract DNA"):
                with st.spinner("Analyzing document..."):
                    # Simple text extraction for now
                    try:
                        text_content = up_doc.read().decode("utf-8", errors='ignore')
                        res = st.session_state.analyzer.analyze_document(text_content)
                        if "error" not in res:
                            aud = res.get("audience", {})
                            voice = res.get("voice", {})
                            current_settings["target_audience"] = aud.get("persona", "")
                            current_settings["tone"] = ", ".join(voice.get("adjectives", []))
                            st.session_state.db.save_brand_settings(current_settings, client_id=current_client_id)
                            st.success("Tone extracted!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error reading file: {e}")

    st.markdown("---")

    # --- MAIN WORKSPACE (TABS) ---
    tab_id, tab_voice, tab_visual, tab_kb, tab_templates = st.tabs([
        "1. Who Are We? (Identity)", 
        "2. How We Sound (Voice)", 
        "3. How We Look (Visuals)", 
        "4. Knowledge Base",
        "5. 🖼️ Prompt Templates"
    ])

    # === TAB 1: IDENTITY ===
    with tab_id:
        c1, c2 = st.columns([2, 1])
        with c1:
            current_settings["name"] = st.text_input("Brand Name", value=current_settings.get("name"))
            current_settings["industry"] = st.text_input("Industry / Niche", value=current_settings.get("industry"))
            current_settings["target_audience"] = st.text_area("Target Audience", value=current_settings.get("target_audience"), height=70, help="Who are we talking to?")
            current_settings["mission"] = st.text_area("Mission Statement", value=current_settings.get("mission"), height=100)
            
            if st.button("✨ AI Polish Mission", help="Rewrite your mission to sound more professional"):
                 with st.spinner("Polishing..."):
                     # Quick call to analyzer for just text polish
                     polished = st.session_state.analyzer.build_professional_profile(current_settings)
                     if "mission" in polished:
                         current_settings["mission"] = polished["mission"]
                         st.session_state.db.save_brand_settings(current_settings)
                         st.rerun()

        with c2:
            st.info("💡 **Tip:** A clear mission helps the AI stay on topic.")
            st.markdown(f"**Current Identity:**\n\n*{current_settings.get('name') or 'Unnamed'}*\n\n{current_settings.get('mission') or 'No mission yet.'}")

    # === TAB 2: VOICE ===
    with tab_voice:
        st.markdown("#### 🎚️ Personality Sliders")
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            current_settings["s_formal"] = st.slider("Formal ↔ Casual", 0, 100, current_settings.get("s_formal"))
            current_settings["s_humor"] = st.slider("Serious ↔ Fun", 0, 100, current_settings.get("s_humor"))
        with c_v2:
            current_settings["s_edgy"] = st.slider("Safe ↔ Edgy", 0, 100, current_settings.get("s_edgy"))
            current_settings["s_concise"] = st.slider("Detailed ↔ Concise", 0, 100, current_settings.get("s_concise"))

        st.markdown("---")
        st.markdown("#### 🧠 Deep Voice Cloning")
        st.caption("Paste your best posts here. The AI will analyze your sentence structure and vocabulary to sound exactly like you.")
        
        # Golden Samples
        current_samples = "\n\n".join(current_settings.get("golden_samples", []))
        samples_input = st.text_area("Your Best Content (Paste 3-5 posts)", value=current_samples, height=150)
        
        col_act_v1, col_act_v2 = st.columns([1, 3])
        if col_act_v1.button("🧬 Learn My Style"):
             if samples_input:
                 with st.spinner("Decoding linguistic DNA..."):
                     res = st.session_state.analyzer.analyze_style(samples_input)
                     if "error" not in res:
                         current_settings["voice_profile"] = res.get("voice_profile")
                         current_settings["anti_patterns"] = res.get("anti_patterns")
                         current_settings["golden_samples"] = [samples_input]
                         st.session_state.db.save_brand_settings(current_settings)
                         st.success("Style learned!")
                     else:
                         st.error(res["error"])
        
        with st.expander("Advanced: Anti-Patterns (What NOT to say)"):
            anti_text = "\n".join(current_settings.get("anti_patterns", []))
            new_anti = st.text_area("Banned Phrases/Habits (One per line)", value=anti_text)
            current_settings["anti_patterns"] = [line.strip() for line in new_anti.split("\n") if line.strip()]

    # === TAB 3: VISUALS ===
    with tab_visual:
        c_vis1, c_vis2 = st.columns(2)
        
        with c_vis1:
            st.markdown("#### 🎨 Color Palette")
            # Simple color picker loop
            colors = current_settings.get("colors", [])
            # Ensure at least one
            if not colors: colors = ["#000000"]
            
            cols_pick = st.columns(4)
            for i in range(4):
                with cols_pick[i]:
                    val = colors[i] if i < len(colors) else "#FFFFFF"
                    new_val = st.color_picker(f"Color {i+1}", val, key=f"cp_{i}")
                    if i < len(colors): colors[i] = new_val
                    elif new_val != "#FFFFFF": colors.append(new_val) # Append new if changed
            
            current_settings["colors"] = colors

            st.markdown("#### 🖼️ Watermark Logo")
            watermark_file = st.file_uploader("Upload Transparent PNG", type=['png'])
            if watermark_file:
                save_path = os.path.join(Config().ASSETS_DIR, "brand_logo.png")
                with open(save_path, "wb") as f:
                    f.write(watermark_file.read())
                st.success("Watermark updated!")

        with c_vis2:
            st.markdown("#### 🖌️ Art Direction (Style DNA)")
            
            # Ensure visual_styles dict exists
            if "visual_styles" not in current_settings:
                current_settings["visual_styles"] = {}
                
            # Style Editor
            presets = ["Minimalist", "Cyberpunk", "Editorial", "Organic", "Corporate"]
            existing_styles = list(current_settings["visual_styles"].keys())
            
            # Combine and unique, plus "Create New" option
            all_styles_options = sorted(list(set(presets + existing_styles)))
            all_styles_options.insert(0, "➕ Create New Style")
            
            # Selector
            edit_style = st.selectbox("Select Style to Train", all_styles_options, key="style_edit_sel")
            
            target_style_key = edit_style
            
            if edit_style == "➕ Create New Style":
                new_style_name = st.text_input("New Style Name", placeholder="e.g. Retro Wave 80s")
                if new_style_name:
                    target_style_key = new_style_name.strip()
                else:
                    target_style_key = None # Block editing until name provided
            
            if target_style_key:
                # Get current value (handle both legacy string and new dict)
                raw_val = current_settings["visual_styles"].get(target_style_key, "")
                
                # Normalize to object
                if isinstance(raw_val, dict):
                    current_style_obj = raw_val
                    current_prompt = current_style_obj.get("prompt", "")
                else:
                    current_style_obj = {"prompt": str(raw_val)}
                    current_prompt = str(raw_val)
                
                # Layout: Preview Image | Editor
                col_sty_img, col_sty_edit = st.columns([1, 2])
                
                with col_sty_img:
                    preview_path = current_style_obj.get("preview_image")
                    if preview_path and os.path.exists(preview_path):
                        st.image(preview_path, caption=f"Preview: {target_style_key}", width="stretch")
                    else:
                        st.info("No Preview Image")
                        
                with col_sty_edit:
                    new_promt = st.text_area(
                        f"Prompt Guidelines for '{target_style_key}'", 
                        value=current_prompt,
                        height=150,
                        placeholder=f"Describe exactly how {target_style_key} looks for your brand..."
                    )

                # --- VARIANTS ---
                with st.expander("🧩 Style Variants"):
                    variants = current_style_obj.get("variants", [])
                    
                    # Add Variant
                    c_v1, c_v2, c_v3 = st.columns([2, 3, 1])
                    v_name = c_v1.text_input("Name", key=f"v_n_{target_style_key}")
                    v_p = c_v2.text_input("Modifier", key=f"v_p_{target_style_key}")
                    if c_v3.button("Add", key=f"v_btn_{target_style_key}"):
                        if v_name and v_p:
                            variants.append({"name": v_name, "prompt": v_p})
                            current_style_obj["variants"] = variants
                            current_style_obj["prompt"] = new_promt # Sync
                            current_settings["visual_styles"][target_style_key] = current_style_obj
                            st.rerun()
                    
                    if variants:
                        for v in variants:
                            st.caption(f"• **{v['name']}**: {v['prompt']}")

                if new_promt != current_prompt:
                    current_style_obj["prompt"] = new_promt
                    current_style_obj["variants"] = variants
                    current_settings["visual_styles"][target_style_key] = current_style_obj
                    st.caption("⚠️ Change pending save (Click 'Save Brand Profile' below)")
                
                # --- VISUALIZATION / TEST ---
                if st.button(f"🎨 Visualize Style: {target_style_key}", help="Generate a test image to see how this style looks."):
                    if not new_promt:
                        st.error("Please define the style prompt first.")
                    else:
                        with st.spinner(f"Agent designing & rendering '{target_style_key}' preview..."):
                            # 1. Init Agency & Generator
                            agency = MarketingAgency()
                            gen = ContentGenerator(client_id=current_client_id)
                            
                            # 2. Mock Brand Info
                            test_brand_info = current_settings.copy()
                            # Ensure we pass the simplified dict structure if the agent expects it, 
                            # or just pass the full object if we updated the agent. 
                            # We updated agent to handle dicts.
                            if "visual_styles" not in test_brand_info: test_brand_info["visual_styles"] = {}
                            
                            # Pass the temp object
                            temp_style_obj = current_style_obj.copy()
                            temp_style_obj["prompt"] = new_promt
                            test_brand_info["visual_styles"][target_style_key] = temp_style_obj
                            
                            # 3. Generate Prompt (Agent)
                            vis_res = agency.generate_visual(
                                topic="Visual Identity Preview", 
                                title="PREVIEW", 
                                style_preset=target_style_key, 
                                brand_info=test_brand_info
                            )
                            smart_prompt = vis_res.get('image_prompt', '')
                            
                            
                            if smart_prompt:
                                # 4. Generate Image (Switched to NanoBanana / Gemini 2.0)
                                st.caption(f"**Agent Generated Prompt:**\n*{smart_prompt}*")
                                
                                # Use NanoBanana (Pro Tier)
                                nb = NanoBanana(tier="Pro")
                                # Filename only, path handled inside
                                fname = "preview_style_" + target_style_key.replace(" ", "_").lower() + ".png"
                                # NanoBanana expects prompt, optional filename. It returns full path.
                                img_path = nb.generate_image(smart_prompt, fname)
                                
                                # 5. Display & Save
                                if img_path and os.path.exists(img_path):
                                    # Fix: Streamlit new version requires explicit string or int, None is invalid.
                                    # 'stretch' mimics use_container_width=True
                                    st.image(img_path, caption=f"Style: {target_style_key}", width="stretch") 
                                    
                                    # Update Preview in Object
                                    current_style_obj["preview_image"] = img_path
                                    current_style_obj["prompt"] = new_promt
                                    current_settings["visual_styles"][target_style_key] = current_style_obj
                                    
                                    st.success("Preview generated! Saving as Style Cover Image...")
                                    st.session_state.db.save_brand_settings(current_settings, client_id=current_client_id)
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Image generation failed.")
                            else:
                                st.error("Agent failed to generate prompt.")
            
            # Preview Watermark
            logo_path = os.path.join(Config().ASSETS_DIR, "brand_logo.png")
            if os.path.exists(logo_path):
                st.caption("Current Watermark:")
                st_image_robust(logo_path, width=100)

    # === TAB 4: KNOWLEDGE ===
    with tab_kb:
        st.info("📂 Upload PDFs, Text files, or Markdown documents about your company. The AI will read these to be factually accurate.")
        
        col_kb1, col_kb2 = st.columns([3, 1])
        with col_kb1:
             new_files = st.file_uploader("Upload Documents", type=['pdf', 'txt', 'md'], accept_multiple_files=True)
             if new_files and st.button("📥 Ingest Documents"):
                 vault_dir = os.path.join(Config().ASSETS_DIR, "vault")
                 os.makedirs(vault_dir, exist_ok=True)
                 for f in new_files:
                     path = os.path.join(vault_dir, f.name)
                     with open(path, "wb") as dest:
                         dest.write(f.getbuffer())
                 st.success(f"Uploaded {len(new_files)} documents.")
        
        with col_kb2:
            if st.button("🔄 Re-Index Brain", help="Process uploaded files so the AI can read them."):
                with st.spinner("Reading & Indexing..."):
                    from backend.rag import RAGEngine
                    rag = RAGEngine()
                    rep = rag.ingest_vault()
                    st.success("Brain Updated!")
                    st.json(rep)

    # === TAB 5: PROMPT TEMPLATES ===
    with tab_templates:
        st.info("🖼️ Define standard visual prompts or patterns for this brand.")
        
        # 1. New Template Form
        if 'new_tpl_desc' not in st.session_state: st.session_state.new_tpl_desc = ""
        
        with st.expander("➕ Add New Template", expanded=False):
            # We need to use session state for the description to allow auto-fill update
            
            # We move the uploader OUTSIDE the form so we can access the file immediately for extraction
            t_img = st.file_uploader("Reference Image (Optional)", type=['png', 'jpg'])
            
            # Helper for Extraction (Now visible immediately after upload)
            if t_img:
                if st.button("✨ Extract Style from Image"):
                    with st.spinner("Analyzing visual DNA..."):
                        # Save temp
                        temp_path = os.path.join(Config().ASSETS_DIR, "temp_style_analysis.png")
                        with open(temp_path, "wb") as f: f.write(t_img.getbuffer())
                        
                        # Analyze
                        gen = ContentGenerator(client_id=current_client_id)
                        style_desc = gen.analyze_image_style(temp_path)
                        
                        st.session_state.new_tpl_desc = style_desc
                        st.toast("Style extracted! Check description.", icon="🧠")
                        st.rerun()

            with st.form("new_tpl_form"):
                t_name = st.text_input("Template Name", placeholder="e.g. LinkedIn Carousel Style")
                
                t_desc = st.text_area("Prompt / Description", value=st.session_state.new_tpl_desc, placeholder="Describe the visual style, camera angle, lighting...", height=100)
                
                if st.form_submit_button("Save Template"):
                    if t_name and t_desc:
                        template_manager.add_template(t_name, t_desc, t_img, client_id=current_client_id)
                        st.session_state.new_tpl_desc = "" # Clear
                        st.success(f"Added template: {t_name}")
                        st.rerun()
                    else:
                        st.error("Name and Description required.")
            


        # 2. List Templates
        templates = template_manager.get_templates(client_id=current_client_id)
        
        if templates:
            st.divider()
            st.markdown(f"**Saved Templates ({len(templates)})**")
            
            for tpl in templates:
                with st.container():
                    c_img, c_info, c_act = st.columns([1, 3, 1])
                    with c_img:

                        if tpl.get('image'):
                            # Styles are saved in a sibling 'styles' folder by VaultManager
                            # We can rely on VaultManager helper or manual construction
                            # Manual: styles_dir is sibling to vault
                            styles_dir = os.path.join(Config().ASSETS_DIR, "styles")
                            img_path = os.path.join(styles_dir, tpl['image'])
                            
                            if os.path.exists(img_path):
                                st.image(img_path, use_container_width=True)
                            else:
                                st.warning("Img Missing")
                        else:
                             st.markdown("🖼️")
                    with c_info:
                        st.subheader(tpl['name'])
                        st.caption(tpl['description'])
                    with c_act:
                        if st.button("🗑️", key=f"del_{tpl['id']}", help="Delete Template"):
                            template_manager.delete_template(tpl['id'], client_id=current_client_id)
                            st.rerun()
                    st.divider()
        else:
            st.caption("No templates found. Add one above!")

    # --- SAVE ACTION ---
    st.markdown("---")
    col_save, col_clear = st.columns([4, 1])
    with col_save:
        if st.button("💾 Save Brand Profile", type="primary", use_container_width=True):
            st.session_state.db.save_brand_settings(current_settings, client_id=current_client_id)
            st.balloons()
            st.toast("Brand DNA Saved Successfully!", icon="🧬")
            
    with col_clear:
        if st.button("🗑️ Reset", use_container_width=True):
            st.warning("Refresh page to clear unsaved inputs.")

    # --- PREVIEW SIDEBAR (Always Visible Context) ---
    with st.sidebar:
        st.markdown("### 🎫 Brand Passport")
        st.markdown(f"**{current_settings.get('name') or 'Unnamed Brand'}**")
        st.caption(current_settings.get('industry') or "Industry N/A")
        
        # Visual Swatches
        cols = st.columns(5)
        for i, c in enumerate(current_settings.get("colors", [])[:5]):
            cols[i].markdown(f'<div style="background:{c};height:20px;border-radius:3px;"></div>', unsafe_allow_html=True)
            
        st.divider()
        st.markdown("**Voice Vibe**")
        st.progress(current_settings.get("s_formal", 50)/100, "Formal")
        st.progress(current_settings.get("s_humor", 50)/100, "Fun")
        
        if current_settings.get("voice_profile"):
            st.success("✅ Deep Style Cloned")
        else:
            st.info("ℹ️ Standard Voice")
            
        # Download
        st.download_button(
            "📥 Export Brand Guidelines", 
            data=json.dumps(current_settings, indent=2), 
            file_name="brand_dna.json", 
            mime="application/json",
            use_container_width=True
        )
