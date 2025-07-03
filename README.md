# OCR Engine

A high-performance Optical Character Recognition (OCR) service built with FastAPI and Google Gemini AI. This service provides accurate text extraction from images and PDF documents through a simple REST API.

## 🚀 Features

- **Multi-format Support**: Processes images (PNG, JPG, JPEG, GIF, BMP, TIFF, WebP) and PDF documents
- **Multiple AI Models**: Supports various Gemini models including GPT-1.5-Pro, GPT-1.5-Flash, and GPT-2.0-Flash (Experimental)
- **API Key Rotation**: Automatic rotation across multiple API keys for improved reliability and rate limiting
- **High Accuracy**: Preserves original document formatting, structure, and layout
- **Performance Monitoring**: Built-in statistics and health monitoring
- **CORS Support**: Ready for frontend integration
- **Scalable Architecture**: Designed for production deployment

## 🏗️ Architecture

```
ocr-engine/
├── backend/
│   ├── main.py          # FastAPI application and OCR endpoints
│   ├── config.py        # Configuration and API key management
│   ├── prompt.py        # OCR prompt templates
│   └── requirements.txt # Python dependencies
├── .env                 # Environment variables (API keys)
└── README.md
```

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key(s)
- 2GB+ RAM (recommended)
- Network access for API calls

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ocr-engine
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Primary API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Multiple keys for rotation (recommended for production)
GEMINI_API_KEY_1=your_first_api_key
GEMINI_API_KEY_2=your_second_api_key
GEMINI_API_KEY_3=your_third_api_key
# ... up to GEMINI_API_KEY_10
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the Service

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Core Endpoints

#### POST `/ocr`
Extract text from uploaded file

**Parameters:**
- `file` (multipart/form-data): Image or PDF file
- `model` (optional): Gemini model to use (default: "gemini-1.5-flash")

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "model=gemini-1.5-pro"
```

**Example Response:**
```json
{
  "success": true,
  "text": "Extracted text content...",
  "confidence": 0.95,
  "metadata": {
    "model_used": "gemini-1.5-pro",
    "file_name": "document.pdf",
    "file_size": 245760,
    "content_type": "application/pdf",
    "processing_time_ms": 1250,
    "text_length": 1024,
    "timestamp": 1704240000.0
  },
  "processing_time_ms": 1250
}
```

### Information Endpoints

#### GET `/health`
Service health check and status

#### GET `/models`
List available Gemini models

#### GET `/formats`
Supported file formats and size limits

#### GET `/stats`
API usage statistics and performance metrics

#### GET `/prompt`
Current OCR prompt configuration

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation with interactive testing capabilities.

## 🔧 Configuration

### API Key Management

The service supports multiple API keys for improved reliability:

```python
# Single key
GEMINI_API_KEY=your_api_key

# Multiple keys (automatic rotation)
GEMINI_API_KEY_1=key_1
GEMINI_API_KEY_2=key_2
GEMINI_API_KEY_3=key_3
```

### Model Selection

Available models with their characteristics:

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `gemini-1.5-flash` | Fast | Good | Quick processing, bulk operations |
| `gemini-1.5-pro` | Medium | Excellent | Complex documents, high accuracy needs |
| `gemini-2.0-flash-exp` | Fast | Good | Latest features (experimental) |

### File Size Limits

- **Images**: 10MB maximum
- **PDFs**: 50MB maximum

### CORS Configuration

Update `ALLOWED_ORIGINS` in `config.py` for your frontend domains:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React dev server
    "http://localhost:5173",    # Vite dev server
    "https://your-app.com",     # Production domain
]
```

## 🎯 Usage Examples

### Python Client

```python
import requests

def extract_text(file_path, model="gemini-1.5-flash"):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'model': model}
        response = requests.post(
            'http://localhost:8000/ocr',
            files=files,
            data=data
        )
    return response.json()

# Extract from image
result = extract_text('invoice.png', 'gemini-1.5-pro')
print(result['text'])
```

### JavaScript/Node.js Client

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function extractText(filePath, model = 'gemini-1.5-flash') {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('model', model);
    
    const response = await axios.post('http://localhost:8000/ocr', form, {
        headers: form.getHeaders()
    });
    
    return response.data;
}

// Usage
extractText('./document.pdf')
    .then(result => console.log(result.text))
    .catch(console.error);
```

### cURL Examples

```bash
# Basic OCR
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg"

# With specific model
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf" \
  -F "model=gemini-1.5-pro"

# Check service health
curl "http://localhost:8000/health"

# Get usage statistics
curl "http://localhost:8000/stats"
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Load Balancing**: Deploy multiple instances behind a load balancer
3. **Rate Limiting**: Implement rate limiting for API protection
4. **Monitoring**: Set up logging and monitoring for production use
5. **SSL/TLS**: Use HTTPS in production environments

### Health Monitoring

The service provides several monitoring endpoints:

- `/health` - Basic health check
- `/stats` - Performance metrics
- Success/failure rates and processing times

## 🔍 Troubleshooting

### Common Issues

**API Key Errors**
```
ValueError: No Gemini API keys found
```
- Ensure `.env` file exists with valid API keys
- Check API key format and permissions

**File Size Errors**
```
413 Request Entity Too Large
```
- Reduce file size or compress images
- Check file size limits in `/formats` endpoint

**Model Not Found**
```
404 Model not found
```
- Use `/models` endpoint to check available models
- Verify model name spelling

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### Typical Processing Times

| File Type | Size | Processing Time |
|-----------|------|----------------|
| Image (PNG) | 1MB | 800-1200ms |
| PDF | 5MB | 1500-2500ms |
| Complex Document | 10MB | 3000-5000ms |

### Optimization Tips

1. **Use appropriate model**: Flash models for speed, Pro models for accuracy
2. **Implement caching**: Cache results for repeated requests
3. **Batch processing**: Process multiple files in parallel
4. **API key rotation**: Use multiple keys to avoid rate limits

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Customizing OCR Prompts

Modify the prompt in `backend/prompt.py`:

```python
OCR_PROMPT = """
Your custom OCR instructions here.
Specify formatting requirements, special handling, etc.
"""
```

### Adding New Endpoints

Extend the FastAPI application in `main.py`:

```python
@app.post("/custom-endpoint")
async def custom_function():
    # Your custom logic
    return {"result": "success"}
```

## 🆘 Support

For technical support or questions:

1. Check the interactive API documentation at `/docs`
2. Review the troubleshooting section above
3. Contact the development team

---

**Last Updated**: January 2025  
**Version**: 1.0.0
