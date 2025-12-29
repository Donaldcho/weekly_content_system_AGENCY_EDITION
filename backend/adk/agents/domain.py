from backend.adk.tools import Toolbox
from .base import BaseAdkAgent
import google.generativeai as genai
import json

class DomainAgent(BaseAdkAgent):
    def suggest_domains(self, keywords_str):
        """
        Takes user keywords, generates variations, and checks availability (mock).
        """
        # 1. Ideation Phase
        prompt = f"""
        You are a Domain Name Expert.
        User Keywords: {keywords_str}
        
        Task: return a JSON list of 10 creative, brandable domain keywords based on the input.
        Do not add TLDs yet. Just the name part.
        Example Input: "fast food" -> Output: ["QuickBite", "SpeedyEats", ...]
        
        Return JSON Key: "ideas"
        """
        raw = self.generate(prompt)
        try:
            ideas = json.loads(raw).get("ideas", [])
        except:
            ideas = [keywords_str]

        # 2. Validation Phase (Tool Use)
        # In a full Agent Runtime, the LLM would call this tool. 
        # Here we manually orchestrate for stability.
        available = self.tools.check_domains(ideas)
        
        return json.loads(available)
