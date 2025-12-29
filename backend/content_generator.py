import google.generativeai as genai
import json
import os
import sys
import time
# Add parent directory to path to import project_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config
from backend.rag import RAGEngine

import google.generativeai as genai
import json
import os
import sys
import time

# Add parent directory to path to import project_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_config import Config
from backend.database import Database
from backend.rag import RAGEngine
from backend.adk.main import MarketingAgency
from backend.agents.art_director import ArtDirectorAgent
from backend.agents.reviewer import ReviewerAgent
from backend.compliance_guard import ComplianceGuard
from PIL import Image, ImageDraw, ImageFont # For fallback generation
import random

class ContentGenerator:
    def __init__(self, client_id=1):
        # Configure shared API key setup
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.db = Database()
        self.client_id = client_id
        
        # Load Context and Memory from DB (Multi-Tenant)
        self.company_info = self.db.get_brand_settings(client_id=client_id)
        
        conf = Config()
        # History is likely still global or needs update, for now keeping file based but note:
        # Ideally history should be in DB per client too.
        # But for now, we focus on brand identity.
        self.history = self._load_json(conf.HISTORY_PATH)
        self.rag = RAGEngine()
        self.db = Database()
        
        # Initialize Agents
        print("Initializing Agents...")
        self.agency = MarketingAgency()
        # Legacy agents kept for visuals/review until fully ported
        self.art_director = ArtDirectorAgent()
        self.reviewer = ReviewerAgent()
        self.compliance = ComplianceGuard()

    def _load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self, post_data):
        self.history.append(post_data)
        if len(self.history) > 20:
            self.history = self.history[-20:]
        try:
            with open(Config().HISTORY_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass

    def _format_company_info(self):
        if isinstance(self.company_info, dict):
            return f"""
            Brand Name: {self.company_info.get('name', '')}
            Industry: {self.company_info.get('industry', '')}
            Mission: {self.company_info.get('mission', '')}
            Tone: {self.company_info.get('tone', '')}
            Target Audience: {self.company_info.get('target_audience', '')}
            """
        return str(self.company_info)

    def generate_weekly_plan(self, topic, trends, model_name='gemini-2.0-flash-exp', use_rag=True, campaign_type="Weekly Routine", progress_callback=None):
        """
        Orchestrates the Multi-Agent Pipeline:
        Strategist -> Creator -> ArtDirector -> Reviewer
        """
        print(f"Starting MAS Pipeline for topic: {topic}")
        if progress_callback: progress_callback(f"🚀 Starting MAS Pipeline for topic: {topic}")
        
        # 0. Context Gathering (RAG)
        context_str = ""
        if use_rag:
            print("Agent: Researcher (RAG + Web) working...")
            if progress_callback: progress_callback("🔍 Agent: Researcher (RAG) gathering context...")
            
            # 1. Local Vault
            docs = self.rag.retrieve(topic)
            
            # 2. Web Research
            web_docs = self.rag.search_web(topic)
            docs.extend(web_docs)
            
            if docs:
                 context_str = "\n".join([f"[{d['filename']}] {d['content']}" for d in docs])
        
        # 1. STRATEGIST: Plan the Week (ADK Version)
        print("Agent: Strategist planning...")
        if progress_callback: progress_callback("🧠 Agent: Strategist designing weekly plan...")
        
        # New ADK Strategist returns { "strategy_analysis": ..., "week_plan": [...] }
        strategy_result = self.agency.create_strategy(
            topic, 
            self.company_info if isinstance(self.company_info, dict) else {}
        )
        week_plan = strategy_result.get("week_plan", [])
        
        # SAFETY: Ensure week_plan is a list of dicts
        if isinstance(week_plan, dict):
            week_plan = [week_plan] # Handle single object return
        if not isinstance(week_plan, list):
            week_plan = []
            
        full_results = []
        brand_tone = self.company_info.get('tone', 'Professional') if isinstance(self.company_info, dict) else "Professional"
        
        # 2. EXECUTION LOOP
        total_days = len(week_plan)
        for i, day_item in enumerate(week_plan):
            if not isinstance(day_item, dict):
                print(f"Skipping invalid day_item: {day_item}")
                continue
                
            day_name = day_item.get('day', 'Unknown')
            print(f"  processing {day_name}...")
            if progress_callback: progress_callback(f"⚡ [Day {i+1}/{total_days}] processing {day_name}...")
            
            # A. Creator (Drafting)
            # A. Creator (Drafting) with CRITIC LOOP
            if progress_callback: progress_callback(f"✍️ [Day {i+1}/{total_days}] Creator writing drafts for {day_name}...")
            
            drafts = {}
            critique = None
            max_retries = 2
            
            for attempt in range(max_retries + 1):
                if attempt > 0:
                     print(f"  [Attempt {attempt+1}] Improving draft based on critique...")
                
                drafts = self.agency.generate_day_content(day_item, self.company_info, critique)
                if not isinstance(drafts, dict): drafts = {}
                
                # Check Compliance (Guardrail)
                # Primary check on LinkedIn draft
                text_to_check = drafts.get('linkedin_draft', '') or drafts.get('facebook_draft', '')
                report = self.compliance.scan_post(text_to_check, self.company_info)
                
                if report['score'] >= 80:
                    # Pass!
                    break
                else:
                    # Fail - prepare feedback for next loop
                    issues = "; ".join(report['issues'])
                    critique = f"GUARDRAIL ALERT (Score {report['score']}): {issues}. Please strictly adhere to brand guidelines."
                    if attempt == max_retries:
                        print("  [Warning] Max retries reached. Using best effort.")
            
            # B. Art Director (Visuals)
            # Use LinkedIn draft as basis for visual
            if progress_callback: progress_callback(f"🎨 [Day {i+1}/{total_days}] Art Director designing visuals for {day_name}...")
            ref_text = drafts.get('linkedin_draft', '') or drafts.get('facebook_draft', '')
            visuals = self.art_director.design_visuals(day_name, topic, ref_text)
            if not isinstance(visuals, dict): visuals = {} # Safety fallback
            
            # C. Reviewer (Quality Control)
            # We review the LinkedIn draft as the primary sample
            if progress_callback: progress_callback(f"👀 [Day {i+1}/{total_days}] Reviewer checking quality for {day_name}...")
            critique_data = self.reviewer.review_draft(ref_text, brand_tone)
            if not isinstance(critique_data, dict): critique_data = {} # Safety fallback
            
            # Combine into final structure expected by UI
            result_obj = {
                "day": day_name,
                "linkedin_draft": drafts.get('linkedin_draft', ""),
                "facebook_draft": drafts.get('facebook_draft', ""),
                "image_prompt": visuals.get("image_prompt", ""),
                "strategy_angle": day_item.get('angle', ""),
                "quality_score": critique_data.get("score", 0),
                "critique": critique_data.get("critique", "")
            }
            full_results.append(result_obj)
            
        print("[OK] Pipeline Complete.")
        if progress_callback: progress_callback("✅ Pipeline Complete.")
        return full_results

    def generate_post(self, platform, topic, trends="", use_rag=True):
        """
        Single post generation using Agents.
        """
        # Quick adaptation of Creator Agent for single post
        # For a single "Generate Post" button, we simulate a single-day plan
        fake_plan = {
            "day": "Today",
            "focus": "Spotlight",
            "angle": f"Talk about {topic}"
        }
        
        drafts = self.agency.generate_day_content(fake_plan, "Professional")
        
        # Return specific platform draft
        if platform.lower() == "linkedin":
            return drafts.get('linkedin_draft', "")
        else:
            return drafts.get('facebook_draft', "")

    def generate_carousel_content(self, topic, original_content):
        # Keeping legacy logic for now, or could use CreatorAgent if we add 'carousel' capability
        # For speed, we just use a direct prompt here as it's a specific format
        model_name = 'gemini-2.0-flash-exp'
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Convert this text into a 3-slide LinkedIn Carousel JSON:
        Text: {original_content}
        Topic: {topic}
        Output JSON list: [{{ "slide": 1, "text": "...", "image_prompt": "..." }}]
        """
        try:
            resp = model.generate_content(prompt)
            # Log Usage
            try:
                usage = resp.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name="ContentGenerator",
                        model=model_name,
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except: pass
            
            clean = resp.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            return []

    def analyze_image_style(self, image_path):
        """
        Uses Gemini Vision to extract a style prompt from an image.
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Load image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            prompt = """
            Analyze this image and describe its visual style in a way that can be used as an AI image generation prompt.
            Focus on:
            1. Art style (e.g. minimalist vector, cyberpunk 3D, oil painting)
            2. Lighting and Color Palette
            3. Composition and Camera Angle
            4. Mood/Atmosphere
            
            Output ONLY the comma-separated description string. Keep it concise (under 50 words).
            """
            
            resp = model.generate_content([prompt, img])
            return resp.text.strip()
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return "Visual style extraction failed."

    def generate_tailored_image_prompt(self, post_content, style_description):
        """
        Generates a specific prompt combining the post's topic and the template's style.
        Uses externalizable prompt templates from PromptRegistry.
        """
        try:
            from backend.prompt_registry import PromptRegistry
            registry = PromptRegistry()
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Fetch from JSON config
            prompt = registry.get(
                "smart_style_generator", 
                post_content=post_content, 
                style_description=style_description
            )
            
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except:
            return f"{post_content}. Style: {style_description}"

    def generate_image(self, prompt, filename_prefix="generated"):
        """
        Generates an image using Gemini Imagen 3 (or fallback Mock).
        Returns the local file path of the saved image.
        """
        print(f"Generating image for: {prompt[:50]}...")
        save_dir = os.path.join(Config().ASSETS_DIR, "generated")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)
        
        # 1. Try Real AI Generation
        try:
            # Check availability dynamically to avoid crash if lib is old
            if hasattr(genai, 'ImageGenerationModel'):
                model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                response = model.generate_images(prompt=prompt, number_of_images=1)
                
                if response and response.images:
                    image = response.images[0]
                    image.save(filepath)
                    return filepath
            else:
                 print("WARN: ImageGenerationModel not found. Using Mock.")

        except Exception as e:
            print(f"Image Gen Error (Falling back to Mock): {e}")
            
        # 2. Fallback: Mock Image Generation (Robustness)
        return self._create_mock_image(prompt, filepath)

    def _create_mock_image(self, prompt, filepath):
        """
        Generates a placeholder image with the prompt text.
        """
        try:
            width, height = 512, 512
            # Random dark background color
            bg_color = (random.randint(20, 50), random.randint(20, 50), random.randint(50, 80))
            img = Image.new('RGB', (width, height), color=bg_color)
            d = ImageDraw.Draw(img)
            
            # Draw basic pattern
            for _ in range(10):
                x_a = random.randint(0, width)
                y_a = random.randint(0, height)
                x_b = random.randint(0, width)
                y_b = random.randint(0, height)
                # Ensure x1 < x2, y1 < y2
                x1, x2 = sorted([x_a, x_b])
                y1, y2 = sorted([y_a, y_b])
                
                fill = (random.randint(50, 100), random.randint(50, 100), random.randint(100, 150), 100)
                d.ellipse([x1, y1, x2, y2], fill=fill)
                
            # Text
            try:
                # Try standard fonts first
                font = ImageFont.truetype("arial.ttf", 20)
                header_font = ImageFont.truetype("arial.ttf", 40)
            except:
                # Fallback to internal default
                print("Using default PIL font")
                font = ImageDraw.load_default()
                header_font = font
                
            # Centered Text (Simplified positioning)
            d.text((width/2, 50), "STYLE PREVIEW", fill=(255, 255, 255), anchor="mm", font=header_font)
            
            # Wrap text manually if needed or just show substring
            # Simple substring for robustness
            clean_prompt = prompt.replace("\n", " ")[:100] + "..."
            d.text((width/2, height/2), clean_prompt, fill=(200, 200, 200), anchor="mm", font=font)
            
            img.save(filepath)
            print(f"Mock image saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Mock Gen Error: {e}")
            import traceback
            traceback.print_exc()
            return None
