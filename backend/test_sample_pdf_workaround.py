#!/usr/bin/env python3
"""
Workaround test for sample.pdf processing without PyMuPDF
"""
import asyncio
import logging
import base64
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_sample_pdf_workaround():
    """Test sample.pdf processing with workaround for PyMuPDF issues"""
    print("🚀 Testing sample.pdf processing with workaround")
    print("=" * 60)
    
    # Check if sample.pdf exists
    sample_pdf = Path("sample.pdf")
    if not sample_pdf.exists():
        print("❌ sample.pdf not found!")
        return
    
    print(f"✅ Found sample.pdf: {sample_pdf}")
    print(f"📊 File size: {sample_pdf.stat().st_size} bytes")
    
    try:
        # Import the Gemini service
        from app.services.gemini_service import GeminiService
        
        print("🔧 Initializing Gemini service...")
        gemini_service = GeminiService()
        
        # Read the PDF file as binary data
        with open(sample_pdf, 'rb') as f:
            pdf_content = f.read()
        
        print(f"📄 Read PDF content: {len(pdf_content)} bytes")
        
        # Convert PDF to base64 for direct API call
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        print(f"🔄 Converted to base64: {len(pdf_base64)} characters")
        
        # Create a simple test prompt for PDF processing
        prompt = """
        Extract all text from this PDF document with high accuracy.
        Preserve the original formatting, structure, and layout as much as possible.
        Include all visible text including headers, body text, captions, labels, and any other textual content.
        If there are tables, maintain the table structure.
        If there are multiple columns, preserve the column layout.
        Return only the extracted text without any additional commentary.
        """
        
        print("🤖 Calling Gemini API with PDF data...")
        print("-" * 40)
        
        # Get API key and model
        gemini_service._get_api_key()
        model = gemini_service._get_model("gemini-2.5-flash")
        
        # Create content for Gemini (PDF as base64 + prompt)
        import google.generativeai as genai
        
        # Create the content parts
        content_parts = [
            prompt,
            {
                "mime_type": "application/pdf",
                "data": pdf_base64
            }
        ]
        
        # Make the API call directly
        start_time = asyncio.get_event_loop().time()
        
        print("🔄 Making direct Gemini API call...")
        response = await asyncio.to_thread(model.generate_content, content_parts)
        end_time = asyncio.get_event_loop().time()
        
        processing_time_ms = int((end_time - start_time) * 1000)
        
        if response and response.text:
            extracted_text = response.text.strip()
            
            print("✅ Gemini API call completed!")
            print("=" * 60)
            print("📋 RESULTS:")
            print(f"📝 Text length: {len(extracted_text)} characters")
            print(f"⏱️  Processing time: {processing_time_ms}ms")
            print(f"🤖 Model used: gemini-2.5-flash")
            print(f"🔑 API Key used: {gemini_service.current_key_name}")
            
            print("\n📄 EXTRACTED TEXT FROM SAMPLE.PDF:")
            print("-" * 40)
            print(extracted_text)
            
            print("\n📊 STATISTICS:")
            print("-" * 40)
            word_count = len(extracted_text.split()) if extracted_text else 0
            char_count = len(extracted_text) if extracted_text else 0
            line_count = len(extracted_text.split('\n')) if extracted_text else 0
            
            print(f"Words: {word_count}")
            print(f"Characters: {char_count}")
            print(f"Lines: {line_count}")
            
        else:
            print("❌ No text extracted from PDF")
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sample_pdf_workaround()) 