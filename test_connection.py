#!/usr/bin/env python3
"""
Simple connectivity test between frontend and backend
"""
import requests
import json
import time

def test_backend():
    """Test backend endpoints"""
    print("🔍 Testing Backend Connectivity")
    print("=" * 40)
    
    endpoints = {
        "Health Check": "http://localhost:8000/api/health",
        "Available Models": "http://localhost:8000/api/models", 
        "Supported Formats": "http://localhost:8000/api/formats",
        "API Stats": "http://localhost:8000/api/stats"
    }
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                data = response.json()
                print(f"   {json.dumps(data, indent=2)[:100]}...")
            else:
                print(f"❌ {name}: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection refused (server not running?)")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
        print()

def test_frontend():
    """Test frontend accessibility"""
    print("🔍 Testing Frontend Connectivity")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:5173")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not accessible (server not running?)")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def test_cors():
    """Test CORS configuration"""
    print("🔍 Testing CORS Configuration")
    print("=" * 40)
    
    try:
        # Simulate a CORS preflight request
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:8000/api/health", headers=headers, timeout=5)
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        
        if cors_headers:
            print("✅ CORS headers present:")
            for header, value in cors_headers.items():
                print(f"   {header}: {value}")
        else:
            print("❌ No CORS headers found")
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

if __name__ == "__main__":
    print("🔗 Frontend-Backend Connection Test")
    print("=" * 50)
    print()
    
    test_backend()
    test_frontend()
    test_cors()
    
    print("🏁 Test completed!")
    print("\nIf tests fail:")
    print("1. Make sure both servers are running:")
    print("   Backend: cd backend && python start_server.py")
    print("   Frontend: cd frontend && npm run dev")
    print("2. Check your .env files have correct API keys")
    print("3. Verify no firewall is blocking the ports") 