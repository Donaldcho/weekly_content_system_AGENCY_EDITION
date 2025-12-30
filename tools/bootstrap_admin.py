from backend.database import Database
import sys
import os

# Add path
sys.path.append(os.getcwd())

print("Bootstrapping Admin User...")
db = Database()
# Create a fresh admin
# We use a unique name to avoid conflict with "Admin User" if it exists without password
username = "SuperAdmin"
password = "password123"

if db.add_user(username, "admin", password):
    print(f"SUCCESS: Created user '{username}' with password '{password}'")
else:
    print(f"User '{username}' already exists. Trying to reset...")
    db.delete_user(username)
    db.add_user(username, "admin", password)
    print(f"SUCCESS: Reset user '{username}' with password '{password}'")

print("You can now login with these credentials.")
