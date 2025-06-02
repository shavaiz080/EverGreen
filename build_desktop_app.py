import os
import sys
import shutil
import subprocess
import platform

def build_desktop_app():
    """Build the desktop application using PyInstaller"""
    print("Building EverGreen Power Dashboard desktop application...")
    
    # Ensure the data directory exists in the current directory
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Create spec file for PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('app.py', '.'),
        ('auth.py', '.'),
        ('views.py', '.'),
        ('admin_view.py', '.'),
        ('sales_view.py', '.'),
        ('database.py', '.'),
    ],
    hiddenimports=['streamlit', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EverGreen Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/evergreen_icon.ico' if os.path.exists('images/evergreen_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EverGreen Dashboard',
)
    """
    
    with open("evergreen_dashboard.spec", "w") as f:
        f.write(spec_content)
    
    # Create a simple icon for the application
    if not os.path.exists("images"):
        os.makedirs("images")
    
    # Run PyInstaller
    cmd = ["pyinstaller", "evergreen_dashboard.spec", "--clean"]
    subprocess.run(cmd)
    
    print("\nBuild completed!")
    print(f"You can find your desktop application in the 'dist/EverGreen Dashboard' directory")
    
    # Create a README file for the desktop app
    readme_content = """# EverGreen Power Dashboard - Desktop Edition

## Installation

1. Extract all files to a location of your choice
2. Run "EverGreen Dashboard.exe" to start the application

## Features

- Complete solar system lead management
- Role-based access control (admin/sales)
- Interactive dashboards and analytics
- Local data storage - your data stays on your computer

## Default Login Credentials

- Admin:
  - Username: admin
  - Password: admin@123

- Sales:
  - Username: Syed.Adeel
  - Password: adeel123

## Support

For support, please contact the development team.
"""
    
    with open("dist/EverGreen Dashboard/README.txt", "w") as f:
        f.write(readme_content)
    
    print("\nCreated README file with instructions")
    print("\nYour desktop application is ready to distribute!")

if __name__ == "__main__":
    build_desktop_app()
