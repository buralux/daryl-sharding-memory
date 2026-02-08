#!/usr/bin/env python3
"""
Script to install pip if not available
"""

import sys
import os
import subprocess

def install_pip():
    """Install pip if not available"""
    print("📦 Installing pip...")
    
    # Download get-pip.py
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import urllib.request; exec(urllib.request.urlopen('{get_pip_url}').read())"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ Error downloading get-pip.py: {result.stderr}")
            return False
        
        # Now install pip
        result = subprocess.run(
            [sys.executable, "/tmp/get-pip.py", "install", "--user", "sentence-transformers", "torch", "numpy", "scipy", "scikit-learn"],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            print("\n📦 Installed packages:")
            print("   - sentence-transformers")
            print("   - torch")
            print("   - numpy")
            print("   - scipy")
            print("   - scikit-learn")
            return True
        else:
            print(f"❌ Error installing packages: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = install_pip()
    sys.exit(0 if success else 1)
