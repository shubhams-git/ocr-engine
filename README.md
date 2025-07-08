# OCR Engine 🔍

A comprehensive document analysis platform built with **FastAPI** and **React** that leverages **Google Gemini AI** for intelligent text extraction and financial data analysis. The platform offers both single document OCR and advanced multi-PDF financial analysis with projections.

![OCR Engine](https://img.shields.io/badge/OCR-Engine-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi) ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black) ![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?logo=google&logoColor=white)

## 🌟 Features

### 📄 Single Document OCR
- **Multi-format Support**: Process images (PNG, JPG, JPEG, GIF, BMP, TIFF, WebP) and PDF documents
- **High Accuracy**: Preserves original document formatting, structure, and layout
- **Real-time Processing**: Fast text extraction with visual feedback
- **Export Options**: Copy to clipboard or download as text file

### 📊 Multi-PDF Financial Analysis (Advanced)
- **Data Extraction**: Automatically extract financial data from multiple PDF documents
- **Data Normalization**: Standardize and combine data across different document formats
- **Financial Projections**: Generate 2-3 year forecasts with confidence levels
- **Risk Assessment**: Identify potential risks and scenario analysis
- **Trend Analysis**: Calculate growth rates, ratios, and seasonal patterns
- **Interactive Results**: Expandable sections with detailed JSON data and visualizations

### 🚀 Technical Features
- **Multiple AI Models**: Support for Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash, and 1.5 models
- **API Key Rotation**: Automatic rotation across multiple API keys for reliability
- **Modern UI**: Responsive design with smooth animations and intuitive interactions
- **Real-time Monitoring**: Health checks, performance metrics, and error handling
- **Scalable Architecture**: Microservices design ready for production deployment

## 🏗️ Architecture

```
ocr-engine/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Application entry point & routing
│   ├── config.py              # Configuration & API key management
│   ├── middleware.py          # Error handling middleware
│   ├── models.py              # Pydantic data models
│   ├── requirements.txt       # Python dependencies
│   ├── routers/               # API route handlers
│   │   ├── admin.py          # API key management
│   │   ├── health.py         # Health & system info
│   │   ├── multi_pdf.py      # Multi-PDF analysis
│   │   └── ocr.py           # Single document OCR
│   └── services/             # Business logic
│       ├── ocr_service.py   # OCR processing
│       └── multi_pdf_service.py # Financial analysis
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── FileUpload.jsx       # Single file upload
│   │   │   ├── MultiPDFUpload.jsx   # Multi-file upload
│   │   │   ├── ResultsDisplay.jsx   # OCR results
│   │   │   ├── MultiPDFResults.jsx  # Analysis results
│   │   │   ├── Header.jsx           # App header
│   │   │   └── LoadingSpinner.jsx   # Loading states
│   │   ├── services/
│   │   │   └── api.js        # API client
│   │   ├── App.jsx           # Main application
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Vite configuration
├── create_sample_pdfs.py      # Generate test PDFs
├── test_multi_pdf_analysis.py # Test script
└── README.md                  # This file
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Google Gemini AI** - Advanced multimodal AI for document processing
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production deployment

### Frontend  
- **React 18** - Modern UI library with hooks and concurrent features
- **Vite** - Next-generation build tool for fast development
- **Framer Motion** - Production-ready motion library for animations
- **Axios** - Promise-based HTTP client
- **React Dropzone** - File upload with drag & drop support
- **Lucide React** - Beautiful, customizable icons

### AI & Processing
- **Google Gemini 2.5 Flash** - Fast, efficient processing (recommended)
- **Google Gemini 2.5 Pro** - Advanced reasoning for complex documents
- **Google Gemini 2.0 Flash** - Latest experimental features

## 📋 Prerequisites

- **Python 3.8+** (Backend)
- **Node.js 16+** (Frontend)  
- **Google Gemini API Key(s)** ([Get here](https://ai.google.dev/))
- **2GB+ RAM** (recommended for document processing)

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd ocr-engine
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the project root:
```env
# Primary API key (required)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Multiple keys for rotation (recommended for production)
GEMINI_API_KEY_1=your_first_api_key
GEMINI_API_KEY_2=your_second_api_key
GEMINI_API_KEY_3=your_third_api_key
# ... up to GEMINI_API_KEY_10
```

#### Start Backend Server
```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 4. Verify Installation

- Visit `http://localhost:5173` for the web interface
- Visit `http://localhost:8000/docs` for API documentation
- Check `http://localhost:8000/health` for backend status

## 🎯 Usage Guide

### Single Document OCR

1. **Select Model**: Choose your preferred Gemini AI model
2. **Upload File**: Drag & drop or browse for an image/PDF (max 50MB)
3. **Processing**: AI extracts text while showing progress
4. **Results**: View extracted text with statistics (words, characters, lines)
5. **Export**: Copy to clipboard or download as text file

**Supported Formats:**
- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP (max 10MB)
- **Documents**: PDF (max 50MB)

### Multi-PDF Financial Analysis

1. **Upload Documents**: Add 2-10 PDF files containing financial data
2. **AI Analysis**: System extracts, normalizes, and analyzes data
3. **View Results**: Explore four main sections:
   - **Methodology & Summary**: Analysis approach and executive summary
   - **Projections & Insights**: 2-3 year forecasts with confidence levels
   - **Normalized Data**: Standardized financial metrics and ratios
   - **Extracted Data**: Raw data from each document

**Key Capabilities:**
- **Trend Analysis**: Calculate growth rates and identify patterns
- **Financial Projections**: Generate yearly forecasts with confidence levels
- **Risk Assessment**: Identify potential risks and scenario analysis
- **Data Quality Scoring**: Assess completeness and reliability
- **Scenario Planning**: Optimistic and conservative projections

## 📚 API Documentation

### Core Endpoints

#### Single Document OCR
```http
POST /ocr
Content-Type: multipart/form-data

# Parameters:
- file: Image or PDF file
- model: Gemini model (optional, default: gemini-2.5-flash)
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf" \
  -F "model=gemini-2.5-pro"
```

**Example Response:**
```json
{
  "success": true,
  "data": "Extracted text content...",
  "error": null
}
```

#### Multi-PDF Analysis
```http
POST /multi-pdf/analyze  
Content-Type: multipart/form-data

# Parameters:
- files: Array of PDF files (2-10 files)
- model: Gemini model (optional, default: gemini-2.5-flash)
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/multi-pdf/analyze" \
  -F "files=@report1.pdf" \
  -F "files=@report2.pdf" \
  -F "model=gemini-2.5-flash"
```

**Example Response:**
```json
{
  "success": true,
  "extracted_data": [...],
  "normalized_data": {...},
  "projections": {...},
  "explanation": "Analysis summary...",
  "data_quality_score": 0.95,
  "confidence_levels": {...},
  "risk_factors": [...],
  "assumptions": [...]
}
```

### System Endpoints

- `GET /health` - Service health check
- `GET /models` - Available AI models  
- `GET /api-keys/status` - API key rotation status
- `POST /api-keys/rotate` - Manually rotate API key

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## 🧪 Testing

### Generate Sample PDFs
```bash
# Install reportlab if needed
pip install reportlab

# Generate test PDFs
python create_sample_pdfs.py
```

### Test Multi-PDF Analysis
```bash
# Run comprehensive test suite
python test_multi_pdf_analysis.py
```

### Frontend Testing
```bash
cd frontend
npm run lint        # Check code style
npm run build       # Test production build
npm run preview     # Preview production build
```

## 🔧 Development

### Adding New AI Models

1. **Update Backend** (`backend/routers/health.py`):
```python
models = [
    {
        "id": "new-model-id",
        "name": "New Model Name", 
        "description": "Model description"
    }
]
```

2. **Update Frontend** (`frontend/src/App.jsx`):
```javascript
const fallbackModels = [
    { id: 'new-model-id', name: 'New Model Name', description: 'Description' }
]
```

### Customizing Analysis Prompts

Modify the analysis prompt in `backend/services/multi_pdf_service.py`:
```python
prompt = """
Your custom analysis instructions here.
Specify data extraction requirements, formatting, etc.
"""
```

### Adding New API Endpoints

1. **Create Router** (`backend/routers/new_feature.py`):
```python
from fastapi import APIRouter
router = APIRouter(prefix="/new-feature", tags=["new-feature"])

@router.post("/endpoint")
async def new_endpoint():
    return {"message": "success"}
```

2. **Register Router** (`backend/main.py`):
```python
from routers import new_feature
app.include_router(new_feature.router)
```

### Frontend Component Development

Components follow this structure:
```jsx
import { motion } from 'framer-motion'

const NewComponent = ({ prop1, prop2 }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="component-class"
    >
      Component content
    </motion.div>
  )
}

export default NewComponent
```

## 🚀 Production Deployment

### Environment Variables
```env
# Production API keys
GEMINI_API_KEY_1=prod_key_1
GEMINI_API_KEY_2=prod_key_2
GEMINI_API_KEY_3=prod_key_3

# CORS origins (update for your domain)
ALLOWED_ORIGINS=https://your-app.com,https://api.your-app.com
```

### Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

### Production Checklist

- [ ] **Security**: Use HTTPS, secure API keys, validate inputs
- [ ] **Performance**: Enable compression, CDN, caching
- [ ] **Monitoring**: Set up logging, health checks, alerts  
- [ ] **Scaling**: Load balancing, multiple instances
- [ ] **Backup**: Regular data backups, disaster recovery plan

## 🔍 Troubleshooting

### Common Issues

**API Key Errors:**
```
ValueError: No API keys found
```
- Ensure `.env` file exists with valid `GEMINI_API_KEY`
- Check API key format and permissions

**File Size Errors:**
```
413 Request Entity Too Large  
```
- Reduce file size or compress images
- Check limits: Images (10MB), PDFs (50MB)

**Backend Connection Errors:**
```
No response from server
```
- Verify backend is running on port 8000
- Check firewall and network settings
- Ensure `.env` file is in project root

**Frontend Build Errors:**
```
Module not found
```
- Run `npm install` in frontend directory
- Check Node.js version (16+ required)

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### Typical Processing Times
| Document Type | Size | Processing Time |
|---------------|------|----------------|
| Image (PNG) | 1MB | 800-1500ms |
| PDF Document | 5MB | 1500-3000ms |
| Multi-PDF (3 files) | 15MB | 5000-8000ms |
| Complex Financial Analysis | 10 PDFs | 10000-15000ms |

### Optimization Tips
- **Use Gemini 2.5 Flash** for speed, Pro models for accuracy
- **Implement caching** for repeated document analysis  
- **API key rotation** prevents rate limiting
- **Batch processing** for multiple files

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new features
- Update documentation for API changes
- Use TypeScript for complex frontend components

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint for API reference
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions

---

**Built with ❤️ using FastAPI, React, and Google Gemini AI**

*Last Updated: January 2025 | Version: 2.0.0*
