#!/usr/bin/env python3
"""
Entry point for the Streamlit application
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app.py"])