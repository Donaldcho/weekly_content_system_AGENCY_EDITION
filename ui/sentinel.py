import streamlit as st
import pandas as pd
import time
from backend.sentinel_agent import SentinelAgent

def render_sentinel_page():
    # --- INIT ---
    if 'sentinel' not in st.session_state:
        st.session_state.sentinel = SentinelAgent()
        
    st.title("📡 The Sentinel")
    st.caption("AI-Powered Social Listening & Competitor Watch")

    # --- 1. KPI HEADER (Mock Real-Time) ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Share of Voice", "18.5%", "+2.1%")
    k2.metric("Brand Sentiment", "Positive", "85%")
    k3.metric("Competitor Alerts", "3 New", "High Urgency", delta_color="inverse")
    k4.metric("Trending Topics", "12 Active", "+4")
    
    st.divider()

    # --- 2. MAIN GRID ---
    col_intel, col_radar = st.columns([1.5, 1])

    # === LEFT: COMPETITOR INTEL ===
    with col_intel:
        st.subheader("🕵️ Competitor Omni-Watch")
        
        if st.button("🔄 Scan Competitor Networks"):
            with st.spinner("Intercepting public signals..."):
                time.sleep(1.5) # UX Delay
                alerts = st.session_state.sentinel.monitor_competitors()
                st.session_state.sentinel_alerts = alerts
                st.rerun()

        if 'sentinel_alerts' in st.session_state:
            for alert in st.session_state.sentinel_alerts:
                # Color code urgency
                urg = alert['urgency']
                border_color = "#E74C3C" if urg == "HIGH" else "#3498DB"
                icon = "🔥" if urg == "HIGH" else "ℹ️"
                
                with st.container(border=True):
                     c_a, c_b = st.columns([1, 4])
                     c_a.markdown(f"## {icon}")
                     c_a.caption(alert['timestamp'])
                     
                     c_b.markdown(f"**{alert['source']}** {alert['event']}")
                     st.progress(alert['impact_score']/100, f"Impact Potential: {alert['impact_score']}")

    # === RIGHT: TRENDS & SENTIMENT ===
    with col_radar:
        # A. TREND RADAR
        st.subheader("🌊 Trend Radar")
        trends = st.session_state.sentinel.fetch_trends()
        
        for t in trends:
            with st.expander(f"📈 {t['topic']} ({t['volume']})"):
                st.write(f"Growth: {t['growth']}")
                st.write(f"Relevance: {t['relevance']}")
                if st.button("⚡ Trendjack This", key=f"tj_{t['topic']}"):
                    # Automation Trigger
                    st.toast(f"Drafting content for '{t['topic']}'...")
                    # Ideally this would jump to Generator with topic pre-filled
        
        st.divider()
        
        # B. SENTIMENT LIVE STREAM
        st.subheader("❤️ Brand Heatmap")
        if st.button("🧠 Analyze Recent Mentions"):
             with st.spinner("Reading the internet..."):
                 results = st.session_state.sentinel.analyze_brand_mentions()
                 st.session_state.sent_results = results
        
        if 'sent_results' in st.session_state:
            # Simple Donut Chart replacement (Metrics)
            pos = len([x for x in st.session_state.sent_results if x['sentiment']=='POSITIVE'])
            neg = len([x for x in st.session_state.sent_results if x['sentiment']=='NEGATIVE'])
            
            c_s1, c_s2 = st.columns(2)
            c_s1.metric("Positivity", f"{pos}", "Mentions")
            c_s2.metric("Negativity", f"{neg}", "Mentions", delta_color="inverse")
            
            st.caption("Latest Mentions:")
            for m in st.session_state.sent_results[:3]:
                emoji = "✅" if m['sentiment'] == "POSITIVE" else "❌" if m['sentiment'] == "NEGATIVE" else "😐"
                st.text(f"{emoji} {m['user']}: {m['text'][:50]}...")
