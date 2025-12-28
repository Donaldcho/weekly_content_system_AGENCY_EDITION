import streamlit as st
import os
from project_config import Config
from backend.vault import VaultManager
from backend.rag import RAGEngine
from backend.ui_utils import st_image_robust

def render_vault_page():
    st.title("🗄️ The Vault")
    st.markdown("Manage your creative assets and Knowledge Base.")

    vault = VaultManager(Config().ASSETS_DIR + "/vault")
    rag = RAGEngine()

    # --- Header Actions ---
    col_h1, col_h2 = st.columns([3, 1])
    with col_h2:
        if st.button("🔄 Re-index Knowledge Base", help="Scan vault files and update AI context"):
            with st.spinner("Indexing documents..."):
                report = rag.ingest_vault()
            st.success(report)

    # --- Upload Section ---
    with st.expander("📤 Upload Assets", expanded=True):
        uploaded_file = st.file_uploader(
            "Drag and drop files here (Images, Videos, PDFs, Text)", 
            type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'pdf', 'txt', 'md'],
            accept_multiple_files=False # Keep simple for now
        )
        
        if uploaded_file:
            if st.button("Save to Vault"):
                path = vault.save_asset(uploaded_file, uploaded_file.name)
                if path:
                    st.success(f"Saved {uploaded_file.name}!")
                    st.rerun()
                else:
                    st.error("Failed to save file.")

    st.markdown("---")

    # --- Filter & Search ---
    col1, col2 = st.columns([3, 1])
    with col2:
        filter_type = st.selectbox("Type", ["All", "Images", "Videos"], index=0)
    
    backend_filter = None
    if filter_type == "Images":
        backend_filter = "image"
    elif filter_type == "Videos":
        backend_filter = "video"
        
    assets = vault.get_assets(backend_filter)
    
    st.subheader(f"Gallery ({len(assets)})")
    
    if not assets:
        st.info("No assets found. Upload some above!")
        return

    # --- Gallery Grid ---
    # Display in rows of 4
    cols = st.columns(4)
    for i, asset in enumerate(assets):
        col = cols[i % 4]
        with col:
            with st.container(border=True):
                if asset['type'] == 'image':
                    st_image_robust(asset['path'], use_container_width=True)
                else:
                    st.video(asset['path'])
                
                st.caption(f"**{asset['filename']}**")
                # st.caption(f"{asset['size'] // 1024} KB")
                
                if st.button("🗑️", key=f"del_{asset['filename']}", help="Delete asset"):
                    if vault.delete_asset(asset['filename']):
                        st.success("Deleted")
                        st.rerun()
                    else:
                        st.error("Error deleting")
