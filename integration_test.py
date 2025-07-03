#!/usr/bin/env python3
"""
Frontend-Backend Integration Test Script
This script will:
1. Set up the necessary environment files
2. Test backend connectivity
3. Test frontend-backend integration
4. Provide debugging information
"""
import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def create_backend_env():
    """Create .env file for backend if it doesn't exist"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("📝 Creating backend .env file...")
        env_content = """# Backend Environment Variables
HOST=0.0.0.0
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173

# Gemini API Keys (Replace with your actual keys)
# Get your keys from: https://aistudio.google.com/
GEMINI_API_KEY_1=your_actual_gemini_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here
GEMINI_API_KEY_5=your_fifth_api_key_here
GEMINI_API_KEY_6=your_sixth_api_key_here
GEMINI_API_KEY_7=your_seventh_api_key_here
GEMINI_API_KEY_8=your_eighth_api_key_here
GEMINI_API_KEY_9=your_ninth_api_key_here
GEMINI_API_KEY_10=your_tenth_api_key_here

# File Upload Settings
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads

# API Settings
API_TIMEOUT=30
RATE_LIMIT=100
"""
        env_file.write_text(env_content)
        print(f"✅ Created {env_file}")
        print("⚠️  Please edit the .env file and add your actual Gemini API keys!")
        return False
    else:
        print(f"✅ Backend .env file already exists: {env_file}")
        return True

def create_frontend_env():
    """Create .env file for frontend if it doesn't exist"""
    frontend_dir = Path("frontend")
    env_file = frontend_dir / ".env"
    
    if not env_file.exists():
        print("📝 Creating frontend .env file...")
        env_content = """# Frontend Environment Variables
VITE_API_URL=http://localhost:8000/api
VITE_MOCK_MODE=false
"""
        env_file.write_text(env_content)
        print(f"✅ Created {env_file}")
    else:
        print(f"✅ Frontend .env file already exists: {env_file}")
    
    return True

def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    try:
        os.chdir("backend")
        result = subprocess.run([sys.executable, "-c", "import fastapi, uvicorn, google.generativeai"], 
                              capture_output=True, text=True)
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Backend dependencies are installed")
            return True
        else:
            print("❌ Backend dependencies missing")
            print("🔧 Installing backend dependencies...")
            os.chdir("backend")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            os.chdir("..")
            return True
    except Exception as e:
        print(f"❌ Error checking backend dependencies: {e}")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("❌ Frontend dependencies missing")
        print("🔧 Installing frontend dependencies...")
        os.chdir("frontend")
        subprocess.run(["npm", "install"])
        os.chdir("..")
        return True
    else:
        print("✅ Frontend dependencies are installed")
        return True

def start_backend_server():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    os.chdir("backend")
    
    try:
        # Try multiple methods to start the server
        methods = [
            [sys.executable, "start_server.py"],
            [sys.executable, "run.py"],
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
        ]
        
        for method in methods:
            print(f"🔄 Trying: {' '.join(method)}")
            process = subprocess.Popen(method, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)  # Give it time to start
            
            if process.poll() is None:  # Process is still running
                print("✅ Backend server started successfully!")
                os.chdir("..")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Method failed: {stderr.decode()}")
        
        print("❌ All backend startup methods failed")
        os.chdir("..")
        return None
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        os.chdir("..")
        return None

def test_backend_connectivity():
    """Test if backend is responding"""
    print("🔍 Testing backend connectivity...")
    
    endpoints = [
        "http://localhost:8000/api/health",
        "http://localhost:8000/api/models",
        "http://localhost:8000/api/formats"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def start_frontend_server():
    """Start the frontend server"""
    print("🚀 Starting frontend server...")
    os.chdir("frontend")
    
    try:
        process = subprocess.Popen(["npm", "run", "dev"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Give it time to start
        
        if process.poll() is None:  # Process is still running
            print("✅ Frontend server started successfully!")
            print("🌐 Frontend available at: http://localhost:5173")
            os.chdir("..")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend startup failed: {stderr.decode()}")
            os.chdir("..")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        os.chdir("..")
        return None

def test_integration():
    """Test the complete frontend-backend integration"""
    print("🔍 Testing frontend-backend integration...")
    
    # Test if frontend can reach backend
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")

def main():
    """Main integration test function"""
    print("🔗 Frontend-Backend Integration Setup")
    print("=" * 50)
    
    # Step 1: Create environment files
    backend_env_exists = create_backend_env()
    create_frontend_env()
    
    if not backend_env_exists:
        print("\n❌ Please edit backend/.env with your actual Gemini API keys before continuing!")
        print("Get your keys from: https://aistudio.google.com/")
        return
    
    # Step 2: Check dependencies
    if not check_backend_dependencies():
        return
    
    if not check_frontend_dependencies():
        return
    
    # Step 3: Start backend
    backend_process = start_backend_server()
    if not backend_process:
        print("❌ Failed to start backend server")
        print("💡 Try running manually:")
        print("   cd backend")
        print("   python start_server.py")
        return
    
    # Step 4: Test backend
    time.sleep(2)
    test_backend_connectivity()
    
    # Step 5: Start frontend
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        return
    
    # Step 6: Test integration
    time.sleep(3)
    test_integration()
    
    print("\n🎉 Integration setup complete!")
    print("📋 Services running:")
    print("   Backend:  http://localhost:8000")
    print("   Frontend: http://localhost:5173")
    print("   API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main() 