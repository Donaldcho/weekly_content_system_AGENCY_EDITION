import streamlit as st
import time

def render_launchpad_page():
    st.header("🚀 Agency Launchpad")
    st.markdown("Initialize your new brand from zero to hero using the Agency Swarm.")
    
    # Ensure Agency is initialized
    if 'agency' not in st.session_state and hasattr(st.session_state, 'generator'):
        st.session_state.agency = st.session_state.generator.agency
    
    # --- TABS ---
    tab_domain, tab_logo, tab_web = st.tabs(["🔍 Find Domain", "🎨 Design Logo", "🌐 Build Website"])
    
    # ---------------------------------------------------------
    # TAB 1: DOMAIN SEARCH
    # ---------------------------------------------------------
    with tab_domain:
        st.subheader("Domain Name Finder")
        col1, col2 = st.columns([3, 1])
        with col1:
            domain_topic = st.text_input("Describe your Business Idea", placeholder="e.g. Organic Coffee Subscription")
        with col2:
            st.write("") # Spacer
            st.write("") 
            if st.button("Find Domains", use_container_width=True, type="primary"):
                with st.spinner("🤖 Agency is brainstorming available domains..."):
                    results = st.session_state.agency.run_domain_search(domain_topic)
                    st.session_state.domain_results = results
        
        if 'domain_results' in st.session_state:
            st.success(f"Found {len(st.session_state.domain_results)} available names!")
            for d in st.session_state.domain_results:
                st.code(d, language="text")

    # ---------------------------------------------------------
    # TAB 2: LOGO STUDIO
    # ---------------------------------------------------------
    with tab_logo:
        st.subheader("Brand Identity Studio")
        
        # Load current brand info or defaults
        brand = st.session_state.get('brand_info', {})
        st.info(f"Designing for: **{brand.get('name', 'Unnamed Brand')}** ({brand.get('industry', 'General')})")
        
        if st.button("✨ Generate Vector Logo", type="primary"):
            with st.spinner("🎨 Designing SVG Logo..."):
                logo_data = st.session_state.agency.design_logo(brand)
                st.session_state.generated_logo = logo_data
        
        if 'generated_logo' in st.session_state:
            logo = st.session_state.generated_logo
            st.write(f"**Designer's Note:** {logo.get('reasoning')}")
            
            # Display SVG
            svg_code = logo.get('svg', '')
            st.image(svg_code, caption="Generated Vector Logo", width=300)
            
            # Download Button
            st.download_button(
                label="📥 Download SVG",
                data=svg_code,
                file_name="brand_logo.svg",
                mime="image/svg+xml"
            )

    # ---------------------------------------------------------
    # TAB 3: WEBSITE BUILDER
    # ---------------------------------------------------------
    with tab_web:
        st.subheader("Instant Landing Page")
        st.markdown("Generate a high-converting landing page based on your Strategy.")
        
        if st.button("🌐 Build Landing Page", type="primary"):
            # Mock Strategy Fetch (In real flow, we'd grab from Strategist)
            with st.spinner("🧠 Analyzing Strategy..."):
                 strategy_result = st.session_state.agency.create_strategy(
                     domain_topic if 'domain_topic' in locals() else brand.get('industry', 'Tech'), 
                     brand
                 )
            
            with st.spinner("👨‍💻 Coding HTML & Tailwind CSS..."):
                site_data = st.session_state.agency.build_website(
                    strategy_result, 
                    brand, 
                    brand.get('name', 'MyBrand')
                )
                st.session_state.generated_site = site_data
        
        if 'generated_site' in st.session_state:
            site = st.session_state.generated_site
            st.success("Website Generated!")
            
            tab_preview, tab_code = st.tabs(["Preview", "Code"])
            with tab_code:
                st.code(site.get('html'), language="html")
            with tab_preview:
                st.components.v1.html(site.get('html'), height=600, scrolling=True)
                
            st.download_button(
                label="📥 Download HTML",
                data=site.get('html'),
                file_name="index.html",
                mime="text/html"
            )
