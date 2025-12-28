import streamlit as st
import json
import os
from backend.brand_analyzer import BrandAnalyzer
from backend.vault import VaultManager
from project_config import Config
from backend.ui_utils import st_image_robust

def render_brand_page():
    # --- SETUP & STATE ---
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = BrandAnalyzer()
    
    vault_styles = VaultManager(Config().ASSETS_DIR + "/vault")
    
    # Load settings with defaults
    current_settings = st.session_state.db.get_brand_settings()
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
                        st.session_state.db.save_brand_settings(current_settings)
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
                            st.session_state.db.save_brand_settings(current_settings)
                            st.success("Tone extracted!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error reading file: {e}")

    st.markdown("---")

    # --- MAIN WORKSPACE (TABS) ---
    tab_id, tab_voice, tab_visual, tab_kb = st.tabs([
        "1. Who Are We? (Identity)", 
        "2. How We Sound (Voice)", 
        "3. How We Look (Visuals)", 
        "4. Knowledge Base"
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
            st.markdown("#### 🖌️ Art Direction")
            current_settings["visual_guidelines"] = st.text_area(
                "Visual Style Prompt", 
                value=current_settings.get("visual_guidelines", ""),
                height=150,
                placeholder="e.g. Minimalist, flat vector art, corporate memphis style, blue and white color scheme..."
            )
            
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

    # --- SAVE ACTION ---
    st.markdown("---")
    col_save, col_clear = st.columns([4, 1])
    with col_save:
        if st.button("💾 Save Brand Profile", type="primary", use_container_width=True):
            st.session_state.db.save_brand_settings(current_settings)
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
