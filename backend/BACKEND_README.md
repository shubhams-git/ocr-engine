# OCR Engine Backend

A powerful FastAPI-based backend for OCR processing using Google Gemini AI with automatic API key rotation.

## 🚀 Features

- **Multiple AI Models**: Support for Gemini 2.5 Pro, Gemini 2.5 Flash, and more
- **API Key Rotation**: Automatic rotation through 10 different Gemini API keys
- **File Support**: Images (PNG, JPG, GIF, BMP, TIFF, WebP) and PDFs
- **Smart Processing**: PDF to image conversion for optimal OCR results
- **Comprehensive Logging**: Detailed terminal logging with emojis for easy monitoring
- **Error Handling**: Robust error handling with retry logic
- **CORS Support**: Pre-configured for frontend integration
- **Health Monitoring**: Built-in health checks and API statistics

## 📋 Requirements

- Python 3.8+
- All dependencies in `requirements.txt`

## 🛠️ Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Create `.env` file** (REQUIRED):
   Create a file named `.env` in the backend directory with your API keys:
   ```env
   # Gemini API Keys (Replace with your real keys)
   GEMINI_API_KEY_1=your_first_api_key_here
   GEMINI_API_KEY_2=your_second_api_key_here
   # ... add up to 10 keys for rotation
   
   # Server Configuration (optional)
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True
   ```
   
   📋 **See `env_setup_guide.md` for complete setup details and example keys**

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Server

### Method 1: Using the startup script
```bash
python run.py
```

### Method 2: Using uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

### Core Endpoints

- **POST** `/api/ocr/process` - Process uploaded file for OCR
- **GET** `/api/health` - Health check with service status
- **GET** `/api/models` - Available AI models
- **GET** `/api/formats` - Supported file formats
- **GET** `/api/stats` - API usage statistics

### Documentation

- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation (ReDoc)

## 🔧 Configuration

### Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `True` | Debug mode |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS |
| `MAX_FILE_SIZE` | `10485760` | Max file size in bytes (10MB) |

### API Key Rotation

The backend automatically rotates through 10 pre-configured Gemini API keys:
- Automatic failover on rate limits or quota issues
- Smart retry logic with exponential backoff
- Real-time monitoring of key health status

## 📁 File Support

### Supported Formats

**Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
**Documents**: PDF (up to 10 pages)

### File Processing

- **Images**: Direct processing with Gemini Vision API
- **PDFs**: Converted to high-resolution images for optimal OCR
- **Size Limits**: 10MB maximum file size

## 🔍 Usage Examples

### Upload Image for OCR
```bash
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "file=@document.jpg" \
  -F "model=gemini-2.5-flash" \
  -F "language=en"
```

### Upload PDF for OCR
```bash
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "file=@document.pdf" \
  -F "model=gemini-2.5-pro" \
  -F "language=en"
```

## 📈 Monitoring

### Terminal Logging

The backend provides comprehensive terminal logging with emojis:

```
🚀 Starting OCR Engine API
🔑 Initialized API key manager with 10 keys
📝 OCR processing requested: document.pdf
📄 Converting PDF to images: document.pdf (3 pages)
🤖 Using API key: Backable_1
✅ OCR processing successful: document.pdf
```

## 🚀 Testing the Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python run.py
   ```

3. **Test health endpoint**:
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **View API docs**: Open `http://localhost:8000/docs` in browser

## 🔧 Integration with Frontend

To connect the React frontend to this backend:

1. In frontend directory, edit `.env`:
   ```
   VITE_MOCK_MODE=false
   VITE_API_URL=http://localhost:8000
   ```

2. Start both frontend and backend:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python run.py
   
   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```

## 📞 API Integration

The backend is fully compatible with the existing frontend. Simply:
1. Start the backend server (port 8000)
2. Set frontend to use real API mode
3. Upload files through the frontend interface

---

**Your AI-powered OCR backend is ready!** 🚀 