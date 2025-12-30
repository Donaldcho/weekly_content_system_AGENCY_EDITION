from backend.database import Database
import sqlite3

db = Database()
urn = "urn:li:organization:110526930"

with sqlite3.connect(db.db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE social_tokens SET user_id = ? WHERE platform = 'LinkedIn'", (urn,))
    conn.commit()
    print(f"Updated LinkedIn user_id to {urn}")
