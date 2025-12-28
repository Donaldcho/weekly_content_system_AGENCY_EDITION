from backend.database import Database
import sqlite3

db = Database()
with sqlite3.connect(db.db_path) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM social_tokens WHERE platform = 'LinkedIn'")
    row = cursor.fetchone()
    if row:
        print(f"Stored user_id for LinkedIn: '{row['user_id']}'")
    else:
        print("No LinkedIn token found in DB.")
