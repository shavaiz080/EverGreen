import os
import json
from datetime import datetime
from pathlib import Path

# Define file paths for local data storage
DATA_DIR = "data"
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Ensure data directory exists
Path(DATA_DIR).mkdir(exist_ok=True)

def save_leads(leads):
    """Save leads to local JSON file"""
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=4)

def load_leads():
    """Load leads from local JSON file"""
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    """Save users to local JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_users():
    """Load users from local JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    
    # Return default users if no users exist
    default_users = [
        {"id": 1, "username": "admin", "name": "Admin User", "email": "admin@example.com", 
         "role": "admin", "status": "Active", "password": "admin@123",
         "last_login": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"id": 2, "username": "Syed.Adeel", "name": "Syed Adeel", "email": "syed.adeel@evergreen.com", 
         "role": "sales", "status": "Active", "password": "adeel123",
         "last_login": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"id": 3, "username": "Saad.Saleem", "name": "Saad Saleem", "email": "saad.saleem@evergreen.com", 
         "role": "sales", "status": "Active", "password": "saad123",
         "last_login": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"id": 4, "username": "Abdullah", "name": "Muhammad Abdullah", "email": "abdullah@evergreen.com", 
         "role": "sales", "status": "Active", "password": "abdullah123",
         "last_login": datetime.now().strftime("%Y-%m-%d %H:%M")}
    ]
    save_users(default_users)
    return default_users

def get_next_lead_id():
    """Get the next available lead ID"""
    leads = load_leads()
    if not leads:
        return 1
    return max(lead["id"] for lead in leads) + 1

def update_user_last_login(username):
    """Update the last login timestamp for a user"""
    users = load_users()
    for user in users:
        # Case-insensitive comparison for username
        if user["username"].lower() == username.lower():
            user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_users(users)

def get_next_customer_code():
    """Get the next available customer code in the format Evr001, Evr002, etc."""
    leads = load_leads()
    
    if not leads:
        return "Evr001"  # First customer code
    
    # Extract existing codes
    existing_codes = []
    for lead in leads:
        if "customer_code" in lead and lead["customer_code"].startswith("Evr"):
            try:
                # Extract the numeric part
                code_num = int(lead["customer_code"][3:])
                existing_codes.append(code_num)
            except ValueError:
                # Skip if the format is not as expected
                continue
    
    if not existing_codes:
        return "Evr001"  # No valid codes found
    
    # Get the next number and format it
    next_num = max(existing_codes) + 1
    return f"Evr{next_num:03d}"  # Format with leading zeros
