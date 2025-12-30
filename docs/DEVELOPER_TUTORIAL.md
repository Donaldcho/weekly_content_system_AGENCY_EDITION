# 👨‍💻 Developer Tutorial: Extending Deviceterra

So you want to modify the code? This guide covers the common tasks you'll likely want to do.

---

## 🧪 Tutorial 1: How to Add a New Agent
Let's say you want to add a **"Meme Agent"** that generates funny captions.

### Step 1: Create the Agent File
Create `backend/adk/agents/meme_lord.py`:

```python
from .base import BaseAdkAgent

class MemeLordAgent(BaseAdkAgent):
    def generate_caption(self, topic):
        prompt = f"""
        You are a viral meme expert.
        Topic: {topic}
        Task: Write a funny, sarcastic caption suitable for an image macro.
        Output JSON: {{ "caption": "..." }}
        """
        return self.generate(prompt, json_mode=True)
```

### Step 2: Register it in the Agency
Open `backend/adk/main.py` and register the new class:

```python
from .agents.meme_lord import MemeLordAgent # Import

class MarketingAgency:
    def __init__(self):
        # ... existing agents ...
        self.meme_lord = MemeLordAgent("MemeLord") # Initialize
    
    def create_meme(self, topic):
        return self.meme_lord.generate_caption(topic)
```

### Step 3: Call it from the UI
Open `ui/generate.py` and add a button:

```python
if st.button("Generate Meme Caption"):
    from backend.adk.main import MarketingAgency
    agency = MarketingAgency()
    caption = agency.create_meme("Monday Morning")
    st.write(caption)
```

---

## 🖥️ Tutorial 2: Adding a New Page
Want a "Analytics" dashboard?

1.  Create `ui/analytics.py`.
2.  Define a render function:
    ```python
    import streamlit as st
    def render_analytics_page():
        st.title("Analytics")
        st.write("Chart goes here...")
    ```
3.  Register it in `app.py`:
    ```python
    from ui.analytics import render_analytics_page
    
    # Inside the sidebar logic
    page = st.sidebar.radio("Navigation", ["Generate", "Analytics", ...])
    
    if page == "Analytics":
        render_analytics_page()
    ```

---

## 💾 Tutorial 3: Modifying the Database
The database uses raw SQLite in `backend/database.py`.

1.  Open `backend/database.py`.
2.  Find `_init_db(self)`.
3.  Add your new column or table to the SQL:
    ```sql
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY,
        views INTEGER
    )
    ```
4.  **Important**: Since this is SQLite, if the file `weekly_content.db` already exists, it won't auto-update. You must delete the `.db` file (resetting data) or write a migration script to `ALTER TABLE`.

---

## 🛠️ Best Practices
1.  **Use the Prompt Registry**: Don't hardcode prompts in Python. Put them in `assets/prompts.json` and use `PromptRegistry`.
2.  **Environment Variables**: Never commit API keys. Use `.env`.
3.  **Error Handling**: Wrap external API calls (Gemini/LinkedIn) in `try/except` blocks to prevent the UI from crashing.
