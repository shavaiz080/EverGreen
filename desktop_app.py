import os
import sys
import subprocess
import threading
import webbrowser
import time
import socket
from tkinter import Tk, Label, Button, Frame, PhotoImage
import tkinter.font as tkfont

def find_free_port():
    """Find a free port on localhost"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_streamlit():
    """Run the Streamlit app in a separate process"""
    port = find_free_port()
    os.environ['STREAMLIT_SERVER_PORT'] = str(port)
    
    # Hide Streamlit's menu and footer
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Run Streamlit
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
    process = subprocess.Popen(streamlit_cmd, stdout=subprocess.PIPE)
    
    # Wait for Streamlit to start
    time.sleep(3)
    
    # Open browser
    webbrowser.open(f'http://localhost:{port}')
    
    return process, port

class EverGreenDesktopApp:
    def __init__(self, root):
        self.root = root
        self.streamlit_process = None
        self.port = None
        
        # Configure the window
        self.root.title("EverGreen Power Dashboard")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set background color
        self.root.configure(bg="#f0f2f6")
        
        # Create a frame
        self.frame = Frame(root, bg="#f0f2f6")
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create title
        title_font = tkfont.Font(family="Arial", size=18, weight="bold")
        self.title_label = Label(
            self.frame, 
            text="EverGreen Power Dashboard", 
            font=title_font,
            bg="#f0f2f6",
            fg="#0e1117"
        )
        self.title_label.pack(pady=(10, 20))
        
        # Create subtitle
        subtitle_font = tkfont.Font(family="Arial", size=12)
        self.subtitle_label = Label(
            self.frame, 
            text="Solar System Lead Management", 
            font=subtitle_font,
            bg="#f0f2f6",
            fg="#0e1117"
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Create launch button
        button_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.launch_button = Button(
            self.frame, 
            text="Launch Dashboard", 
            command=self.launch_app,
            font=button_font,
            bg="#FF4B4B",
            fg="white",
            activebackground="#FF2B2B",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.launch_button.pack(pady=10)
        
        # Create exit button
        self.exit_button = Button(
            self.frame, 
            text="Exit", 
            command=self.on_close,
            font=button_font,
            bg="#0e1117",
            fg="white",
            activebackground="#1e2127",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.exit_button.pack(pady=10)
        
        # Status label
        self.status_label = Label(
            self.frame, 
            text="Ready to launch", 
            bg="#f0f2f6",
            fg="#0e1117"
        )
        self.status_label.pack(pady=(20, 0))
    
    def launch_app(self):
        """Launch the Streamlit app"""
        if self.streamlit_process is None:
            self.status_label.config(text="Starting dashboard...")
            self.root.update()
            
            # Run Streamlit in a separate thread
            def start_streamlit():
                self.streamlit_process, self.port = run_streamlit()
                self.root.after(0, lambda: self.status_label.config(text=f"Dashboard running on port {self.port}"))
            
            threading.Thread(target=start_streamlit).start()
            self.launch_button.config(text="Open in Browser", command=self.open_browser)
        else:
            self.open_browser()
    
    def open_browser(self):
        """Open the app in a browser"""
        if self.port:
            webbrowser.open(f'http://localhost:{self.port}')
    
    def on_close(self):
        """Clean up and close the application"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
        self.root.destroy()

def main():
    root = Tk()
    app = EverGreenDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
