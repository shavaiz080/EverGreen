import os
import json
import firebase_db

def main():
    """Migrate local data to Firebase"""
    print("Starting migration of local data to Firebase...")
    
    # Ensure Firebase is initialized
    try:
        firebase_db.initialize_firebase()
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return
    
    # Migrate data
    try:
        firebase_db.migrate_local_data_to_firebase()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        return
    
    print("\nNext steps:")
    print("1. Update your app.py to use firebase_db instead of database.py")
    print("2. Deploy your application")
    print("3. Share the link with your team")

if __name__ == "__main__":
    main()
