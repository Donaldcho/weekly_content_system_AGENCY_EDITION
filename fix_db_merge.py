import sqlite3
import shutil
import os
from datetime import datetime

source_db = "weekly_content.db"
target_db = "memory/weekly_content.db"
backup_db = "memory/weekly_content.db.bak"

def merge_db():
    if not os.path.exists(source_db):
        print(f"Source DB {source_db} not found!")
        return
        
    if not os.path.exists(target_db):
        print(f"Target DB {target_db} not found!")
        return

    # Backup first
    print(f"Backing up {target_db}...")
    shutil.copy2(target_db, backup_db)
    
    try:
        src_conn = sqlite3.connect(source_db)
        src_conn.row_factory = sqlite3.Row
        src_cursor = src_conn.cursor()
        
        tgt_conn = sqlite3.connect(target_db)
        tgt_cursor = tgt_conn.cursor()
        
        # 1. Merge Social Tokens
        print("Merging Social Tokens...")
        src_cursor.execute("SELECT * FROM social_tokens")
        tokens = src_cursor.fetchall()
        for token in tokens:
            row = dict(token)
            # Use REPLACE to overwrite empty/old
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?'] * len(row))
            sql = f"INSERT OR REPLACE INTO social_tokens ({columns}) VALUES ({placeholders})"
            tgt_cursor.execute(sql, list(row.values()))
        print(f"  Merged {len(tokens)} tokens.")
            
        # 2. Merge Posts
        print("Merging Posts...")
        src_cursor.execute("SELECT * FROM posts")
        posts = src_cursor.fetchall()
        count = 0
        for post in posts:
            row = dict(post)
            # Check if exists in target to avoid overwriting newer?
            # Assuming Root has valid posts and Target has 0.
            # But let's check ID.
            tgt_cursor.execute("SELECT id FROM posts WHERE id = ?", (row['id'],))
            if not tgt_cursor.fetchone():
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['?'] * len(row))
                sql = f"INSERT INTO posts ({columns}) VALUES ({placeholders})"
                tgt_cursor.execute(sql, list(row.values()))
                count += 1
        print(f"  Merged {count} posts.")
        
        # 3. Merge Brand Settings
        print("Merging Brand Settings...")
        src_cursor.execute("SELECT * FROM brand_settings")
        settings = src_cursor.fetchall()
        for setting in settings:
             row = dict(setting)
             columns = ', '.join(row.keys())
             placeholders = ', '.join(['?'] * len(row))
             sql = f"INSERT OR REPLACE INTO brand_settings ({columns}) VALUES ({placeholders})"
             tgt_cursor.execute(sql, list(row.values()))
        print(f"  Merged settings.")

        tgt_conn.commit()
        src_conn.close()
        tgt_conn.close()
        print("\nMerge Complete!")
        
    except Exception as e:
        print(f"Merge Failed: {e}")
        # Restore?
        print("Restoring backup...")
        shutil.copy2(backup_db, target_db)

if __name__ == "__main__":
    merge_db()
