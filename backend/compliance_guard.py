import google.generativeai as genai
import re
import json
from project_config import Config
from backend.database import Database

class ComplianceGuard:
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Use Flash for speed
        self.db = Database()

    def scan_post(self, text, brand_dna):
        """
        Runs a comprehensive compliance check on the post.
        """
        report = {
            "score": 100,
            "status": "PASS",
            "issues": [],
            "banned_word_hits": []
        }

        # 1. Hard Rule Check (Banned Words)
        # Handle case where brand_dna might be partially populated
        banned_words = []
        if brand_dna and 'voice_analysis' in brand_dna:
             banned_words = brand_dna['voice_analysis'].get('banned_words', [])
        
        for word in banned_words:
            # Simple case-insensitive match
            if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                report["banned_word_hits"].append(word)
                report["issues"].append(f"Contains banned word: '{word}'")
                report["score"] -= 20

        # 2. Smart AI Check (Legal/PR/Tone)
        ai_report = self._ai_risk_assessment(text, brand_dna)
        
        # Merge AI findings
        if ai_report:
            if ai_report.get('legal_risk', False):
                report["issues"].append(f"⚠️ LEGAL RISK: {ai_report.get('legal_reason')}")
                report["score"] -= 50
            
            if ai_report.get('pr_risk', False):
                report["issues"].append(f"🔥 PR RISK: {ai_report.get('pr_reason')}")
                report["score"] -= 30

            if ai_report.get('tone_violation', False):
                 report["issues"].append(f"Tone Mismatch: {ai_report.get('tone_reason')}")
                 report["score"] -= 10

            if ai_report.get('factual_risk', False):
                 report["issues"].append(f"🧠 REALITY CHECK: {ai_report.get('factual_reason')}")
                 report["score"] -= 100 # Immediate Fail for hallucinations
                 
        # Final Score Logic
        report["score"] = max(0, report["score"])
        
        if report["score"] < 50:
            report["status"] = "FAIL"
        elif report["score"] < 80:
            report["status"] = "WARN"
            
        return report

    def _ai_risk_assessment(self, text, brand_dna):
        """
        Uses LLM to detect subtle risks.
        """
        
        # Extract constraints for the prompt
        anti_patterns = []
        if brand_dna and 'voice_analysis' in brand_dna:
             anti_patterns = brand_dna['voice_analysis'].get('anti_patterns', [])
             
        prompt = f"""
        You are a Corporate Compliance Officer and PR Crisis Manager.
        Analyze this social media post for critical risks.

        POST CONTENT:
        "{text}"

        BRAND ANTI-PATTERNS (Things strictly forbidden):
        {json.dumps(anti_patterns)}

        CHECKLIST:
        1. Legal Risk: Does it make specific unverified claims ("We guarantee 100% ROI"), promise results that vary, or slander competitors?
        2. PR Risk: Is it offensive, tone-deaf, politically charged, or likely to cause a backlash?
        3. Factual Risk: Does it contain claims that are physically impossible or universally known to be false (e.g. "Humans living on Mars", "Time travel")?
        4. Tone Violation: Does it violate the Anti-Patterns listed above?

        Return a JSON object:
        {{
            "legal_risk": true/false,
            "legal_reason": "Brief explanation if true",
            "pr_risk": true/false,
            "pr_reason": "Brief explanation if true",
            "factual_risk": true/false,
            "factual_reason": "Brief explanation if true",
            "tone_violation": true/false,
            "tone_reason": "Brief explanation if true"
        }}
        RETURN ONLY JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # --- COST LOGGING ---
            try:
                usage = response.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name="ComplianceGuard",
                        model="gemini-2.0-flash-exp",
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except Exception as e:
                print(f"Failed to log usage: {e}")
            
            result = response.text.strip()
            # Clean markdown code blocks if present
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            return json.loads(result)
        except Exception as e:
            print(f"Compliance AI Error: {e}")
            return None
