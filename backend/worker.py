import time
import json
from datetime import datetime
from backend.database import Database
from backend.linkedin_poster import post_to_linkedin
from backend.facebook_poster import post_to_facebook

def run_worker_cycle():
    """
    Checks for posts that need to be published.
    """
    db = Database()
    
    # Fetch all scheduled posts
    # Note: get_scheduled_posts() specifically filters for 'scheduled'
    scheduled_posts = db.get_scheduled_posts()
    
    now = datetime.now()
    processed_count = 0
    
    for post in scheduled_posts:
        # Check if it's time to post
        scheduled_time_str = post.get('scheduled_time')
        if not scheduled_time_str:
            continue
            
        try:
            # Handle possible variations in timestamp format
            scheduled_time = datetime.fromisoformat(scheduled_time_str)
        except ValueError:
            try:
                # Fallback for simple date format
                scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
            except:
                print(f"ERROR: Could not parse time for post {post['id']}: {scheduled_time_str}")
                continue
        
        if scheduled_time <= now:
            print(f"[*] Processing post {post['id']} for {post.get('platform', 'Multi')}...")
            
            # 2. Call Posting APIs based on Platform
            platform = post.get('platform', 'Multi')
            results = []
            final_social_id = None
            
            # Helper to consolidate success/fail
            def process_result(success, result, plat_name):
                nonlocal final_social_id
                if success:
                    print(f"    [+] Successfully posted to {plat_name}! ID: {result}")
                    final_social_id = result # We use the last successful ID as primary ref
                    return True
                else:
                    print(f"    [-] Failed to post to {plat_name}: {result}")
                    return False

            overall_success = False

            if platform == 'LinkedIn' or platform == 'Multi':
                s, r = post_to_linkedin(content, image_path=image_path)
                if process_result(s, r, "LinkedIn"): overall_success = True

            if platform == 'Facebook' or platform == 'Multi':
                s, r = post_to_facebook(content, image_path=image_path)
                if process_result(s, r, "Facebook"): overall_success = True
            
            if overall_success:
                db.mark_as_posted(post['id'], social_id=final_social_id)
                processed_count += 1
                # We could implement a retry limit here or mark as failed
                # For now, let's just log it.
                
    return processed_count

if __name__ == "__main__":
    print("🚀 LinkedIn Scheduler Worker Started")
    print("Checking for scheduled posts every 30 seconds...")
    try:
        while True:
            try:
                count = run_worker_cycle()
                if count > 0:
                    print(f"Processed {count} posts in this cycle.")
            except Exception as e:
                print(f"CRITICAL WORKER ERROR: {e}")
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("Worker stopped.")
