#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Crawler Setup Script
===========================

Quick setup script for the WeChat crawler.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("WeChat Posts Crawler Setup")
    print("=" * 60)
    print("This script will help you set up the WeChat crawler.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✓ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    try:
        # Try to create virtual environment
        print("Creating virtual environment...")
        result = subprocess.run([sys.executable, "-m", "venv", "venv"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠ Warning: Could not create virtual environment")
            print("Installing globally instead...")
            pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        else:
            print("✓ Virtual environment created")
            # Use virtual environment pip
            if platform.system() == "Windows":
                pip_cmd = ["venv\\Scripts\\pip", "install", "-r", "requirements.txt"]
            else:
                pip_cmd = ["venv/bin/pip", "install", "-r", "requirements.txt"]
        
        print("Installing packages...")
        result = subprocess.run(pip_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            print("\nTry installing manually:")
            print("pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\nSetting up directories...")
    
    directories = [
        "crawled_data",
        "logs",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_chrome():
    """Check if Chrome is available"""
    print("\nChecking Chrome browser...")
    
    chrome_paths = [
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium"
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Found Chrome at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        # Check if chrome is in PATH
        try:
            subprocess.run(["chrome", "--version"], capture_output=True, check=True)
            print("✓ Chrome found in PATH")
            chrome_found = True
        except:
            try:
                subprocess.run(["google-chrome", "--version"], capture_output=True, check=True)
                print("✓ Google Chrome found in PATH")
                chrome_found = True
            except:
                pass
    
    if not chrome_found:
        print("⚠ Warning: Chrome browser not found")
        print("Please install Google Chrome for Selenium to work:")
        print("- Windows/macOS: Download from https://www.google.com/chrome/")
        print("- Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("- Other Linux: Use your package manager")
    
    return chrome_found

def create_example_config():
    """Create an example configuration file"""
    print("\nCreating example configuration...")
    
    example_config = '''# WeChat Crawler Environment Configuration
# Copy this file to .env and modify as needed

# Basic settings
WECHAT_HEADLESS=true
WECHAT_OUTPUT_DIR=./crawled_data

# Proxy settings (uncomment and modify if needed)
# WECHAT_PROXY=http://your-proxy-server:port

# Rate limiting
WECHAT_DELAY_MIN=1
WECHAT_DELAY_MAX=3

# Maximum requests
WECHAT_MAX_POSTS=10
WECHAT_MAX_ACCOUNTS=5
'''
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(example_config)
    
    print("✓ Created .env.example file")
    print("  You can copy this to .env and customize the settings")

def run_test():
    """Run the test suite"""
    print("\nRunning tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_crawler.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("Setup Complete! 🎉")
    print("=" * 60)
    print()
    print("Quick Start:")
    print("1. Basic usage:")
    print("   python wechat_crawler.py")
    print()
    print("2. Run examples:")
    print("   python example_usage.py")
    print()
    print("3. Test the setup:")
    print("   python test_crawler.py")
    print()
    print("Configuration:")
    print("- Edit config.py for advanced settings")
    print("- Copy .env.example to .env for environment variables")
    print("- Check README.md for detailed documentation")
    print()
    print("Troubleshooting:")
    print("- Check logs/ directory for error logs")
    print("- Ensure Chrome browser is installed")
    print("- Use proxy if you encounter rate limiting")
    print()
    print("⚠ Legal Notice:")
    print("This tool is for educational and research purposes only.")
    print("Please respect WeChat's Terms of Service and rate limits.")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Check Chrome
    chrome_available = check_chrome()
    
    # Install dependencies
    deps_installed = install_dependencies()
    
    # Create example config
    create_example_config()
    
    # Run tests
    tests_passed = run_test()
    
    # Print results
    print("\n" + "=" * 60)
    print("Setup Summary:")
    print("=" * 60)
    print(f"✓ Python version: {'OK' if True else 'FAIL'}")
    print(f"✓ Dependencies: {'OK' if deps_installed else 'FAIL'}")
    print(f"✓ Chrome browser: {'OK' if chrome_available else 'WARNING'}")
    print(f"✓ Tests: {'PASSED' if tests_passed else 'FAILED'}")
    
    if deps_installed and tests_passed:
        print_usage_instructions()
    else:
        print("\n❌ Setup incomplete. Please resolve the issues above.")
        if not deps_installed:
            print("Try installing dependencies manually:")
            print("pip install -r requirements.txt")
        if not chrome_available:
            print("Install Google Chrome browser for full functionality.")

if __name__ == "__main__":
    main()