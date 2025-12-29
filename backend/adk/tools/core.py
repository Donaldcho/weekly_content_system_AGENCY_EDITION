import google.generativeai as genai
from duckduckgo_search import DDGS
import json
import os
import sys

# Add parent to path to reach backend.database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database import Database
from project_config import Config

class Toolbox:
    """
    Shared tools for ADK agents.
    """
    def __init__(self):
        self.ddgs = DDGS()
        self.db = Database()
        genai.configure(api_key=Config().GOOGLE_API_KEY)

    def search_web(self, query):
        """
        Tool: Search the web for information.
        """
        try:
            results = list(self.ddgs.text(query, max_results=5))
            return json.dumps(results)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def check_domains(self, keywords):
        """
        Tool: Mock domain availability check.
        In a real scenario, this would hit a Namecheap/GoDaddy API.
        """
        tlds = ['.com', '.io', '.co', '.ai', '.net']
        results = []
        for kw in keywords[:5]: # limit checks
            clean_kw = kw.replace(" ", "")
            for tld in tlds:
                domain = f"{clean_kw}{tld}"
                # Mock logic: if it's too short, it's taken
                available = len(domain) > 8 
                if available:
                    results.append(domain)
        return json.dumps(results)
    
    def log_agent_action(self, agent_name, action, details):
        print(f"[{agent_name}] {action}: {details}")
