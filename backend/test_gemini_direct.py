#!/usr/bin/env python3
"""
Direct test of Gemini API without PDF processing
"""
import asyncio
import logging
from PIL import Image
import io

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_gemini_direct():
    """Test Gemini API directly with a simple image"""
    print("🚀 Testing Gemini API directly")
    print("=" * 50)
    
    try:
        # Import the Gemini service
        from app.services.gemini_service import GeminiService
        
        print("🔧 Initializing Gemini service...")
        gemini_service = GeminiService()
        
        # Create a simple test image (white background with black text)
        print("🖼️ Creating test image...")
        width, height = 800, 600
        image = Image.new('RGB', (width, height))
        
        # Add some text to the image (this will be a simple test)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw some test text
        test_text = "This is a test image for OCR processing.\nIt contains multiple lines of text.\nThe Gemini API should be able to extract this text."
        
        # Calculate text position (center of image)
        bbox = draw.textbbox((0, 0), test_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw the text
        draw.text((x, y), test_text, fill='black', font=font)
        
        print(f"✅ Created test image: {width}x{height}")
        
        # Test the Gemini API call
        print("🤖 Calling Gemini API...")
        print("-" * 30)
        
        # Process the image
        result = await gemini_service.extract_text_from_image(
            image=image,
            model_name="gemini-2.5-flash",
            language="en",
            filename="test_image.png"
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
        
        print("\n📊 METADATA:")
        print("-" * 30)
        for key, value in result.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct()) 