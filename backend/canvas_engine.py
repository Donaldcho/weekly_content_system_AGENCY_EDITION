from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import os
import uuid

class CanvasEngine:
    def __init__(self, width=1080, height=1080, bg_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.layers = [] # List of dicts: {type, content, x, y, ...}
        self.bg_image_path = None

    def set_background_image(self, path):
        if os.path.exists(path):
            self.bg_image_path = path

    def add_text_layer(self, text, x, y, font_size=60, color="#000000", font_path=None, effects=None, box_width=0, align="left"):
        layer = {
            "id": str(uuid.uuid4()),
            "type": "text",
            "content": text,
            "x": x,
            "y": y,
            "font_size": font_size,
            "color": color,
            "font_path": font_path,
            "box_width": box_width,
            "align": align,
            "effects": effects or {}
        }
        self.layers.append(layer)
        return layer["id"]

    def add_image_layer(self, image_path, x, y, width=None, opacity=1.0):
        if not os.path.exists(image_path):
            return None
            
        layer = {
            "id": str(uuid.uuid4()),
            "type": "image",
            "content": image_path,
            "x": x,
            "y": y,
            "width": width, # If None, use original
            "opacity": opacity
        }
        self.layers.append(layer)
        return layer["id"]

    def update_layer(self, layer_id, **kwargs):
        for layer in self.layers:
            if layer["id"] == layer_id:
                layer.update(kwargs)
                return True
        return False

    def remove_layer(self, layer_id):
        self.layers = [l for l in self.layers if l["id"] != layer_id]

    def add_shape_layer(self, shape_type, x, y, width, height, color="#000000", opacity=1.0, border_radius=0):
        layer = {
            "id": str(uuid.uuid4()),
            "type": "shape",
            "shape_type": shape_type, # "rectangle", "circle"
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "color": color,
            "opacity": opacity,
            "border_radius": border_radius
        }
        self.layers.append(layer)
        return layer["id"]
    
    # ... (Keep add_text_layer and add_image_layer)

    def render(self):
        # 1. Background
        if self.bg_image_path:
            try:
                base = Image.open(self.bg_image_path).convert("RGBA")
                base = ImageOps.fit(base, (self.width, self.height), method=Image.Resampling.LANCZOS)
            except:
                base = Image.new("RGBA", (self.width, self.height), self.bg_color)
        else:
            base = Image.new("RGBA", (self.width, self.height), self.bg_color)

        # 2. Layers
        for layer in self.layers:
            try:
                if layer["type"] == "shape":
                    # Draw Shape to temp layer for opacity
                    shape_img = Image.new('RGBA', (layer["width"], layer["height"]), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(shape_img)
                    
                    fill_col = layer["color"] # Hex
                    
                    if layer["shape_type"] == "rectangle":
                        draw.rounded_rectangle(
                            (0, 0, layer["width"], layer["height"]), 
                            radius=layer.get("border_radius", 0), 
                            fill=fill_col
                        )
                    elif layer["shape_type"] == "circle":
                        draw.ellipse((0, 0, layer["width"], layer["height"]), fill=fill_col)
                        
                    # Opacity
                    if layer.get("opacity", 1.0) < 1.0:
                        start_alpha = shape_img.split()[3]
                        alpha = start_alpha.point(lambda p: p * layer["opacity"])
                        shape_img.putalpha(alpha)
                        
                    base.paste(shape_img, (layer["x"], layer["y"]), shape_img)

                elif layer["type"] == "text":
                    # ... (Text Rendering Logic - Keep Existing)
                    fill = layer["color"]
                    
                    try:
                        f = ImageFont.truetype(layer.get("font_path") or "arial.ttf", layer["font_size"])
                    except:
                        f = ImageFont.load_default()
                    
                    effects = layer.get("effects", {})
                    x_start, y_start = layer["x"], layer["y"]
                    raw_text = layer["content"]
                    box_w = layer.get("box_width", 0)
                    align = layer.get("align", "left")

                    # Wrap Text
                    lines = self._wrap_text(raw_text, f, box_w) if box_w > 0 else raw_text.split('\n')
                    
                    # Calculate Line Height
                    try:
                        bbox_sample = f.getbbox("Ay")
                        line_height = (bbox_sample[3] - bbox_sample[1]) * 1.2 
                    except:
                        line_height = layer["font_size"] * 1.2

                    current_y = y_start
                    draw = ImageDraw.Draw(base)

                    # 0. Layout Calculation
                    layout = [] 
                    current_y = y_start
                    max_line_w = 0
                    
                    for line in lines:
                        line_w = f.getlength(line)
                        if line_w > max_line_w: max_line_w = line_w
                        draw_x = x_start
                        if box_w > 0:
                            if align == "center": draw_x = x_start + (box_w - line_w) / 2
                            elif align == "right": draw_x = x_start + (box_w - line_w)
                        layout.append((line, draw_x, current_y))
                        current_y += line_height

                    # 1. Background Effect
                    if effects.get("background"):
                        bg_eff = effects["background"]
                        pad = bg_eff.get("padding", 10)
                        if box_w > 0: block_w = box_w 
                        else: block_w = max_line_w
                        block_h = len(lines) * line_height
                        draw.rounded_rectangle(
                            (x_start - pad, y_start - pad, x_start + block_w + pad, y_start + block_h + pad - (line_height * 0.2)),
                            radius=bg_eff.get("radius", 0), fill=bg_eff.get("color", "#000000")
                        )

                    # 2. Glow / Shadow
                    if effects.get("shadow") or effects.get("glow"):
                        if effects.get("glow"):
                            gl = effects["glow"]
                            glow_img = Image.new('RGBA', base.size, (0,0,0,0))
                            g_draw = ImageDraw.Draw(glow_img)
                            for text_line, lx, ly in layout: g_draw.text((lx, ly), text_line, font=f, fill=gl.get("color", "yellow"))
                            glow_img = glow_img.filter(ImageFilter.GaussianBlur(gl.get("blur", 10)))
                            base.paste(glow_img, (0,0), glow_img)

                        if effects.get("shadow"):
                            sh = effects["shadow"]
                            shadow_img = Image.new('RGBA', base.size, (0,0,0,0))
                            s_draw = ImageDraw.Draw(shadow_img)
                            for text_line, lx, ly in layout: s_draw.text((lx + sh.get("offset_x", 5), ly + sh.get("offset_y", 5)), text_line, font=f, fill=sh.get("color", "black"))
                            if sh.get("blur", 5) > 0: shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(sh.get("blur", 5)))
                            base.paste(shadow_img, (0,0), shadow_img)

                    # 3. Main Text
                    outline = effects.get("outline")
                    for text_line, lx, ly in layout:
                        if outline:
                             draw.text((lx, ly), text_line, font=f, fill=fill, stroke_width=outline.get("width", 2), stroke_fill=outline.get("color", "black"))
                        else:
                             draw.text((lx, ly), text_line, font=f, fill=fill)

                elif layer["type"] == "image":
                    img = Image.open(layer["content"]).convert("RGBA")
                    
                    # Resize
                    if layer.get("width"):
                        w_pct = layer["width"] / float(img.size[0])
                        h_size = int((float(img.size[1]) * float(w_pct)))
                        img = img.resize((layer["width"], h_size), Image.Resampling.LANCZOS)
                    
                    # FILTERS
                    filters = layer.get("filters", {})
                    if filters.get("brightness") and filters["brightness"] != 1.0:
                        img = ImageEnhance.Brightness(img).enhance(filters["brightness"])
                    if filters.get("contrast") and filters["contrast"] != 1.0:
                        img = ImageEnhance.Contrast(img).enhance(filters["contrast"])
                    if filters.get("saturation") and filters["saturation"] != 1.0:
                        img = ImageEnhance.Color(img).enhance(filters["saturation"])
                    
                    # Opacity
                    if layer.get("opacity", 1.0) < 1.0:
                        alpha = img.split()[3]
                        alpha = alpha.point(lambda p: p * layer["opacity"])
                        img.putalpha(alpha)

                    base.paste(img, (layer["x"], layer["y"]), img)
            except Exception as e:
                print(f"Error rendering layer {layer}: {e}")

        return base

    def save(self, output_path):
        img = self.render()
        img.save(output_path)
        return output_path
