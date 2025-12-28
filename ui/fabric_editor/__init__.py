import os
import streamlit.components.v1 as components

# Declare component
_component_func = components.declare_component(
    "fabric_editor",
    path=os.path.dirname(os.path.abspath(__file__))
)

def fabric_editor(layers, canvas_width=1080, canvas_height=1080, background_image=None, background_color="#FFFFFF", save_request_id=None, key=None):
    """
    Renders the Fabric.js editor.
    
    Args:
        layers (list): List of layer dicts.
        canvas_width (int): Canvas width.
        canvas_height (int): Canvas height.
        background_image (str): Data URL or Path (if handled) for bg.
        background_color (str): Hex color.
        save_request_id (str): ID to trigger snapshot.
        key (str): Streamlit key.
        
    Returns:
        dict: Updated visual state (or None if no change yet).
    """
    component_value = _component_func(
        layers=layers,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        background_image=background_image,
        background_color=background_color,
        save_request_id=save_request_id,
        key=key,
        default=None
    )
    return component_value
