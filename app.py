import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import local_db as db

# Set page configuration
st.set_page_config(
    page_title="EverGreen Power Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state variables
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'display_name' not in st.session_state:
        st.session_state.display_name = ""
    if 'notification' not in st.session_state:
        st.session_state.notification = None

    # Always load fresh data from the database on app startup
    st.session_state.leads = db.load_leads()
    st.session_state.users = db.load_users()
    st.session_state.next_lead_id = db.get_next_lead_id()


# Import modules
from auth import authenticate_user, logout_user
from views import router

# Initialize session state
init_session_state()


# Function to encode the image to base64 for inline HTML display
def get_base64_encoded_image(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


# Main application
def main():
    # Check authentication status
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Show dashboard based on role
        router()


def show_login_page():
    # Add CSS for styling
    st.markdown("""
    <style>
    /* Page background */
    .stApp {
        background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Fix container padding and width */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    /* Main content container */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    /* Logo and title */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .logo {
        width: 80px;
        margin-bottom: 10px;
    }
    
    .title {
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin-bottom: 5px;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 14px;
    }
    
    /* Form container */
    .form-container {
        background-color: white;
        border-radius: 8px;
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Welcome text */
    .welcome-text {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    /* Features section */
    .features {
        display: flex;
        justify-content: space-around;
        margin-top: 30px;
    }
    
    .feature {
        text-align: center;
        color: white;
        padding: 15px;
    }
    
    .feature-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .feature-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .feature-desc {
        font-size: 12px;
        opacity: 0.8;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        padding: 20px;
        font-size: 14px;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
    }
    
    /* Override Streamlit's default styling */
    .stTextInput > div > div > input {
        color: #333;
        height: 45px;
        font-size: 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
        padding-left: 15px;
        margin-bottom: 15px;
        box-shadow: none;
        background-color: rgba(255, 255, 255, 0.9);
    }
    
    .stTextInput > div {
        width: 80% !important;
        max-width: 400px;
        margin: 0 auto 10px auto;
    }
    
    .stButton {
        width: 80% !important;
        max-width: 400px;
        margin: 10px auto;
    }
    
    .stButton > button {
        background-color: #ff5a5f;
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px 15px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        height: 45px;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #ff3b40;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Logo and title
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{get_base64_encoded_image('images/logo.png')}" class="logo">
        <div class="title">EverGreen Power</div>
        <div class="subtitle">Sustainable Energy Solutions</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Form elements
    username = st.text_input("", placeholder="Enter your username", label_visibility="collapsed")
    password = st.text_input("", placeholder="Enter your password", type="password", label_visibility="collapsed")
    login_button = st.button("Sign In", use_container_width=True)
    
    if login_button:
        if authenticate_user(username, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    # Features section
    st.markdown("""
    <div class="features">
        <div class="feature">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Energy Tracking</div>
            <div class="feature-desc">Real-time monitoring</div>
        </div>
        <div class="feature">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Analytics</div>
            <div class="feature-desc">Performance metrics</div>
        </div>
        <div class="feature">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Cost Savings</div>
            <div class="feature-desc">Track your ROI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        &copy; 2025 EverGreen Power Solutions. All rights reserved.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
