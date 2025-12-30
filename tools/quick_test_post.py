from backend.linkedin_poster import post_to_linkedin
import datetime

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
content = f"Hello LinkedIn! This is a test post from the DeviceterraSM Content System. Time: {timestamp} (Verification Run)"

print(f"Attempting to post: {content}")
success, result = post_to_linkedin(content)

if success:
    print(f"SUCCESS! Post ID: {result}")
else:
    print(f"FAILURE: {result}")
