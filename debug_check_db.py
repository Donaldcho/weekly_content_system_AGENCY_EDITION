import sqlite3
import os

files = [
    "weekly_content.db",
    "memory/weekly_content.db"
]

for db_path in files:
    print(f"\nScanning: {db_path}")
    if not os.path.exists(db_path):
        print("  [MISSING] File not found.")
        continue
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Tokens
        try:
            cursor.execute("SELECT platform, user_id FROM social_tokens")
            rows = cursor.fetchall()
            if rows:
                print(f"  [TOKENS] Found {len(rows)} tokens:")
                for row in rows:
                    print(f"    - {row}")
            else:
                print("  [TOKENS] Table exists but EMPTY.")
        except Exception as e:
            print(f"  [TOKENS] Error: {e}")
            
        # Check Posts
        try:
            cursor.execute("SELECT count(*) FROM posts")
            count = cursor.fetchone()[0]
            print(f"  [POSTS] Count: {count}")
        except:
            print("  [POSTS] Error or table missing")

        conn.close()
    except Exception as e:
        print(f"  [ERROR] Failed to open DB: {e}")
