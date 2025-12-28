import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @classmethod
    def get(cls, key, default=None):
        """
        Dynamic resolver:
        1. Checks streamlit session state db if available
        2. Checks environment variables
        3. Returns default
        """
        import streamlit as st
        from backend.database import Database
        
        # 1. Try DB via Session state or fresh instance
        try:
            # Check if we are in a streamlit context
            db = None
            try:
                if 'db' in st.session_state:
                    db = st.session_state.db
            except:
                pass
                
            if not db:
                db = Database()
            
            db_val = db.get_system_setting(key.lower())
            if db_val and cls._sanitize(db_val):
                return db_val
        except Exception as e:
            # print(f"DEBUG: Config.get({key}) DB error: {e}")
            pass

        # 2. Try Env
        env_val = os.getenv(key.upper())
        if env_val and cls._sanitize(env_val):
            return env_val
            
        return default

    @property
    def GOOGLE_API_KEY(self): return self.get("GOOGLE_API_KEY")
    
    # LinkedIn
    @property
    def LINKEDIN_CLIENT_ID(self): return self.get("LINKEDIN_CLIENT_ID")
    @property
    def LINKEDIN_CLIENT_SECRET(self): return self.get("LINKEDIN_CLIENT_SECRET")
    @property
    def LINKEDIN_ACCESS_TOKEN(self): return self.get("LINKEDIN_ACCESS_TOKEN")
    @property
    def LINKEDIN_PERSON_URN(self): return self.get("LINKEDIN_PERSON_URN")
    
    # Facebook
    @property
    def FACEBOOK_CLIENT_ID(self): return self.get("FACEBOOK_CLIENT_ID")
    @property
    def FACEBOOK_CLIENT_SECRET(self): return self.get("FACEBOOK_CLIENT_SECRET")
    @property
    def FACEBOOK_ACCESS_TOKEN(self): return self.get("FACEBOOK_ACCESS_TOKEN")
    @property
    def FACEBOOK_PAGE_ID(self): return self.get("FACEBOOK_PAGE_ID")
    
    # Authenticated User
    @property
    def ADMIN_USER(self): return self.get("ADMIN_USER")
    @property
    def ADMIN_PASSWORD(self): return self.get("ADMIN_PASSWORD")

    # Static Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEMORY_DIR = os.path.join(BASE_DIR, "memory")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
    
    COMPANY_INFO_PATH = os.path.join(MEMORY_DIR, "company_info.txt")
    HISTORY_PATH = os.path.join(MEMORY_DIR, "history.json")
    SCHEDULED_PATH = os.path.join(MEMORY_DIR, "scheduled.json")
    DB_PATH = os.path.join(MEMORY_DIR, "weekly_content.db")

    @staticmethod
    def _sanitize(val):
        """Helper to ensure we never return 'YOUR_' placeholders."""
        if not val or not isinstance(val, str): return None
        low = val.lower()
        if "your_" in low or "paste_" in low or (("key" in low or "token" in low or "secret" in low) and len(val) < 10): 
            return None
        return val

    @classmethod
    def validate(cls):
        # Instantiate to check properties
        instance = cls()
        if not instance.GOOGLE_API_KEY:
            print("WARNING: GOOGLE_API_KEY is missing")
