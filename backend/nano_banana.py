from google import genai
from google.genai import types
import os
import time
import sys
from PIL import Image

# Add parent directory to path to import project_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config
from backend.database import Database

class NanoBanana:
    def __init__(self):
        conf = Config()
        if not conf.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not found in environment.")
        
        self.client = genai.Client(api_key=conf.GOOGLE_API_KEY)
        self.db = Database()
        
        # Using the "Nano Banana Pro" model (Gemini 3 Pro Image Preview)
        # As per docs: "generates up to two interim images... reasoning process"
        self.model_name = "gemini-3-pro-image-preview" 

    def generate_image(self, prompt, output_filename=None, reference_image_path=None):
        """
        Generates an image using Gemini 3 Pro 'Native' Image generation.
        Uses generate_content instead of generate_images.
        Supports optional reference_image_path for style/structure guidance.
        """
        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"nano_banana_{timestamp}.png"
        
        conf = Config()
        output_path = os.path.join(conf.IMAGES_DIR, output_filename)
        os.makedirs(conf.IMAGES_DIR, exist_ok=True)

        print(f"Nano Banana (Gemini 3) thinking about: {prompt}...")
        
        # Prepare contents (Prompt + Optional Image)
        contents = [prompt]
        if reference_image_path:
            try:
                print(f"Loading reference image: {reference_image_path}")
                ref_img = Image.open(reference_image_path)
                contents.append(ref_img)
            except Exception as e:
                print(f"Warning: Could not load reference image: {e}")

        try:
            # Native Gemini Image Generation uses generate_content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'], # Request generic Image output
                    image_config=types.ImageConfig(
                        aspect_ratio="1:1",
                        image_size="1K" 
                    )
                )
            )
            
            # Extract image from parts
            saved = False
            if response.parts:
                for part in response.parts:
                    # Check for inline data (image)
                    if part.inline_data:
                        # Decode and save
                        # The SDK helper part.as_image() returns a PIL Image
                        img = part.as_image()
                        img.save(output_path)
                        print(f"Success! Image saved to {output_path}")
                        saved = True
                        
                        # --- COST LOGGING ---
                        try:
                            # $0.04 per image generated
                            self.db.log_usage(
                                agent_name="NanoBanana",
                                model=self.model_name,
                                input_tokens=0,
                                output_tokens=0,
                                override_cost=0.04
                            )
                        except Exception as e:
                            print(f"Failed to log image cost: {e}")
                            
                        break # Save first image only for now
            
            if saved:
                # Apply Branding
                try:
                    from backend.post_processing import ImageBrander
                    brander = ImageBrander(logo_path=os.path.join(Config().ASSETS_DIR, "brand_logo.png"))
                    final_path = brander.apply_branding(output_path)
                    print(f"Branding applied: {final_path}")
                    return final_path
                except Exception as e:
                    print(f"Branding application failed: {e}")
                    return output_path
            else:
                print("No image parts found in response.")
                return self._generate_placeholder(prompt, output_path)

        except Exception as e:
            print(f"slipped: {e}")
            print("Falling back to placeholder...")
            return self._generate_placeholder(prompt, output_path)

    def _generate_placeholder(self, prompt, output_path):
        try:
            img = Image.new('RGB', (1024, 1024), color = (255, 223, 0)) 
            img.save(output_path)
            return output_path
        except Exception as e:
            print(f"CRITICAL: Placeholder generation failed: {e}")
            return None

if __name__ == "__main__":
    nb = NanoBanana()
    print("Testing Nano Banana Pro (Gemini 3)...")
    path = nb.generate_image("A cyberpunk banana reading a hologram newspaper")
    print(f"Result: {path}")
