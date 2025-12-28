from PIL import Image
import os

class ImageBrander:
    def __init__(self, logo_path=None):
        self.logo_path = logo_path

    def apply_branding(self, image_path, logo_path=None):
        """
        Overlays a logo onto the bottom-right corner of the image.
        Args:
            image_path: Path to the base image.
            logo_path: Path to the logo (overrides instance logo_path).
        Returns:
            Path to the modified image (overwrites original by default).
        """
        target_logo = logo_path or self.logo_path
        if not target_logo or not os.path.exists(target_logo):
            return image_path

        try:
            base_img = Image.open(image_path).convert("RGBA")
            logo_img = Image.open(target_logo).convert("RGBA")

            # Resize logo to 15% of base image width
            base_width, base_height = base_img.size
            logo_width_percent = 0.15
            
            w_percent = (base_width * logo_width_percent) / float(logo_img.size[0])
            h_size = int((float(logo_img.size[1]) * float(w_percent)))
            logo_resized = logo_img.resize((int(base_width * logo_width_percent), h_size), Image.Resampling.LANCZOS)

            # Position: Bottom Right with padding
            padding = int(base_width * 0.05)
            position = (base_width - logo_resized.width - padding, base_height - logo_resized.height - padding)

            # Composite
            base_img.paste(logo_resized, position, logo_resized)
            
            # Save back (convert to RGB if saving as JPG, or keep RGBA for PNG)
            # Assuming PNG for now or checking extension
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                base_img = base_img.convert("RGB")
            
            base_img.save(image_path)
            return image_path
            
        except Exception as e:
            print(f"Branding failed: {e}")
            return image_path
