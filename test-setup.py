#!/usr/bin/env python3
"""
Quick setup verification script for AI Marketing News System
Run this after installation to verify everything is working
"""

import sys
import subprocess
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check if required Python packages can be imported"""
    packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
        'openai', 'requests', 'beautifulsoup4', 'feedparser', 
        'portalocker', 'simhash', 'schedule'
    ]
    
    missing = []
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Check if .env file exists and has API key"""
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        print(f"❌ {env_path} file not found")
        print("   Run: cp backend/.env.example backend/.env")
        return False
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=sk-' in content:
                print(f"✅ {env_path} has API key configured")
                return True
            else:
                print(f"⚠️  {env_path} exists but API key may not be set")
                print("   Please add your OpenAI API key to the .env file")
                return False
    except Exception as e:
        print(f"❌ Error reading {env_path}: {e}")
        return False

def check_directories():
    """Check if required directories exist"""
    dirs = ["backend/data", "backend/logs"]
    for directory in dirs:
        if os.path.exists(directory):
            print(f"✅ {directory} directory exists")
        else:
            print(f"❌ {directory} directory missing")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created {directory}")
            except Exception as e:
                print(f"❌ Failed to create {directory}: {e}")
                return False
    return True

def main():
    print("🔍 AI Marketing News System - Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    print("\n📋 Checking Python version...")
    all_good &= check_python_version()
    
    print("\n📦 Checking Python dependencies...")
    all_good &= check_dependencies()
    
    print("\n⚙️  Checking configuration...")
    all_good &= check_env_file()
    
    print("\n📁 Checking directories...")
    all_good &= check_directories()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! Your system is ready.")
        print("\n📝 Next steps:")
        print("1. cd backend/src && python -m uvicorn main:app --reload")
        print("2. In new terminal: cd frontend && npm run dev")
        print("3. Open http://localhost:3000")
    else:
        print("❌ Some issues found. Please fix them before proceeding.")
        print("\n🛠️  Common fixes:")
        print("- Install dependencies: cd backend && pip install -r requirements.txt")
        print("- Copy environment: cp backend/.env.example backend/.env")
        print("- Add OpenAI API key to backend/.env file")

if __name__ == "__main__":
    main()