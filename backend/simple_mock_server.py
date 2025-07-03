#!/usr/bin/env python3
"""
Simple mock server for frontend integration testing
"""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import base64
import asyncio
from pathlib import Path

app = FastAPI(title="OCR Mock Server")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/api/models")
async def get_models():
    return {
        "models": [
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "provider": "google"},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "provider": "google"}
        ],
        "default": "gemini-2.5-flash"
    }

@app.post("/api/ocr/process")
async def process_ocr(file: UploadFile = File(...), model: str = Form("gemini-2.5-flash")):
    """Mock OCR processing that actually calls the real Gemini API"""
    
    print(f"📄 Processing file: {file.filename}")
    print(f"🤖 Using model: {model}")
    
    try:
        # Read file content
        content = await file.read()
        print(f"📊 File size: {len(content)} bytes")
        
        # Check if it's a PDF
        if file.filename and file.filename.lower().endswith('.pdf'):
            print("🔄 Processing PDF file...")
            
            # Use our workaround for PDF processing
            from app.services.gemini_service import GeminiService
            
            gemini_service = GeminiService()
            gemini_service._get_api_key()
            gemini_model = gemini_service._get_model(model)
            
            # Convert PDF to base64
            pdf_base64 = base64.b64encode(content).decode('utf-8')
            
            prompt = """
            Extract all text from this PDF document with high accuracy.
            Preserve the original formatting, structure, and layout as much as possible.
            Include all visible text including headers, body text, captions, labels, and any other textual content.
            If there are tables, maintain the table structure.
            If there are multiple columns, preserve the column layout.
            Return only the extracted text without any additional commentary.
            """
            
            content_parts = [prompt, {"mime_type": "application/pdf", "data": pdf_base64}]
            
            start_time = time.time()
            response = await asyncio.to_thread(gemini_model.generate_content, content_parts)
            end_time = time.time()
            
            processing_time_ms = int((end_time - start_time) * 1000)
            
            if response and response.text:
                extracted_text = response.text.strip()
                
                # Calculate statistics
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                
                result = {
                    "text": extracted_text,
                    "confidence": 0.95,
                    "metadata": {
                        "model": model,
                        "api_key_name": gemini_service.current_key_name,
                        "language": "en",
                        "filename": file.filename or "unknown.pdf",
                        "file_type": "application/pdf",
                        "file_size": len(content),
                        "pages": 1,
                        "words": word_count,
                        "characters": char_count,
                        "timestamp": time.time()
                    },
                    "processing_time_ms": processing_time_ms
                }
                
                print(f"✅ Successfully processed PDF: {word_count} words, {char_count} characters")
                return result
            else:
                return {"error": "No text extracted from PDF"}
                
        else:
            # For images, use the image processing method
            print("🖼️ Processing image file...")
            
            from PIL import Image
            import io
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(content))
            
            # Use the Gemini service for image processing
            from app.services.gemini_service import GeminiService
            
            gemini_service = GeminiService()
            result = await gemini_service.extract_text_from_image(
                image=image,
                model_name=model,
                language="en",
                filename=file.filename or "unknown.jpg"
            )
            
            print(f"✅ Successfully processed image: {result['word_count']} words")
            return result
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Mock OCR Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔗 Frontend can connect at: http://localhost:5173")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info") 