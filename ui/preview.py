import streamlit as st
import base64
import os

def get_image_base64(image_path):
    """Encodes an image file to base64 string."""
    if not image_path or not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_mobile_preview(platform, brand_name, content, image_path=None, is_carousel=False, slides=None):
    """
    Generates HTML for a mobile feed preview.
    """
    
    # CSS Styles
    css = """
    <style>
        .phone-frame {
            border: 12px solid #111;
            border-radius: 30px;
            overflow: hidden;
            width: 320px;
            background: #fff;
            color: #000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0 auto;
            position: sticky;
            top: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        .li-header, .fb-header {
            padding: 12px;
            display: flex;
            align-items: center;
        }
        .avatar {
            width: 40px;
            height: 40px;
            background-color: #ddd;
            border-radius: 50%;
            margin-right: 10px;
            display: flex;
            align-items: center;
            justify_content: center;
            font-size: 20px;
        }
        .meta {
            display: flex;
            flex-direction: column;
            line-height: 1.2;
        }
        .name {
            font-weight: 600;
            font-size: 14px;
        }
        .sub-meta {
            font-size: 12px;
            color: #666;
        }
        .post-content {
            padding: 0 12px 12px 12px;
            font-size: 14px;
            white-space: pre-wrap;
            color: #333;
        }
        .post-image {
            width: 100%;
            height: auto;
            display: block;
            border-top: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }
        .carousel-container {
            display: flex;
            overflow-x: auto;
            padding-bottom: 5px;
        }
        .carousel-slide {
            min-width: 280px;
            margin-right: 10px;
            border: 1px solid #eee;
        }
        .action-bar {
            padding: 10px;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-around;
            color: #666;
            font-size: 12px;
            font-weight: 600;
        }
        /* Platform Specifics */
        .platform-li { border-bottom: 1px solid #e0e0e0; margin-bottom: 10px; }
        .platform-fb { border-bottom: 1px solid #e0e0e0; margin-bottom: 10px; }
    </style>
    """
    
    # Header Construction
    if platform.lower() == 'linkedin':
        sub_meta_html = "<span>Promoted</span> • <i class='icon'>Now</i>"
        actions_html = "<span>👍 Like</span><span>💬 Comment</span><span>↪️ Repost</span><span>🚀 Send</span>"
    else: # Facebook
        sub_meta_html = "<span>Sponsored</span> • <i class='icon'>Now</i>"
        actions_html = "<span>👍 Like</span><span>💬 Comment</span><span>↗️ Share</span>"

    # Image Logic
    img_html = ""
    
    if is_carousel and slides:
        # Carousel View
        img_html = "<div class='carousel-container'>"
        for slide in slides:
            s_img_path = slide.get('image_path')
            s_img_b64 = get_image_base64(s_img_path) if s_img_path else None
            
            img_src = f"data:image/png;base64,{s_img_b64}" if s_img_b64 else "https://via.placeholder.com/300x300?text=Slide"
            
            img_html += f"""
            <div class='carousel-slide'>
                <img src='{img_src}' class='post-image'>
                <div style='padding:5px; font-size:11px; color:#555; background:#f9f9f9;'>{slide.get('text', '')[:50]}...</div>
            </div>
            """
        img_html += "</div>"
    
    else:
        # Single Image View
        img_b64 = get_image_base64(image_path)
        if img_b64:
            img_html = f"<img src='data:image/png;base64,{img_b64}' class='post-image'>"
        else:
            img_html = "<div style='height:200px; background:#f0f2f5; display:flex; align-items:center; justify-content:center; color:#999;'>No Visual</div>"

    # Truncate content for preview
    display_content = content[:200] + "..." if len(content) > 200 else content

    # Assemble HTML
    html = f"""
    {css}
    <div class="phone-frame">
        <div class="{'platform-li' if platform=='LinkedIn' else 'platform-fb'}">
            <div class="{ 'li-header' if platform=='LinkedIn' else 'fb-header' }">
                <div class="avatar">🤖</div>
                <div class="meta">
                    <span class="name">{brand_name}</span>
                    <span class="sub-meta">{sub_meta_html}</span>
                </div>
            </div>
            <div class="post-content">
                {display_content} 
                { "<span style='color:#0a66c2; font-weight:600;'>...see more</span>" if len(content)>200 else ""}
            </div>
            {img_html}
            <div class="action-bar">
                {actions_html}
            </div>
        </div>
    </div>
    """
    
    return html
