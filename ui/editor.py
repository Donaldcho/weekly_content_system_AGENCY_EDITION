import streamlit as st
import os
import uuid
import copy
import base64
from datetime import datetime
from PIL import Image

from project_config import Config
from backend.canvas_engine import CanvasEngine
from backend.vault import VaultManager
from backend.database import Database
from ui.fabric_editor import fabric_editor

def image_to_base64(image_path):
    """Encodes a local image to Base64 for HTML display."""
    if not os.path.exists(image_path): return None
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        return None

def safe_int(val, default=0):
    try: return int(val) if val is not None else default
    except: return default

def safe_float(val, default=0.0):
    try: return float(val) if val is not None else default
    except: return default

def safe_hex(val, default='#000000'):
    if not val or not isinstance(val, str): return default
    if not val.startswith("#"): return default
    if len(val) != 7: return default
    return val

def render_editor_page():
    st.markdown("## 🎨 Visual Studio Pro")
    
    # --- INIT STATE ---
    if 'canvas_state' not in st.session_state:
        st.session_state.canvas_state = {
            "bg_path": None,
            "layers": [],
            "canvas_width": 1080,
            "canvas_height": 1080
        }
    
    if 'selected_layer_id' not in st.session_state: st.session_state.selected_layer_id = None
    if 'last_synced_canvas' not in st.session_state: st.session_state.last_synced_canvas = None
    
    c_state = st.session_state.canvas_state

    # --- SYNC LOGIC (Pre-Render) ---
    if "fabric_canvas" in st.session_state and st.session_state["fabric_canvas"]:
        raw_update = st.session_state["fabric_canvas"]
        # Handle dict return
        updated_layers_early = raw_update.get("layers", []) if isinstance(raw_update, dict) else raw_update
        
        if updated_layers_early != st.session_state.last_synced_canvas:
            current_layer_map = {l["id"]: l for l in c_state["layers"]}
            for fl in updated_layers_early:
                 lid = fl["id"]
                 if lid in current_layer_map:
                     target = current_layer_map[lid]
                     # Merge props
                     target["x"] = fl.get("left", 0)
                     target["y"] = fl.get("top", 0)
                     target["opacity"] = fl.get("opacity", 1.0)
                     target["width"] = fl.get("width")
                     target["height"] = fl.get("height")
                     if fl["type"] == "text" or fl.get("type") == "textbox":
                         target["content"] = fl.get("content", "")
                         target["color"] = fl.get("color", "#000000")
                         target["size"] = fl.get("fontSize", 60) * fl.get("scaleY", 1)
            
            st.session_state.last_synced_canvas = copy.deepcopy(updated_layers_early)

    # --- LAYOUT SETUP ---
    col_tools, col_canvas, col_props = st.columns([1, 3, 1])

    # === 1. TOOL RACK (LEFT) ===
    with col_tools:
        st.subheader("🛠️ Tools")
        
        # Tool Buttons as Grid
        t1, t2 = st.columns(2)
        if t1.button("T", help="Add Text", use_container_width=True):
            c_state["layers"].append({
                "id": str(uuid.uuid4()), "type": "text", "content": "Headline", "x": 100, "y": 100, 
                "size": 60, "color": "#000000"
            })
            st.rerun()
            
        if t2.button("⬜", help="Add Shape", use_container_width=True):
             c_state["layers"].append({
                "id": str(uuid.uuid4()), "type": "shape", "shape_type": "rectangle", 
                "x": 200, "y": 200, "width": 200, "height": 200, "color": "#FFC300"
            })
             st.rerun()

        st.divider()
        st.caption("🍌 AI Studio")
        prompt = st.text_area("Background Prompt", "Cyberpunk city...")
        if st.button("Generate Art", use_container_width=True, type="primary"):
            with st.spinner("Dreaming..."):
                # Mock result
                st.session_state['editor_bg_url'] = "https://placehold.co/800x600/png?text=Cyberpunk"
                # If we had real backend, we'd save to temp file and set bg_path
                st.success("Generated!")

        st.divider()
        st.caption("Background")
        uploaded_bg = st.file_uploader("Upload BG", type=['png','jpg'], label_visibility="collapsed")
        if uploaded_bg:
            save_path = os.path.join(Config().ASSETS_DIR, "temp_bg_pro.png")
            with open(save_path, "wb") as f: f.write(uploaded_bg.getbuffer())
            if c_state.get("bg_path") != save_path:
                c_state["bg_path"] = save_path
                st.rerun()

    # === 2. THE STAGE (CENTER) ===
    with col_canvas:
        # Prepare Data for Fabric Component
        if "img_cache" not in st.session_state: st.session_state.img_cache = {}
        
        fabric_layers = []
        for l in c_state["layers"]:
            fl = copy.deepcopy(l)
            if l["type"] == "image":
                path = l.get("content")
                if path and os.path.exists(path):
                    if path not in st.session_state.img_cache:
                        st.session_state.img_cache[path] = image_to_base64(path)
                    fl["content"] = st.session_state.img_cache[path]
            fabric_layers.append(fl)

        # Handle Background
        bg_b64 = None
        if c_state.get("bg_path"):
            bgp = c_state["bg_path"]
            if os.path.exists(bgp):
                bg_b64 = image_to_base64(bgp)
        elif 'editor_bg_url' in st.session_state:
             # We can't easily pass URL to component if it expects base64 or strict path logic
             # For now, just show message
             st.caption("AI Background (Mock): " + st.session_state['editor_bg_url'])

        # Render Component
        updated_layers = fabric_editor(
            layers=fabric_layers,
            background_image=bg_b64,
            canvas_width=1080, # Virtual
            canvas_height=1080,
            save_request_id=st.session_state.get("save_request_id"),
            key="fabric_canvas"
        )
        
        # Save Handler
        if "fabric_canvas" in st.session_state:
             raw = st.session_state["fabric_canvas"]
             if isinstance(raw, dict) and raw.get("snapshot") and raw.get("save_id") == st.session_state.get("save_request_id"):
                  
                  # Decode
                  b64_str = raw["snapshot"].split(",")[1]
                  img_bytes = base64.b64decode(b64_str)
                  fname = f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                  save_path = os.path.join(Config().ASSETS_DIR, "vault", fname)
                  
                  # Save
                  os.makedirs(os.path.dirname(save_path), exist_ok=True)
                  with open(save_path, "wb") as f: f.write(img_bytes)
                  
                  # DB
                  if 'db' not in st.session_state: st.session_state.db = Database()
                  st.session_state.db.save_asset(fname, save_path, "design", "visual_studio")
                  
                  st.toast(f"Saved: {fname}")
                  st.session_state.save_request_id = None
                  st.rerun()

    # === 3. INSPECTOR (RIGHT) ===
    with col_props:
        st.subheader("⚙️ Props")
        
        # Layer Selector / List
        st.caption("Layers")
        for i, layer in enumerate(c_state["layers"]):
            is_sel = (layer["id"] == st.session_state.selected_layer_id)
            lbl = f"{layer['type']} {i}"
            if st.button(f"{'🔵' if is_sel else '⚪'} {lbl}", key=f"sel_{layer['id']}", use_container_width=True):
                st.session_state.selected_layer_id = layer["id"]
                st.rerun()
                
        st.divider()
        
        # Selected Props
        sel_layer = next((l for l in c_state["layers"] if l["id"] == st.session_state.selected_layer_id), None)
        if sel_layer:
            st.markdown(f"**Edit: {sel_layer['type']}**")
            
            if sel_layer['type'] == 'text':
                sel_layer['content'] = st.text_input("Text", sel_layer.get('content', ''))
                sel_layer['size'] = st.slider("Size", 10, 200, safe_int(sel_layer.get('size')))
                sel_layer['color'] = st.color_picker("Color", safe_hex(sel_layer.get('color')))
                
            elif sel_layer['type'] == 'shape':
                sel_layer['color'] = st.color_picker("Fill", safe_hex(sel_layer.get('color')))
                sel_layer['width'] = st.number_input("Width", 10, 1000, safe_int(sel_layer.get('width')))
                
            col_del, col_dupe = st.columns(2)
            if col_del.button("🗑️ Delete", type="primary"):
                 c_state["layers"].remove(sel_layer)
                 st.session_state.selected_layer_id = None
                 st.rerun()
                 
        else:
            st.info("Select a layer to edit.")

        st.divider()
        if st.button("💾 Save Image (PNG)", use_container_width=True):
             st.session_state.save_request_id = str(uuid.uuid4())
             st.rerun()
