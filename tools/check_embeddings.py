import sqlite3
import os

files = [
    "weekly_content.db",
    "memory/weekly_content.db"
]

for db_path in files:
    print(f"\nScanning: {db_path}")
    if not os.path.exists(db_path):
        continue
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT count(*) FROM embeddings")
            count = cursor.fetchone()[0]
            print(f"  [EMBEDDINGS] Count: {count}")
        except:
            print("  [EMBEDDINGS] Table missing or error")

        conn.close()
    except:
        pass
