import sqlite3
import os

db_path = r"c:\Users\Admin\.gemini\antigravity\scratch\weekly_content_system\memory\weekly_content.db"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if embeddings table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        cursor.execute("SELECT count(*) FROM embeddings;")
        count = cursor.fetchone()[0]
        print(f"SUCCESS: 'embeddings' table found with {count} records.")
    else:
        print("ERROR: 'embeddings' table does not exist.")
        
    conn.close()
except Exception as e:
    print(f"ERROR: Database check failed: {e}")
