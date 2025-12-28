from backend.database import Database
import sqlite3

db = Database()
with sqlite3.connect(db.db_path) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_tokens WHERE platform = 'LinkedIn'")
    row = cursor.fetchone()
    if row:
        print(f"Platform: {row['platform']}")
        print(f"User ID: '{row['user_id']}'")
        print(f"Token (First 10): {row['access_token'][:10]}...")
    else:
        print("No LinkedIn token found.")
