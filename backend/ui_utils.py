import base64
import os
import streamlit as st

def get_base64_img(image_path):
    """
    Reads an image file and returns it as a Base64 data URL.
    This bypasses Streamlit's in-memory MediaFileStorage, making it
    immune to session clearing/server reloads that cause 'Missing file' errors.
    """
    if not image_path:
        return None
        
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        return None
        
    try:
        ext = os.path.splitext(abs_path)[1].lower().replace(".", "")
        if ext == "jpg": ext = "jpeg"
        
        with open(abs_path, "rb") as f:
            data = f.read()
            b64_str = base64.b64encode(data).decode()
            return f"data:image/{ext};base64,{b64_str}"
    except Exception as e:
        print(f"Error encoding image {abs_path}: {e}")
        return None

def st_image_robust(image_path, caption=None, width=None):
    """
    Renders an image robustly using Base64.
    """
    if str(image_path).startswith(("http://", "https://")):
        st.image(image_path, caption=caption, width=width)
        return

    b64_data = get_base64_img(image_path)
    if b64_data:
        st.image(b64_data, caption=caption, width=width)
    else:
        st.info("Image not found (Simulator/Placeholder)")
