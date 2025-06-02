import streamlit as st
import json
import os
from pathlib import Path
import database as db

# Get users from database
def get_users():
    users = db.load_users()
    # Convert to dictionary format for authentication
    users_dict = {}
    for user in users:
        if user["status"] == "Active":  # Only include active users
            # Store username in lowercase for case-insensitive comparison
            users_dict[user["username"].lower()] = {
                "password": user.get("password", "password123"),  # Default password if not set
                "role": user["role"],
                "display_name": user["name"],
                "email": user["email"],
                "original_username": user["username"]  # Store original username for session state
            }
    return users_dict

def authenticate_user(username, password):
    """
    Authenticate a user with username and password
    
    Args:
        username (str): The username
        password (str): The password
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    USERS = get_users()
    # Convert input username to lowercase for case-insensitive comparison
    username_lower = username.lower()
    
    if username_lower in USERS and USERS[username_lower]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = USERS[username_lower]["original_username"]  # Use original username
        st.session_state.role = USERS[username_lower]["role"]
        st.session_state.display_name = USERS[username_lower]["display_name"]
        
        # Update last login time
        db.update_user_last_login(USERS[username_lower]["original_username"])
        
        return True
    return False

def logout_user():
    """
    Log out the current user by resetting session state
    """
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.display_name = ""

def get_user_info(username=None):
    """Get user information from the database"""
    USERS = get_users()
    if username is None and "username" in st.session_state:
        username = st.session_state.username
    
    if username in USERS:
        return {
            "username": username,
            "role": USERS[username]["role"],
            "display_name": USERS[username]["display_name"],
            "email": USERS[username]["email"]
        }
    return None

def get_all_users():
    """Get all users from the database"""
    return db.load_users()
