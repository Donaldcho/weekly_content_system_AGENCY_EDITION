import streamlit as st
import time
import os
from project_config import Config
from backend.vault import VaultManager
from backend.ui_utils import st_image_robust

def render_repurpose_page():
    st.title("🚀 content Multiplier")
    st.markdown("One Idea. Everywhere.")
    
    col1, col2 = st.columns([1, 1])
    
    # Initialize variables to ensure scope safety
    topic = ""
    source_text = ""
    multiplier_btn = False
    
    with col1:
       # --- INPUT SECTION (Blaze Card) ---
        st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 0.5])
        with c1:
            topic = st.text_input("Source Topic / Content", placeholder="Paste a blog, URL, or idea...", label_visibility="collapsed")
        with c2:
            multiplier_btn = st.button("🚀 Multiply", type="primary", use_container_width=True)
        
        # Re-introducing source_text as it was likely an oversight in the provided snippet
        source_text = st.text_area("Source Material (Optional)", placeholder="Paste a blog post, newsletter, or rough thoughts here...", height=250)
        
        st.caption("Distribution Matrix: 6 Channels")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.info("💡 **Pro Tip**: Paste your raw notes or a URL summary on the left. We'll turn it into a LinkedIn Post, a Twitter Thread, and an Instagram Visual automatically.")
        
    if multiplier_btn and topic:
        with st.spinner("Analyzing semantics... rewriting for platforms..."):
            campaign = st.session_state.content_gen.generate_campaign(topic, source_text)
            
            if campaign:
                st.session_state.latest_campaign = campaign
                st.success("Campaign Generated!")
            else:
                st.error("Failed to generate campaign. Try again.")

    st.markdown("---")
    
    # Display Results
    if 'latest_campaign' in st.session_state:
        c = st.session_state.latest_campaign
        
        # --- OUTPUT MATRIX (Grid Layout) ---
        st.markdown("### 📡 Distribution Matrix")
        
        # Row 1: Social Core (LinkedIn, X, Insta)
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        
        with r1_c1: # LinkedIn
            st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
            st.markdown("#### 🔵 LinkedIn")
            st.text_area("Authority Post", value=c.get('linkedin', {}).get('text', ''), height=200, key="li_txt")
            st.button("📋 Copy", key="cp_li")
            st.markdown('</div>', unsafe_allow_html=True)

        with r1_c2: # Twitter
            st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
            st.markdown("#### ⚫ X Thread")
            tweets = c.get('twitter', [])
            tweet_txt = "\n\n".join([t.get('tweet', '') for t in tweets])
            st.text_area("Thread", value=tweet_txt, height=200, key="tw_txt")
            st.button("📋 Copy", key="cp_tw")
            st.markdown('</div>', unsafe_allow_html=True)

        with r1_c3: # Instagram
            st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
            st.markdown("#### 🟣 Instagram")
            st.text_area("Caption", value=c.get('instagram', {}).get('caption', ''), height=100, key="ig_cap")
            
            # Visual Mini-Studio (Simplified for Grid)
            viz_src = st.radio("Visual", ["Generate", "Vault"], horizontal=True, label_visibility="collapsed", key="v_src_mini")
            if viz_src == "Generate":
                 path = c.get('instagram', {}).get('image_path')
                 if path:
                      st_image_robust(path, use_container_width=True)
                 
                 if st.button("✨ Paint", key="paint_mini"):
                     p = c.get('instagram', {}).get('image_prompt', '')
                     path = st.session_state.image_gen.generate_image(p)
                     # Persist
                     if 'instagram' not in c: c['instagram'] = {}
                     c['instagram']['image_path'] = path
                     st.rerun()
            
            if viz_src == "Vault":
                 # Simple Vault Picker
                 vault = VaultManager(Config().ASSETS_DIR + "/vault")
                 assets = vault.get_assets("image")
                 if assets:
                     s = st.selectbox("Select", [a['filename'] for a in assets], key="v_sel_mini")
                     # render (omitted for brevity in grid)
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 2: Extended Reach (Email, TikTok, FB)
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        
        with r2_c1: # Newsletter
            st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
            st.markdown("#### 📧 Newsletter")
            nl = c.get('newsletter', {})
            st.text_input("Subject", value=nl.get('subject', ''))
            st.text_area("Body", value=nl.get('body', ''), height=150)
            st.markdown('</div>', unsafe_allow_html=True)

        with r2_c2: # TikTok
            st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
            st.markdown("#### 🎵 TikTok Script")
            st.text_area("Script", value=c.get('tiktok', {}).get('script', ''), height=220)
            st.markdown('</div>', unsafe_allow_html=True)

        with r2_c3: # Facebook
             st.markdown('<div class="blaze-card">', unsafe_allow_html=True)
             st.markdown("#### 📘 Facebook")
             st.text_area("Post", value=c.get('facebook', {}).get('post', ''), height=220)
             st.markdown('</div>', unsafe_allow_html=True)
