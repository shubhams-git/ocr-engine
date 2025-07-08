#!/usr/bin/env python3
"""
Test script for multi-PDF analysis feature
"""
import requests
import json
import os
from pathlib import Path

def test_multi_pdf_analysis():
    """Test the new multi-PDF analysis endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/multi-pdf/analyze"
    
    print("🧪 Testing Multi-PDF Analysis Service")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("❌ Server not running. Start with: python backend/main.py")
            return
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python backend/main.py")
        return
    
    # Look for PDF files in current directory
    pdf_files = list(Path(".").glob("*.pdf"))
    
    if len(pdf_files) < 2:
        print("⚠️  Need at least 2 PDF files in current directory for testing (up to 10 files supported)")
        print("\nTo test with sample PDFs, you can:")
        print("1. Download some PDFs to the current directory")
        print("2. Or use these sample URLs:")
        
        # Test with sample PDFs from URLs
        test_with_sample_urls()
        return
    
    # Test with local PDF files
    print(f"📁 Found {len(pdf_files)} PDF files: {[f.name for f in pdf_files[:3]]}")
    
    # Use first 2-10 PDFs for testing
    test_files = pdf_files[:min(10, len(pdf_files))]
    
    files = []
    for pdf_file in test_files:
        files.append(('files', (pdf_file.name, open(pdf_file, 'rb'), 'application/pdf')))
    
    data = {
        'model': 'gemini-2.5-flash'
    }
    
    print(f"🚀 Sending {len(files)} files for analysis...")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed successfully!")
            print("\n" + "="*50)
            
            if result['success']:
                print("📊 EXTRACTED DATA:")
                print(json.dumps(result['extracted_data'], indent=2)[:500] + "...")
                
                print("\n🔄 NORMALIZED DATA:")
                print(json.dumps(result['normalized_data'], indent=2)[:500] + "...")
                
                print("\n📈 PROJECTIONS:")
                print(json.dumps(result['projections'], indent=2)[:500] + "...")
                
                print("\n💡 EXPLANATION:")
                print(result['explanation'][:500] + "...")
                
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out (this is normal for large files)")
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        # Close files
        for file_tuple in files:
            file_tuple[1][1].close()

def test_with_sample_urls():
    """Test with sample PDF files from URLs"""
    print("\n🌐 Testing with sample PDFs from URLs...")
    
    import httpx
    import tempfile
    
    # Sample PDF URLs (you can replace with your own)
    sample_urls = [
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        # Add more sample URLs here
    ]
    
    if not sample_urls or len(sample_urls) < 2:
        print("⚠️  Add sample PDF URLs to test_with_sample_urls() function")
        return
    
    print("💡 To test with your own PDFs:")
    print("1. Place PDF files in this directory")
    print("2. Or update the sample_urls list in this script")
    print("3. Run this script again")

def test_api_endpoints():
    """Test all related API endpoints"""
    print("\n🔍 Testing API Endpoints:")
    print("-" * 30)
    
    endpoints = [
        ("GET", "http://localhost:8000/health", "Health check"),
        ("GET", "http://localhost:8000/models", "Available models"),
        ("GET", "http://localhost:8000/api-keys/status", "API key status"),
    ]
    
    for method, url, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(url)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                if "models" in url:
                    models = response.json().get("models", [])
                    print(f"   Available models: {[m['id'] for m in models[:3]]}")
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {e}")

if __name__ == "__main__":
    test_multi_pdf_analysis()
    test_api_endpoints()
    
    print("\n" + "="*50)
    print("📝 Manual Testing Commands:")
    print("="*50)
    print("# Test with curl:")
    print("curl -X POST 'http://localhost:8000/multi-pdf/analyze' \\")
    print("  -F 'files=@document1.pdf' \\")
    print("  -F 'files=@document2.pdf' \\")
    print("  -F 'model=gemini-2.5-flash'")
    print("\n# Check server logs for detailed information") 