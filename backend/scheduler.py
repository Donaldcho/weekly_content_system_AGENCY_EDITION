from datetime import datetime, timedelta
from backend.database import Database
import streamlit as st

def get_calendar_events():
    """
    Fetches posts and formats them for FullCalendar.js
    """
    if 'db' not in st.session_state:
        st.session_state.db = Database()
        
    posts = st.session_state.db.get_all_posts() 
    
    calendar_events = []
    
    for post in posts:
        # 1. Color Logic based on Platform & Status
        color = "#808080" # Default Grey (Draft)
        
        status = post.get('status', 'draft').lower()
        platform = post.get('platform', 'Multi')
        
        if status == 'posted' or status == 'published':
            color = "#00CC96" # Green
        elif status == 'scheduled':
            if platform == 'LinkedIn':
                color = "#0077B5" # LinkedIn Blue
            elif platform == 'Facebook':
                color = "#1877F2" # FB Blue
            elif platform == 'Instagram':
                color = "#E1306C" # Insta Pink
            elif platform == 'Twitter':
                color = "#1DA1F2" # Twitter Blue
        
        # 2. Build Event Object
        # Check date
        start = post.get('scheduled_time')
        if not start:
            # If TBD, we might skip or put it on today?
            # For calendar, we need a date. If no date, it's a "queue" item, handled separately.
            continue
            
        # Ensure ISO format (YYYY-MM-DDTHH:MM:SS)
        # Our DB stores it as ISO usually.
            
        event = {
            "id": post['id'], # Standard FullCalendar ID
            "title": f"{platform}: {post.get('topic') or post.get('linkedin_draft', 'Post')[:20]}...",
            "start": start, 
            "end": start,   # For social posts, start = end usually
            "resourceId": post['id'],
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "status": status.title(),
                "platform": platform,
                "content": post.get('linkedin_draft') or post.get('content') or "",
                "image": post.get('image_path'),
                "agent_thought": post.get('agent_thought'),
                "agent_reasoning": post.get('agent_reasoning')
            }
        }
        calendar_events.append(event)
        
    return calendar_events
