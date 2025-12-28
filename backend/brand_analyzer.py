import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from project_config import Config
from backend.database import Database
import json

class BrandAnalyzer:
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Good for vision
        self.text_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.db = Database()

    def _log_usage(self, response, model_name="gemini-2.0-flash-exp"):
        try:
            usage = response.usage_metadata
            if usage:
                self.db.log_usage(
                    agent_name="BrandAnalyzer",
                    model=model_name,
                    input_tokens=usage.prompt_token_count,
                    output_tokens=usage.candidates_token_count
                )
        except Exception as e:
            print(f"Failed to log usage: {e}")

    def analyze_logo(self, image_bytes, mime_type='image/png'):
        """
        FR-02: Visual Intelligence
        Analyzes a logo to extract precise Brand DNA.
        """
        prompt = """
        You are a Senior Brand Designer. Analyze this logo image.
        
        Strictly extract the following fields into a raw JSON object:
        {
            "primary_hex": "#RRGGBB (The single most dominant non-white/non-black color)",
            "secondary_hex": "#RRGGBB (The second most dominant accent color)",
            "art_style": "Short description of the visual style (e.g. 'Minimalist Flat', 'Cyberpunk 3D', 'Vintage Hand-drawn')",
            "colors": ["Hex1", "Hex2", "Hex3"]
        }
        
        If the image is monochrome, set secondary_hex to null.
        RETURN ONLY JSON. DO NOT use markdown code blocks.
        """
        try:
            image_part = {"mime_type": mime_type, "data": image_bytes}
            response = self.vision_model.generate_content([prompt, image_part])
            self._log_usage(response)
            return self._clean_json(response.text)
        except Exception as e:
            return {"error": str(e)}

    def analyze_website(self, url):
        """
        FR-01: Automated Discovery Tools
        Scrapes a website and uses AI to deduce the Identity.
        """
        try:
            # 1. Scrape with Timeout & UA Rotation
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            resp = requests.get(url, headers=headers, timeout=5) # FR-01 Timeout
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Extraction Heuristics
            page_title = soup.title.string if soup.title else ""
            
            meta_desc = ""
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta: meta_desc = meta.get('content')
            
            # Fallback for mission (first H1 or H2)
            h1 = soup.find('h1')
            h1_text = h1.get_text(strip=True) if h1 else ""
            
            # Body Text (Limit 1000 chars as per FR)
            text_body = soup.get_text(separator=' ', strip=True)[:1500]
            
            # 2. Analyze
            prompt = f"""
            Analyze this raw website data for a Brand Profile.
            
            Title: {page_title}
            Meta Description: {meta_desc}
            H1: {h1_text}
            Body Sample: {text_body}
            
            Deduce and return a raw JSON object:
            {{
                "identity": {{
                    "name": "Brand Name (inferred from title)",
                    "website": "{url}",
                    "mission": "A single clear mission statement (use meta desc or synthesize from body)",
                    "tagline": "A catchy, short tagline (existing or generated)",
                    "archetype": "One of the 12 Brand Archetypes (e.g. Hero, Sage, Innocent, Ruler, Creator, Caregiver, etc.)",
                    "values": ["Value 1", "Value 2", "Value 3"],
                    "differentiators": ["Diff 1", "Diff 2"]
                }},
                "voice": {{
                    "tone_vectors": {{
                        "formality": 0.0 to 1.0 (float),
                        "humor": 0.0 to 1.0 (float),
                        "edginess": 0.0 to 1.0 (float)
                    }},
                    "adjectives": ["Tone Adj 1", "Tone Adj 2", "Tone Adj 3"]
                }}
            }}
            RETURN ONLY JSON.
            """
            response = self.text_model.generate_content(prompt)
            self._log_usage(response)
            return self._clean_json(response.text)
        except Exception as e:
            return {"error": f"Failed to analyze website: {str(e)}"}

    def analyze_document(self, text_content):
        """
        FR-03: Document Ingestion
        Reads a manifesto/guideline and extracts granular constraints.
        """
        prompt = f"""
        Analyze this Brand Manifesto / internal document.
        
        TEXT CONTENT:
        {text_content[:8000]}
        
        Extract the following into a raw JSON object:
        {{
            "audience": {{
                "persona": "Primary User Persona Name/Title",
                "demographics": "Age, Role, Location details",
                "goals": ["Goal 1", "Goal 2"],
                "pain_points": ["Pain Point 1", "Pain Point 2"]
            }},
            "voice": {{
                 "adjectives": ["Tone Adj 1", "Tone Adj 2"],
                 "archetype": "Inferred Brand Archetype",
                 "dos": ["Do: Use active voice", "Do: Be encouraging"],
                 "donts": ["Don't: Use jargon", "Don't: Be passive"]
            }}
        }}
        RETURN ONLY JSON.
        """
        try:
            response = self.text_model.generate_content(prompt)
            self._log_usage(response)
            data = self._clean_json(response.text)
            return data
        except Exception as e:
            return {"error": str(e)}

    def analyze_style(self, text_samples):
        """
        FR-02 Upgrade: Linguistic Fingerprinting
        Analyzes past content to reverse-engineer the writing DNA.
        """
        prompt = f"""
        You are a Computational Linguist. Analyze these text samples from a specific author/brand.
        
        SAMPLES:
        {text_samples[:15000]}
        
        Reverse-engineer their writing style into a strict JSON format:
        {{
            "tone": "A high level string description of the tone (e.g. Professional, Witty)",
            "voice_profile": {{
                "sentence_structure": "e.g. Mix of short punchy fragments and long explanatory lists",
                "vocabulary_level": "e.g. PhD level technical OR 5th grade simple English",
                "emoji_usage": "e.g. Heavy usage at start of lines OR sparse usage only for emphasis",
                "formatting_quirks": "e.g. Uses '>>' for bullets, or double line breaks for emphasis"
            }},
            "key_phrases": ["List 3-5 phrases they use often"],
            "banned_words": ["List specific words or phrases they avoid"],
            "anti_patterns": ["List 3 things they NEVER do (e.g. never start with 'Hello', never use hashtags inline)"],
            "golden_samples": ["Select the best single paragraph from the input that represents their style"]
        }}
        """
        try:
            response = self.text_model.generate_content(prompt)
            self._log_usage(response)
            return self._clean_json(response.text)
        except Exception as e:
            return {"error": str(e)}

    def build_professional_profile(self, current_data):
        """
        Synthesizes raw brand data into a professional profile using AI.
        """
        prompt = f"""
        Act as a CMO. Synthesize the following raw brand data into a cohesive, professional 
        Brand Identity Profile.
        
        Raw Data:
        {json.dumps(current_data, indent=2, default=str)}
        
        1. Refine the 'mission' to be more impactful.
        2. Refine the 'tone' description.
        3. Create a 'value_proposition' summary.
        4. Generate a 'visual_guidelines' template if strictly missing, otherwise polish the existing one.
        
        Return a raw JSON object with:
        {{
            "mission": "Polished mission statement",
            "tone": "Polished tone guide",
            "value_proposition": "A compelling 1-2 sentence value prop",
            "visual_guidelines": "Clear visual art direction",
        }}
        RETURN ONLY JSON.
        """
        try:
            response = self.text_model.generate_content(prompt)
            self._log_usage(response)
            return self._clean_json(response.text)
        except Exception as e:
            return {"error": str(e)}

    def _clean_json(self, text):
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            if not text: return {}
            return json.loads(text)
        except:
            return {"error": "Failed to parse API response", "raw": text}
