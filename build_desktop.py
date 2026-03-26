"""
Build script for GMRIT Results Scraper Desktop Executable
Packages the Flask application, templates, static files, and dependencies.
"""
import os
import subprocess
import sys
import shutil

def build():
    """Build the executable using PyInstaller"""
    print("Building GMRIT Results Scraper desktop executable...")
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Check for required directories
    if not os.path.exists(templates_dir) or not os.path.exists(static_dir):
        print("Error: templates or static directory missing!")
        return
        
    # Build command
    cmd = [
        'pyinstaller',
        '--name=GMRIT_Results_Scraper',
        '--onefile',
        '--windowed',
        f'--add-data={templates_dir}{os.pathsep}templates',
        f'--add-data={static_dir}{os.pathsep}static',
        '--hidden-import=webview.platforms.winforms',
        '--hidden-import=clr',
        '--collect-all=webview',
        '--collect-all=flask',
        '--collect-all=selenium',
        'desktop_main.py'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        subprocess.check_call(cmd)
        print("\nBuild successful! Executable is in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
    except Exception as e:
        print(f"\nUnexpected error during build: {e}")

if __name__ == '__main__':
    build()
