import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    if not firebase_admin._apps:
        # Check if running on a deployment platform that uses environment variables
        if os.environ.get('FIREBASE_CREDENTIALS'):
            # Use environment variable for credentials in production
            cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
            cred = credentials.Certificate(cred_dict)
        else:
            # Use local file for development
            cred_path = os.path.join(os.path.dirname(__file__), "firebase_credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                raise FileNotFoundError(
                    "Firebase credentials not found. Please create firebase_credentials.json or set FIREBASE_CREDENTIALS environment variable."
                )
        
        # Get database URL from environment or use default
        db_url = os.environ.get('FIREBASE_DATABASE_URL', 'https://evergreen-dashboard-default-rtdb.firebaseio.com/')
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })

# Initialize Firebase on module import
initialize_firebase()

# Leads functions
def save_leads(leads):
    """Save leads to Firebase"""
    ref = db.reference('/leads')
    ref.set(leads)

def load_leads():
    """Load leads from Firebase"""
    ref = db.reference('/leads')
    leads = ref.get()
    return leads if leads else []

# Users functions
def save_users(users):
    """Save users to Firebase"""
    ref = db.reference('/users')
    ref.set(users)

def load_users():
    """Load users from Firebase"""
    ref = db.reference('/users')
    users = ref.get()
    
    if not users:
        # Return default users if no users exist in the database
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
    
    return users

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

# Function to initialize the database with data from local files (for migration)
def migrate_local_data_to_firebase():
    """Migrate data from local JSON files to Firebase"""
    # Define file paths for local data storage
    DATA_DIR = "data"
    LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    
    # Migrate leads if local file exists
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'r') as f:
            local_leads = json.load(f)
            save_leads(local_leads)
            print(f"Migrated {len(local_leads)} leads to Firebase")
    
    # Migrate users if local file exists
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            local_users = json.load(f)
            save_users(local_users)
            print(f"Migrated {len(local_users)} users to Firebase")
