import os
import time
import sys
from PIL import Image
import io
from google import genai
# types removed to avoid version conflicts

# Add parent directory to path to import project_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config
from backend.database import Database

class NanoBanana:
    def __init__(self, tier="Pro"):
        conf = Config()
        self.api_key = conf.GOOGLE_API_KEY
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment.")
        
        # Initialize the new 2025 Client
        self.client = genai.Client(api_key=self.api_key)
        self.db = Database()
        
        # Model Mapping based on User Definition
        self.default_model = self._get_model_for_tier(tier)
        print(f"Nano Banana Initialized. Default Tier: {tier} | Model: {self.default_model}") 

    def _get_model_for_tier(self, tier):
        if tier == "Pro":
            return "gemini-3-pro-image-preview"
        elif tier == "Flash" or tier == "Nano":
            return "gemini-2.5-flash-image"
        else:
            return "imagen-3.0-generate-001"

    def generate_image(self, prompt, output_filename=None, reference_image_path=None, tier=None):
        """
        Generates an image using the new Google GenAI SDK.
        Automatically switches between 'generate_content' (Gemini) and 'generate_images' (Imagen).
        """
        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"nano_banana_{timestamp}.png"
        
        # Determine Model
        active_model_name = self._get_model_for_tier(tier) if tier else self.default_model
        
        conf = Config()
        output_path = os.path.join(conf.IMAGES_DIR, output_filename)
        os.makedirs(conf.IMAGES_DIR, exist_ok=True)

        print(f"🍌 Nano Banana ({active_model_name}) engaging: {prompt[:50]}...")
        
        try:
            # UNIVERSAL SWITCH LOGIC
            # Gemini models (e.g. gemini-3-pro-image-preview) are multimodal -> use generate_content
            # Imagen models (e.g. imagen-3.0) are pure image -> use generate_images
            
            if "gemini" in active_model_name.lower():
                # --- PATH A: GEMINI (Multimodal) ---
                print(f"   -> Detected Gemini Model. Using generate_content(response_modalities=['IMAGE'])...")
                response = self.client.models.generate_content(
                    model=active_model_name,
                    contents=prompt,
                    config={
                        'response_modalities': ['IMAGE'],
                        'safety_settings': [ # Minimal safety for creative freedom (user requested Block Only High)
                            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_ONLY_HIGH'},
                            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_ONLY_HIGH'},
                            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_ONLY_HIGH'},
                            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_ONLY_HIGH'}
                        ]
                    }
                )
                
                # Gemini returns images in response.candidates[0].content.parts[0].inline_data
                # Or sometimes response.text if it failed to gen image.
                # The SDK helper `response.candidates[0].content.parts[0].image` or similar might exist?
                # Let's try standard part inspection.
                
                valid_image = False
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.mime_type.startswith('image'):
                            image = Image.open(io.BytesIO(part.inline_data.data))
                            image.save(output_path)
                            valid_image = True
                            break
                        # SDK specific helper for newer versions
                        if hasattr(part, 'image') and part.image:
                             # part.image might be the image bytes or object
                             # In 0.8.5 it might be part.image_bytes?
                             # Let's rely on inline_data if possible as it's raw protobuf
                             # actually, let's try the high level first if available
                             pass
                
                if not valid_image:
                     # Check if it returned text refusal
                     if response.text:
                         print(f"Gemini Refusal: {response.text}")
                     raise Exception("No image part found in Gemini response.")

            else:
                # --- PATH B: IMAGEN (Pure Image) ---
                print(f"   -> Detected Imagen Model. Using generate_images()...")
                response = self.client.models.generate_images(
                    model=active_model_name,
                    prompt=prompt,
                    config={
                        'number_of_images': 1,
                        'safety_filter_level': "BLOCK_ONLY_HIGH",
                        'person_generation': "ALLOW_ADULT",
                    }
                )
                
                if hasattr(response, 'generated_images') and response.generated_images:
                    image_bytes = response.generated_images[0].image.image_bytes
                    image = Image.open(io.BytesIO(image_bytes))
                    image.save(output_path)
                else:
                     raise Exception("No image returned from Imagen API")

            return self._apply_branding_if_enabled(output_path)

        except Exception as e:
            print(f"Nano Banana Engine Failure ({active_model_name}): {e}")
            
            # 2. Fallback: Dream Mode (Gemini 2.0 Flash)
            print("Engaging Dream Mode (Fallback)...")
            dream_text = self._dream_concept(prompt)
            return self._generate_dream_card(dream_text, output_path)

    def _apply_branding_if_enabled(self, image_path):
        """
        Applies watermark/logo if configured in Brand Identity.
        """
        # (Keep existing implementation or stub call to external tool)
        # For now, just return path, or you can import backend.post_processing
        try:
            from backend.post_processing import ImageBrander
            brander = ImageBrander(self.db)
            # Assuming we pick the first client for now or default
            return brander.apply_brand_to_image(image_path, client_id=1) 
        except ImportError:
            return image_path
        except Exception as e:
            print(f"Branding failed: {e}")
            return image_path

    def _dream_concept(self, original_prompt):
        """
        Uses Gemini (Text) to describe a concept image.
        """
        try:
            # Using the same client for text generation
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp", # or gemini-1.5-flash
                contents=f"Describe a vivid, abstract, artistic concept image for this prompt. Keep it under 20 words. Prompt: {original_prompt}"
            )
            return response.text.strip()
        except Exception as e:
            print(f"Dreaming failed: {e}")
            return "Abstract Concept Failure"

    def _generate_dream_card(self, text, output_path):
        from PIL import Image, ImageDraw, ImageFont
        try:
            img = Image.new('RGB', (1024, 1024), color=(20, 20, 40))
            d = ImageDraw.Draw(img)
            
            # Abstract Art (Random circles)
            import random
            for _ in range(5):
                x = random.randint(0, 1024)
                y = random.randint(0, 1024)
                r = random.randint(100, 400)
                color = (random.randint(50, 255), random.randint(50, 255), 255, 50)
                d.ellipse([x-r, y-r, x+r, y+r], fill=color)
                
            # Text
            try:
                # Basic font fallback
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Draw Text
            d.text((512, 400), "✨ CONCEPT DREAM", fill="yellow", anchor="mm", font=font)
            d.text((512, 512), text[:50], fill="white", anchor="mm", font=font)
            
            img.save(output_path)
            return output_path
        except Exception as e:
            print(f"Card Gen Failed: {e}")
            return None

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
