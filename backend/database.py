import sqlite3
import json
from datetime import datetime, date, time
from project_config import Config
import contextlib

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)

class Database:
    def __init__(self):
        # Ensure we use the centralized path from Config
        self.db_path = Config().DB_PATH 
        
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            
            # Brand Settings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brand_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    content TEXT
                )
            ''')
            
            # Posts/Schedule Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    platform TEXT,
                    content TEXT,  -- JSON string for multiple fields if needed
                    scheduled_time TIMESTAMP,
                    status TEXT, -- 'scheduled', 'posted'
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    impressions INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migration for existing tables: Individual try-except blocks to prevent early exits
            valid_cols = [
                ("likes", "INTEGER DEFAULT 0"),
                ("comments", "INTEGER DEFAULT 0"),
                ("impressions", "INTEGER DEFAULT 0"),
                ("engagement_rate", "REAL DEFAULT 0.0"),
                ("social_id", "TEXT"),
                ("id_token", "TEXT"),
                ("scopes", "TEXT")
            ]
            
            for col_name, col_def in valid_cols:
                try:
                    cursor.execute(f"ALTER TABLE posts ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass # Column already exists
                    
            try:
                cursor.execute("ALTER TABLE social_tokens ADD COLUMN id_token TEXT")
                cursor.execute("ALTER TABLE social_tokens ADD COLUMN scopes TEXT")
            except Exception:
                pass
            
            # Embeddings Table for RAG
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    chunk_index INTEGER,
                    content TEXT,
                    embedding_json TEXT -- JSON array of floats
                )
            ''')
            
            # Drafts Table for Project Saving
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS drafts (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    topic TEXT,
                    data TEXT, -- JSON structure of the plan
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Vault Table for Asset Management (Operations Center)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    file_path TEXT,
                    asset_type TEXT, -- 'generated', 'upload'
                    tags TEXT, -- comma separated
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Social Tokens Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_tokens (
                    platform TEXT PRIMARY KEY, -- 'LinkedIn', 'Facebook'
                    access_token TEXT,
                    refresh_token TEXT,
                    expires_at TIMESTAMP,
                    user_id TEXT, -- The user's specific LinkedIn ID
                    id_token TEXT, -- OpenID Connect ID Token (JWT)
                    scopes TEXT    -- Permissions granted
                )
            ''')
            
            # Migration
            try:
                cursor.execute("ALTER TABLE social_tokens ADD COLUMN id_token TEXT")
                cursor.execute("ALTER TABLE social_tokens ADD COLUMN scopes TEXT")
            except:
                pass
            
            # System Settings (for BYOK credentials)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # --- AGENCY MULTI-TENANCY ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    logo_path TEXT,
                    industry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Seed Default Client if empty (Migration Step 1)
            cursor.execute("SELECT COUNT(*) FROM clients")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO clients (name, industry) VALUES (?, ?)", ("Default Agency", "General"))
                default_client_id = cursor.lastrowid
                print(f"DEBUG: Created Default Client ID: {default_client_id}")
            else:
                cursor.execute("SELECT id FROM clients ORDER BY id ASC LIMIT 1")
                default_client_id = cursor.fetchone()[0]

            # --- USERS (Update) ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    role TEXT, -- 'admin', 'editor', 'writer'
                    password_hash TEXT,
                    client_id INTEGER DEFAULT 1, -- Default to First Client
                    agency_role TEXT -- 'super_admin', 'agency_user', 'client_viewer'
                )
            ''')
            
            # Migration: Add columns to existing tables
            try: cursor.execute("ALTER TABLE users ADD COLUMN client_id INTEGER DEFAULT 1") 
            except: pass
            try: cursor.execute("ALTER TABLE users ADD COLUMN agency_role TEXT") 
            except: pass

            # --- API LOGS ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent_name TEXT, 
                    model TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost_usd REAL,
                    client_id INTEGER DEFAULT 1
                )
            ''')
            try: cursor.execute("ALTER TABLE api_logs ADD COLUMN client_id INTEGER DEFAULT 1")
            except: pass
            
            # --- POSTS ---
            try: cursor.execute("ALTER TABLE posts ADD COLUMN client_id INTEGER DEFAULT 1")
            except: pass

            # --- ASSETS ---
            try: cursor.execute("ALTER TABLE assets ADD COLUMN client_id INTEGER DEFAULT 1")
            except: pass

            
            conn.commit()

    # --- Social Tokens ---
    def save_token(self, platform, access_token, refresh_token, expires_at, user_id, id_token=None, scopes=None):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO social_tokens (platform, access_token, refresh_token, expires_at, user_id, id_token, scopes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (platform, access_token, refresh_token, expires_at, user_id, id_token, scopes))
            conn.commit()

    def get_token(self, platform):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM social_tokens WHERE platform = ?", (platform,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def delete_token(self, platform):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM social_tokens WHERE platform = ?", (platform,))
            conn.commit()

    # --- Brand Settings ---
    def get_brand_settings(self):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM brand_settings WHERE id = 1")
            row = cursor.fetchone()
            if row:
                content = row[0]
                # Try to parse as JSON, if it looks like it
                try:
                    return json.loads(content)
                except:
                    # Legacy string format support
                    return content
            # Default fallback if empty
            return {
                "name": "Deviceterra",
                "industry": "AI",
                "tone": "Professional",
                "mission": "Empowering the future.",
                "colors": []
            }

    def save_brand_settings(self, content):
        # If content is a dict, serialize it
        if isinstance(content, dict):
            content = json.dumps(content, cls=DateTimeEncoder)
            
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO brand_settings (id, content) VALUES (1, ?)", (content,))
            conn.commit()

    # --- Posts/Schedule ---
    def get_scheduled_posts(self, client_id=1):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE status = 'scheduled' AND client_id = ? ORDER BY scheduled_time ASC", (client_id,))
            rows = cursor.fetchall()
            
            requests = []
            for row in rows:
                data = json.loads(row['content'])
                data['id'] = row['id']
                data['status'] = row['status']
                data['scheduled_time'] = row['scheduled_time']
                requests.append(data)
            return requests

    def get_next_free_slot(self):
        """
        Finds the first date (starting from tomorrow) that has no posts.
        """
        from datetime import date, timedelta
        start_date = date.today() + timedelta(days=1)
        
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            
            while True:
                date_str = start_date.isoformat()
                # Check for any post on this day (ignoring time)
                cursor.execute("SELECT COUNT(*) FROM posts WHERE substr(scheduled_time, 1, 10) = ?", (date_str,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    return f"{date_str}T09:00:00" # Default 9 AM
                
                start_date += timedelta(days=1)
                
                # Safety break
                if (start_date - date.today()).days > 60:
                    return f"{date_str}T09:00:00"

    def get_occupied_slots(self):
        """Returns a list of all occupied ISO timestamps from scheduled/posted posts."""
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT scheduled_time FROM posts WHERE status IN ('scheduled', 'posted') AND scheduled_time IS NOT NULL")
            return [row[0] for row in cursor.fetchall()]
            
    def get_all_posts(self):
        """Retrieves all posts regardless of status (Draft, Scheduled, Posted)"""
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts ORDER BY scheduled_time ASC")
            rows = cursor.fetchall()
            
            requests = []
            for row in rows:
                try:
                    data = json.loads(row['content'])
                    data['id'] = row['id']
                    data['status'] = row['status']
                    data['scheduled_time'] = row['scheduled_time']
                    requests.append(data)
                except:
                    continue # Skip corrupted rows
            return requests

    def add_scheduled_post(self, post_data):
        with contextlib.closing(self.get_connection()) as conn:
            post_id = post_data.get('id')
            # Store the raw scheduled time and status separately for querying, rest in content blob
            scheduled_time = post_data.get('scheduled_time')
            status = post_data.get('status', 'scheduled')
            
            # Store full blob
            content_json = json.dumps(post_data, cls=DateTimeEncoder)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO posts (id, platform, content, scheduled_time, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (post_id, "Multi", content_json, scheduled_time, status))
            conn.commit()
            
    def update_post_status(self, post_id, new_status):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE posts SET status = ? WHERE id = ?", (new_status, post_id))
            conn.commit()
            
    def update_post(self, post_id, updated_data):
        """Full update of a post's content and metadata"""
        with contextlib.closing(self.get_connection()) as conn:
            # We need to preserve the ID but update everything else
            # First, fetch existing to merge if needed, but for now assume full overwrite of content
            # Recalculate content json
            content_json = json.dumps(updated_data, cls=DateTimeEncoder)
            scheduled_time = updated_data.get('scheduled_time')
            status = updated_data.get('status', 'scheduled')
            
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE posts 
                SET content = ?, scheduled_time = ?, status = ?
                WHERE id = ?
            ''', (content_json, scheduled_time, status, post_id))
            conn.commit()

    def mark_as_posted(self, post_id, social_id=None):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            if social_id:
                cursor.execute("UPDATE posts SET status = 'posted', social_id = ? WHERE id = ?", (social_id, post_id))
            else:
                cursor.execute("UPDATE posts SET status = 'posted' WHERE id = ?", (post_id,))
            conn.commit()

    def delete_post(self, post_id):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()

    def update_post_date(self, post_id, new_date_iso):
        """Updates just the scheduled time for Drag & Drop"""
        with contextlib.closing(self.get_connection()) as conn:
            # We also need to update the content blob's time
            cursor = conn.cursor()
            # First get content
            cursor.execute("SELECT content FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                content = json.loads(row[0])
                content['scheduled_time'] = new_date_iso
                new_blob = json.dumps(content, cls=DateTimeEncoder)
                
                cursor.execute("UPDATE posts SET scheduled_time = ?, content = ? WHERE id = ?", (new_date_iso, new_blob, post_id))
                conn.commit()

    def get_history(self, limit=50):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE status = 'posted' ORDER BY scheduled_time DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                data = json.loads(row['content'])
                data['id'] = row['id']
                data['status'] = row['status']
                history.append(data)
            return history
            
    def get_top_performing_posts(self, limit=3):
        """Fetches top posts based on engagement rate."""
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM posts 
                WHERE status = 'posted' 
                ORDER BY engagement_rate DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
            top_posts = []
            for row in rows:
                try:
                    data = json.loads(row['content'])
                    # Inject metrics into the dictionary for the planner to see
                    data['metrics'] = {
                        'likes': row['likes'],
                        'comments': row['comments'],
                        'engagement_rate': row['engagement_rate']
                    }
                    data['topic'] = data.get('topic', 'Unknown') # Ensure topic exists
                    top_posts.append(data)
                except:
                    continue
            return top_posts

    def update_post_metrics(self, post_id, likes, comments, impressions, engagement_rate):
        """Updates social metrics for a post."""
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE posts 
                SET likes=?, comments=?, impressions=?, engagement_rate=? 
                WHERE id=?
            """, (likes, comments, impressions, engagement_rate, post_id))
            conn.commit()
            
    # --- Vault (Asset Management) ---
    def save_asset(self, filename, file_path, asset_type="generated", tags=""):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vault (filename, file_path, asset_type, tags)
                VALUES (?, ?, ?, ?)
            ''', (filename, file_path, asset_type, tags))
            conn.commit()
            
    def get_vault_assets(self, filter_type=None):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT * FROM vault ORDER BY created_at DESC"
            params = ()
            if filter_type:
                query = "SELECT * FROM vault WHERE asset_type = ? ORDER BY created_at DESC"
                params = (filter_type,)
                
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_asset(self, asset_id):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vault WHERE id = ?", (asset_id,))
            conn.commit()

    # --- Project Drafts ---
    def save_draft(self, draft_id, name, topic, plan_data):
        """Saves a weekly plan as a draft."""
        data_json = json.dumps(plan_data, cls=DateTimeEncoder)
        updated_at = datetime.now()
        
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO drafts (id, name, topic, data, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (draft_id, name, topic, data_json, updated_at))
            conn.commit()
            
    def get_drafts(self):
        """Returns metadata of all drafts."""
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, topic, updated_at FROM drafts ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def load_draft(self, draft_id):
        """Returns the full data for a draf."""
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row['data'])
            return None
            
    def delete_draft(self, draft_id):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            conn.commit()

    # --- System Settings (BYOK) ---
    def get_system_setting(self, key):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None

    def save_system_setting(self, key, value):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    # --- RBAC ---
    # --- RBAC & AUTH ---
    def _hash_password(self, password):
        """Hashes password using SHA256 + Salt."""
        import hashlib
        import os
        salt = os.urandom(32) # 32 bytes
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ":" + pwd_hash.hex()

    def _verify_password(self, stored_password, provided_password):
        """Verifies a stored password against provided input."""
        import hashlib
        try:
            salt_hex, hash_hex = stored_password.split(":")
            salt = bytes.fromhex(salt_hex)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
            return pwd_hash.hex() == hash_hex
        except:
            return False

    def get_users(self):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users") # Exclude hash
            return [dict(row) for row in cursor.fetchall()]

    def add_user(self, username, role, password):
        password_hash = self._hash_password(password)
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)", (username, role, password_hash))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False 

    def authenticate_user(self, username, password):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                # Legacy support for users without passwords (migrated)
                if not user['password_hash']:
                     # If no password set, allow any password (or force reset? for now allow dev mode access if needed, or fail)
                     # Let's fail secure: requires password.
                     # But for dev convenience during migration, we might want to set a default.
                     return None
                
                if self._verify_password(user['password_hash'], password):
                    return dict(user)
                    
            return None

    def delete_user(self, username):
        # Prevent deleting the last Admin or strictly "Admin User" if desired, 
        # but for flexibility we just allow deletion (UI should warn).
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()

            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()

    # --- CLIENT MGMT (Agency) ---
    def get_clients(self):
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients")
            return [dict(row) for row in cursor.fetchall()]

    def add_client(self, name, industry="General"):
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO clients (name, industry) VALUES (?, ?)", (name, industry))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    # --- API LOGS ---
    def log_usage(self, agent_name, model, input_tokens, output_tokens, override_cost=None, client_id=1):
        """
        Logs API usage. Defaults to client_id=1 if not specified.
        """
        # Pricing Table (USD per 1M tokens) - Updated Dec 2025
        # Fallback to Flash rates if unknown
        PRICING = {
            'gemini-1.5-flash': {'input': 0.075, 'output': 0.30}, # Very cheap
            'gemini-2.0-flash-exp': {'input': 0.10, 'output': 0.40}, # Est.
            'gemini-1.5-pro':   {'input': 1.25,  'output': 5.00}, # Premium
            'gemini-3-pro-image-preview': {'input': 0, 'output': 0} # Handled by override
        }
        
        # Normalize model string
        model_key = 'gemini-1.5-flash' # Default
        for k in PRICING.keys():
            if k in model.lower():
                model_key = k
                break
                
        rates = PRICING[model_key]
        
        if override_cost is not None:
             total_cost = override_cost
        else:
            cost_input = (input_tokens / 1_000_000) * rates['input']
            cost_output = (output_tokens / 1_000_000) * rates['output']
            total_cost = cost_input + cost_output
        
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            # Try/Except to handle potential schema mismatch if migration failed silently (though we ran DDL above)
            try:
                cursor.execute('''
                    INSERT INTO api_logs (agent_name, model, input_tokens, output_tokens, cost_usd, client_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (agent_name, model, input_tokens, output_tokens, total_cost, client_id))
            except:
                # Fallback for legacy schema just in case
                 cursor.execute('''
                    INSERT INTO api_logs (agent_name, model, input_tokens, output_tokens, cost_usd)
                    VALUES (?, ?, ?, ?, ?)
                ''', (agent_name, model, input_tokens, output_tokens, total_cost))
            conn.commit()
            
    def get_api_usage(self):
        """Returns log entries for the dashboard."""
        with contextlib.closing(self.get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM api_logs ORDER BY timestamp DESC LIMIT 100")
            return [dict(row) for row in cursor.fetchall()]
            
    def get_total_cost(self):
        """Returns the sum of all costs."""
        with contextlib.closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(cost_usd) FROM api_logs")
            result = cursor.fetchone()[0]
            return result if result else 0.0
