#!/usr/bin/env python3
"""
Direct test of OCR service with sample.pdf
"""
import asyncio
import logging
from pathlib import Path
from fastapi import UploadFile
from app.services.ocr_service import ocr_service
from app.config import settings

# Set up logging to see all events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_sample_pdf():
    """Test OCR processing with sample.pdf"""
    print("🚀 Starting OCR test with sample.pdf")
    print("=" * 50)
    
    # Get the sample.pdf path
    sample_pdf_path = Path("sample.pdf")
    if not sample_pdf_path.exists():
        print("❌ sample.pdf not found!")
        return
    
    print(f"📄 Found sample.pdf: {sample_pdf_path}")
    print(f"📊 File size: {sample_pdf_path.stat().st_size} bytes")
    
    try:
        # Create a proper mock UploadFile object
        class MockUploadFile(UploadFile):
            def __init__(self, file_path):
                self.file_path = file_path
                self.filename = file_path.name
                self.content_type = "application/pdf"
            
            async def read(self):
                with open(self.file_path, 'rb') as f:
                    return f.read()
        
        # Create mock upload file
        mock_file = MockUploadFile(sample_pdf_path)
        
        print("🔍 Processing with Gemini 2.5 Flash...")
        print("-" * 30)
        
        # Process the file
        result = await ocr_service.process_file(
            mock_file, 
            model="gemini-2.5-flash", 
            language="en"
        )
        
        print("✅ Processing completed!")
        print("=" * 50)
        print("📋 RESULTS:")
        print(f"📝 Text length: {len(result.text)} characters")
        print(f"🎯 Confidence: {result.confidence}")
        print(f"⏱️  Processing time: {result.processing_time_ms}ms")
        print(f"🤖 Model used: {result.metadata.get('model', 'Unknown')}")
        print(f"🔑 API Key used: {result.metadata.get('api_key_name', 'Unknown')}")
        
        print("\n📄 EXTRACTED TEXT:")
        print("-" * 30)
        print(result.text)
        
        print("\n📊 METADATA:")
        print("-" * 30)
        for key, value in result.metadata.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Initializing OCR service...")
    asyncio.run(test_sample_pdf()) 