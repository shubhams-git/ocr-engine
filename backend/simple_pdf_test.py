#!/usr/bin/env python3
"""
Simple test of PDF processing with Gemini
"""
import os
import sys
import asyncio
from pathlib import Path
from fastapi import UploadFile

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_pdf_processing():
    """Test PDF processing directly"""
    print("🚀 Testing PDF processing with sample.pdf")
    print("=" * 50)
    
    # Check if sample.pdf exists
    sample_pdf = Path("sample.pdf")
    if not sample_pdf.exists():
        print("❌ sample.pdf not found!")
        return
    
    print(f"✅ Found sample.pdf: {sample_pdf}")
    print(f"📊 File size: {sample_pdf.stat().st_size} bytes")
    
    try:
        # Import and test the Gemini service directly
        from app.services.gemini_service import GeminiService
        from app.utils.file_utils import PDFProcessor
        
        print("🔧 Initializing Gemini service...")
        gemini_service = GeminiService()
        
        # Read the PDF file and convert to images
        with open(sample_pdf, 'rb') as f:
            pdf_content = f.read()
        
        print(f"📄 Read PDF content: {len(pdf_content)} bytes")
        print("🔄 Converting PDF to images...")
        
        # Create a mock UploadFile for the PDF processor
        class MockUploadFile(UploadFile):
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
                self.content_type = "application/pdf"
            
            async def read(self):
                return self.content
            
            async def seek(self, pos):
                pass
        
        mock_file = MockUploadFile(pdf_content, "sample.pdf")
        
        # Convert PDF to images
        images = await PDFProcessor.pdf_to_images(mock_file)
        print(f"✅ Converted to {len(images)} images")
        
        # Test the Gemini API call
        print("🤖 Calling Gemini API...")
        print("-" * 30)
        
        # Process the PDF pages
        result = await gemini_service.extract_text_from_pdf_pages(
            images=images,
            model_name="gemini-2.5-flash",
            language="en",
            filename="sample.pdf"
        )
        
        print("✅ Gemini API call completed!")
        print("=" * 50)
        print("📋 RESULTS:")
        print(f"📝 Text length: {len(result['text'])} characters")
        print(f"🎯 Confidence: {result['confidence']}")
        print(f"⏱️  Processing time: {result['processing_time_ms']}ms")
        print(f"🤖 Model used: {result['model_used']}")
        print(f"🔑 API Key used: {result['api_key_used']}")
        
        print("\n📄 EXTRACTED TEXT:")
        print("-" * 30)
        print(result['text'])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_processing()) 