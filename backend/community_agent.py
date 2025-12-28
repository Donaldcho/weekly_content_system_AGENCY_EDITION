import google.generativeai as genai
import random
from datetime import datetime
from project_config import Config
from backend.database import Database

class CommunityAgent:
    """
    The Community Agent handles Unified Inbox logic.
    It simulates a stream of cross-platform messages and provides AI Smart Replies.
    """
    def __init__(self):
         genai.configure(api_key=Config().GOOGLE_API_KEY)
         self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
         self.db = Database()
         
         # Mock Data Store
         self.messages = [
             {
                 "id": 1,
                 "author": "Sarah_VP",
                 "platform": "LinkedIn",
                 "avatar": "💼",
                 "preview": "Hey, saw your post about AI...",
                 "full_text": "Hey, saw your post about AI Agents. We're looking to implement something similar next quarter. Do you offer consulting?",
                 "timestamp": "10:30 AM",
                 "read": False,
                 "folder": "inbox"
             },
             {
                 "id": 2,
                 "author": "MikeTech",
                 "platform": "Twitter",
                 "avatar": "🐦",
                 "preview": "This is completely wrong...",
                 "full_text": "This is completely wrong. LLMs hallucinate way too much for this to be viable in enterprise.",
                 "timestamp": "09:45 AM",
                 "read": True,
                 "folder": "inbox"
             },
             {
                 "id": 3,
                 "author": "FanBoy99",
                 "platform": "Instagram",
                 "avatar": "📸",
                 "preview": "Love the new visuals! 🔥",
                 "full_text": "Love the new visuals! 🔥 What tool are you using for the cover art?",
                 "timestamp": "Yesterday",
                 "read": False,
                 "folder": "inbox"
             }
         ]

    def fetch_messages(self, folder="inbox"):
        """
        Returns messages for the requested folder.
        """
        return [m for m in self.messages if m['folder'] == folder]
    
    def generate_smart_reply(self, message):
        """
        Uses Gemini to generate 3 distinct reply options based on context.
        """
        prompt = f"""
        You are a Social Media Manager for a tech brand ("Deviceterra").
        Draft 3 short, professional, and engaging replies to the following message.
        
        MESSAGE CONTEXT:
        Platform: {message['platform']}
        Author: {message['author']}
        Text: "{message['full_text']}"
        
        TONE: Helpful, slightly witty, professional.

        Return strictly a list of strings:
        - Option 1 (Professional)
        - Option 2 (Casual/Grateful)
        - Option 3 (Question/Engagement)
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # --- COST LOGGING ---
            try:
                usage = response.usage_metadata
                if usage:
                    self.db.log_usage(
                        agent_name="CommunityAgent",
                        model="gemini-2.0-flash-exp",
                        input_tokens=usage.prompt_token_count,
                        output_tokens=usage.candidates_token_count
                    )
            except Exception as e:
                print(f"Failed to log usage: {e}")
                
            # Simple text parsing since we asked for a list format, or we can use JSON mode to be safe.
            # Let's hope Gemini 2 is smart enough to just give text, but for robustness let's just use text.
            replies = [line.strip("- ").strip() for line in response.text.split('\n') if line.strip().startswith("-")]
            if not replies:
                 # Fallback if formatting fails
                 replies = ["Thanks for reaching out!", "Great point, thanks for sharing.", "Could you elaborate?"]
            return replies[:3]
        except Exception as e:
            print(f"Smart Reply Error: {e}")
            return ["Error generating reply."]
    
    def mark_as_read(self, msg_id):
        for m in self.messages:
            if m['id'] == msg_id:
                m['read'] = True

    def send_reply(self, msg_id, reply_text):
        """
        Simulates sending a reply.
        """
        # In real app, this calls LinkedIn/Twitter API
        print(f"Sending to {msg_id}: {reply_text}")
        # Archive message to show "Done" state
        for m in self.messages:
            if m['id'] == msg_id:
                m['folder'] = 'done'
                m['read'] = True
        return True
