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
from backend.agents.strategist import StrategistAgent
from backend.agents.creator import CreatorAgent
from backend.agents.art_director import ArtDirectorAgent
from backend.agents.reviewer import ReviewerAgent
from backend.compliance_guard import ComplianceGuard

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
        self.strategist = StrategistAgent()
        self.creator = CreatorAgent()
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
        
        # 1. STRATEGIST: Plan the Week
        print("Agent: Strategist planning...")
        if progress_callback: progress_callback("🧠 Agent: Strategist designing weekly plan...")
        week_plan = self.strategist.plan_week(
            topic, 
            self.company_info if isinstance(self.company_info, dict) else {},
            context=f"{trends}\n{context_str}",
            campaign_type=campaign_type
        )
        
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
                
                drafts = self.creator.draft_content(day_item, self.company_info, critique)
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
        
        drafts = self.creator.draft_content(fake_plan, "Professional")
        
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
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""
            Create a highly detailed AI image generation prompt.
            
            CONTEXT (The Post):
            "{post_content}"
            
            VISUAL STYLE (The Template):
            "{style_description}"
            
            TASK:
            Combine the core subject from the Context with the Visual Style.
            describe the SUBJECT acting out the context, but strictly adhering to the VISUAL STYLE.
            
            Output ONLY the final prompt string.
            """
            
            resp = model.generate_content(prompt)
            # Log usage
            try:
                usage = resp.usage_metadata
                if usage:
                     self.db.log_usage("ContentGenerator", "gemini-2.0-flash-exp", usage.prompt_token_count, usage.candidates_token_count, client_id=self.client_id)
            except: pass
            
            return resp.text.strip()
        except Exception as e:
            print(f"Error tailoring prompt: {e}")
            return f"{post_content}. Style: {style_description}"
