from backend.database import Database
import sqlite3

db = Database()
urn = "urn:li:organization:110526930"

with sqlite3.connect(db.db_path) as conn:
    cursor = conn.cursor()
    # Check if entry exists
    cursor.execute("SELECT platform FROM social_tokens WHERE platform = 'LinkedIn'")
    if cursor.fetchone():
        cursor.execute("UPDATE social_tokens SET user_id = ? WHERE platform = 'LinkedIn'", (urn,))
        print(f"Updated existing LinkedIn entry to {urn}")
    else:
        # If it doesn't exist (unlikely), we create it with a dummy token so the fallback works
        cursor.execute("INSERT INTO social_tokens (platform, access_token, user_id, expires_at) VALUES (?, ?, ?, ?)", 
                      ("LinkedIn", "PENDING_RECONNECT", urn, "2099-01-01"))
        print(f"Created new LinkedIn entry with URN {urn}. PLEASE RECONNECT in UI to get real token.")
    conn.commit()
