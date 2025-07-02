# API Integration Guide

## 🔄 Mock vs Real API Modes

This frontend is designed to work seamlessly with or without a backend. Here's how it works:

## 📁 Current Setup (Mock Mode)

Right now, the app is running in **Mock Mode** which means:
- ✅ **Works immediately** without any backend
- ✅ **Simulates real OCR processing** with realistic delays
- ✅ **Returns sample extracted text** to test the UI
- ✅ **No external dependencies** required

### Environment Configuration

Your current `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_ENV=development
VITE_MOCK_MODE=true  # This enables mock mode
```

## 🚀 How to Switch to Real Backend

When you're ready to use the real backend API:

### Step 1: Update Environment
```env
VITE_API_URL=http://localhost:8000/api  # Your backend URL
VITE_APP_ENV=development
VITE_MOCK_MODE=false  # Disable mock mode
```

### Step 2: Ensure Backend Endpoints

Your backend needs to provide these endpoints:

#### POST `/api/ocr/process`
Process uploaded files for OCR extraction.

**Request:**
```javascript
// FormData with file
const formData = new FormData()
formData.append('file', fileObject)
formData.append('model', 'openai-gpt4-vision') // optional
formData.append('language', 'en') // optional
```

**Expected Response:**
```json
{
  "text": "Extracted text from the image/PDF",
  "confidence": 0.95,
  "metadata": {
    "model": "openai-gpt4-vision",
    "language": "en",
    "pages": 1,
    "words": 123,
    "characters": 456,
    "processingTime": 2500
  }
}
```

#### GET `/api/health`
Health check endpoint.

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/models`
Get available AI models.

**Expected Response:**
```json
[
  {
    "id": "openai-gpt4-vision",
    "name": "OpenAI GPT-4 Vision",
    "provider": "openai"
  },
  {
    "id": "gemini-pro-vision",
    "name": "Google Gemini Pro Vision",
    "provider": "google"
  }
]
```

## 🔧 Smart Fallback System

The frontend includes a smart fallback system:

1. **Mock Mode ON** → Always uses mock data
2. **Mock Mode OFF + Development** → Tries real API, falls back to mock if backend is down
3. **Production** → Always uses real API (no fallback)

## 🎯 Backend Implementation Examples

### Node.js/Express Example
```javascript
app.post('/api/ocr/process', upload.single('file'), async (req, res) => {
  try {
    const file = req.file
    const model = req.body.model || 'openai-gpt4-vision'
    
    // Process with your chosen AI model
    const result = await processWithAI(file, model)
    
    res.json({
      text: result.extractedText,
      confidence: result.confidence,
      metadata: {
        model: model,
        language: result.language,
        pages: result.pages,
        words: result.wordCount,
        characters: result.charCount
      }
    })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})
```

### Python/FastAPI Example
```python
@app.post("/api/ocr/process")
async def process_ocr(file: UploadFile = File(...), model: str = "openai-gpt4-vision"):
    try:
        # Process with your chosen AI model
        result = await process_with_ai(file, model)
        
        return {
            "text": result.extracted_text,
            "confidence": result.confidence,
            "metadata": {
                "model": model,
                "language": result.language,
                "pages": result.pages,
                "words": result.word_count,
                "characters": result.char_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🔑 AI Model Integration

When building your backend, you'll integrate with these AI services:

### OpenAI GPT-4 Vision
```javascript
const response = await openai.chat.completions.create({
  model: "gpt-4-vision-preview",
  messages: [{
    role: "user",
    content: [
      { type: "text", text: "Extract all text from this image." },
      { type: "image_url", image_url: { url: base64Image } }
    ]
  }]
})
```

### Google Gemini Pro Vision
```python
model = genai.GenerativeModel('gemini-pro-vision')
response = model.generate_content([
    "Extract all text from this image",
    image
])
```

## 📊 File Processing

Your backend should handle:
- **File validation** (size, type)
- **Image processing** (PNG, JPG, etc.)
- **PDF processing** (convert to images if needed)
- **Error handling** with proper HTTP status codes
- **Rate limiting** for API calls
- **Response formatting** as expected by frontend

## 🚀 Testing Your Backend

1. Start your backend server
2. Update `.env` to set `VITE_MOCK_MODE=false`
3. Restart the frontend dev server
4. Test file upload - it should now use your real API!

## 🎯 Production Checklist

- [ ] Backend API endpoints working
- [ ] AI model API keys configured
- [ ] File upload limits set
- [ ] Error handling implemented
- [ ] CORS configured for your domain
- [ ] Environment variables set correctly
- [ ] `VITE_MOCK_MODE=false` in production

---

**Current Status**: Mock Mode ✅ | Ready for Backend Integration 🚀 