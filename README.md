# OCR Engine 🔍

A comprehensive document analysis platform built with **FastAPI** and **React** that leverages **Google Gemini AI** for intelligent text extraction and advanced financial data analysis. The platform offers both single document OCR and sophisticated multi-file financial analysis with projections.

![OCR Engine](https://img.shields.io/badge/OCR-Engine-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi) ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black) ![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?logo=google&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white)

## 🌟 Features

### 📄 Single Document OCR
- **Multi-format Support**: Process images (PNG, JPG, JPEG, GIF, BMP, TIFF, WebP), PDF documents, and CSV files
- **High Accuracy**: Preserves original document formatting, structure, and layout
- **Real-time Processing**: Fast text extraction with visual feedback
- **Export Options**: Copy to clipboard or download as text file

### 📊 Multi-File Financial Analysis (Advanced)
- **Hybrid File Processing**: Analyze multiple PDFs and CSV files together in a single analysis
- **Data Extraction**: Automatically extract financial data from diverse document formats
- **Data Normalization**: Standardize and combine data across different document types
- **Financial Projections**: Generate forecasts for 1, 3, 5, 10, and 15 years with confidence levels
- **Complete Financial Schema**: Enforced projection of all four key metrics: revenue, gross profit, expenses, and net profit
- **Risk Assessment**: Comprehensive risk analysis and scenario planning
- **Trend Analysis**: Calculate growth rates, seasonal patterns, and financial ratios
- **Australian FY Support**: Automatic detection and alignment with Australian Financial Year (July-June)
- **Interactive Results**: Expandable sections with detailed JSON data and visualizations

### 🚀 Technical Features
- **Latest AI Models**: Support for Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash, 1.5 Flash, and 1.5 Pro
- **New GenAI SDK**: Built with Google's latest `google-genai` SDK (v1.24.0+)
- **Smart API Key Rotation**: Automatic rotation across multiple API keys for reliability
- **Modern UI**: React 19 with TailwindCSS, Framer Motion animations, and responsive design
- **Configurable Prompts**: Centralized prompt management system for analysis customization
- **Real-time Monitoring**: Health checks, performance metrics, and comprehensive error handling
- **Scalable Architecture**: Production-ready microservices design

## 🏗️ Architecture

```
ocr-engine/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Application entry point & routing
│   ├── config.py              # Configuration & API key management
│   ├── middleware.py          # Error handling middleware
│   ├── models.py              # Pydantic data models
│   ├── prompts.py             # ⭐ Centralized AI prompts configuration
│   ├── requirements.txt       # Python dependencies
│   ├── routers/               # API route handlers
│   │   ├── admin.py          # API key management
│   │   ├── health.py         # Health & system info
│   │   ├── multi_pdf.py      # Multi-file analysis
│   │   └── ocr.py           # Single document OCR
│   └── services/             # Business logic
│       ├── ocr_service.py   # OCR processing
│       └── multi_pdf_service.py # Financial analysis engine
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
│   ├── postcss.config.js     # ⭐ PostCSS/TailwindCSS config
│   └── vite.config.js        # Vite configuration
├── create_sample_pdfs.py      # Generate test PDFs
├── test_multi_pdf_analysis.py # Test script
└── README.md                  # This file
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Google GenAI SDK** (v1.24.0+) - Latest multimodal AI SDK for document processing
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production deployment
- **Python-dotenv** - Environment variable management

### Frontend  
- **React 19.1** - Latest React with concurrent features and modern hooks
- **Vite 7.0** - Next-generation build tool for lightning-fast development
- **TailwindCSS 3.4** - Utility-first CSS framework for rapid UI development
- **Framer Motion 12.22** - Production-ready motion library for smooth animations
- **Axios 1.10** - Promise-based HTTP client with interceptors
- **React Dropzone 14.3** - File upload with drag & drop support
- **Lucide React 0.525** - Beautiful, customizable icon library

### AI & Processing
- **Google Gemini 2.5 Flash** - Fast, efficient processing (recommended for most tasks)
- **Google Gemini 2.5 Pro** - Advanced reasoning for complex financial documents
- **Google Gemini 2.0 Flash** - Latest experimental features and capabilities
- **Google Gemini 1.5 Flash** - Reliable, cost-effective processing
- **Google Gemini 1.5 Pro** - Enhanced reasoning for detailed analysis

## 📋 Prerequisites

- **Python 3.8+** (Backend)
- **Node.js 18+** (Frontend - updated for React 19)  
- **Google Gemini API Key(s)** ([Get here](https://ai.google.dev/))
- **4GB+ RAM** (recommended for multi-file processing)

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

# Optional: Custom CORS origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
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
- Visit `http://localhost:8000/docs` for interactive API documentation
- Check `http://localhost:8000/health` for backend status
- Verify `http://localhost:8000/models` for available AI models

## 🎯 Usage Guide

### Single Document OCR

1. **Select Model**: Choose your preferred Gemini AI model from 5 available options
2. **Upload File**: Drag & drop or browse for an image, PDF, or CSV file
3. **Processing**: AI extracts text while showing real-time progress
4. **Results**: View extracted text with detailed statistics (words, characters, lines)
5. **Export**: Copy to clipboard or download as text file

**Supported Formats:**
- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP (max 10MB)
- **Documents**: PDF (max 50MB)
- **Spreadsheets**: CSV (max 25MB)

### Multi-File Financial Analysis

1. **Upload Documents**: Add 2-10 files (PDFs and/or CSV files) containing financial data
2. **AI Analysis**: System extracts, normalizes, and analyzes data using enhanced prompts
3. **View Results**: Explore comprehensive analysis sections:
   - **📋 Methodology & Summary**: Analysis approach, model selection, and executive summary
   - **📈 Projections & Insights**: 1, 3, 5, 10, and 15-year forecasts with confidence levels
   - **📊 Normalized Data**: Standardized financial metrics, ratios, and seasonal analysis
   - **📄 Extracted Data**: Raw data from each source document

**Key Capabilities:**
- **Comprehensive Projections**: All forecasts include revenue, gross profit, expenses, and net profit
- **Australian FY Alignment**: Automatic detection and alignment with July-June financial years
- **Advanced Analytics**: Growth rates, seasonality patterns, and financial ratio analysis
- **Risk & Scenario Analysis**: Multiple scenario projections with confidence scoring
- **Data Quality Assessment**: Completeness scoring and reliability validation

## 📚 API Documentation

### Core Endpoints

#### Single Document OCR
```http
POST /ocr
Content-Type: multipart/form-data

# Parameters:
- file: Image, PDF, or CSV file
- model: Gemini model (optional, default: gemini-2.5-flash)
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@document.pdf" \
  -F "model=gemini-2.5-flash"
```

**Example Response:**
```json
{
  "success": true,
  "data": "Extracted text content...",
  "error": null
}
```

#### Multi-File Analysis
```http
POST /multi-pdf/analyze  
Content-Type: multipart/form-data

# Parameters:
- files: Array of PDF and/or CSV files (2-10 files)
- model: Gemini model (optional, default: gemini-2.5-flash)
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/multi-pdf/analyze" \
  -F "files=@financial_report.pdf" \
  -F "files=@balance_sheet.csv" \
  -F "files=@income_statement.pdf" \
  -F "model=gemini-2.5-pro"
```

**Example Response:**
```json
{
  "success": true,
  "extracted_data": [...],
  "normalized_data": {
    "time_series": {
      "revenue": [...],
      "gross_profit": [...],
      "expenses": [...],
      "net_profit": [...]
    },
    "seasonality_analysis": {...},
    "growth_rates": {...}
  },
  "projections": {
    "methodology": {...},
    "specific_projections": {
      "1_year_ahead": {
        "revenue": [...],
        "gross_profit": [...],
        "expenses": [...],
        "net_profit": [...]
      },
      "3_years_ahead": {...},
      "5_years_ahead": {...},
      "10_years_ahead": {...},
      "15_years_ahead": {...}
    }
  },
  "data_quality_score": 0.95,
  "confidence_levels": {...},
  "risk_factors": [...],
  "assumptions": [...],
  "data_analysis_summary": {...}
}
```

### System Endpoints

- `GET /health` - Service health check
- `GET /models` - Available AI models with descriptions
- `GET /api-keys/status` - API key rotation status
- `POST /api-keys/rotate` - Manually rotate API key

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing and schema exploration.

## 🧪 Testing

### Generate Sample PDFs
```bash
# Install reportlab if needed
pip install reportlab

# Generate test financial PDFs and CSVs
python create_sample_pdfs.py
```

### Test Multi-File Analysis
```bash
# Run comprehensive test suite with real financial data
python test_multi_pdf_analysis.py
```

### Frontend Testing
```bash
cd frontend
npm run lint        # Check code style with ESLint
npm run build       # Test production build
npm run preview     # Preview production build locally
```

## 🔧 Development

### Customizing Analysis Prompts

The project uses a centralized prompt configuration system. Edit `backend/prompts.py` to customize:

```python
# OCR prompt for single documents
OCR_PROMPT = """Your custom OCR instructions..."""

# Multi-file analysis prompt with financial projections
MULTI_PDF_PROMPT = """Your enhanced analysis instructions...
🚨 MANDATORY FINANCIAL METRICS SCHEMA ENFORCEMENT 🚨
All projection periods must include: revenue, gross_profit, expenses, net_profit
"""
```

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

### Frontend Styling with TailwindCSS

The project uses TailwindCSS for styling. Key configuration files:
- `frontend/postcss.config.js` - PostCSS configuration
- Component styles use Tailwind utility classes
- Custom styles in `frontend/src/App.css`

Example component with Tailwind:
```jsx
const CustomComponent = () => (
  <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
    <h2 className="text-2xl font-bold text-gray-800 mb-4">Title</h2>
    <p className="text-gray-600 leading-relaxed">Content</p>
  </div>
)
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

## 🚀 Production Deployment

### Environment Variables
```env
# Production API keys (use multiple for redundancy)
GEMINI_API_KEY_1=prod_key_1
GEMINI_API_KEY_2=prod_key_2
GEMINI_API_KEY_3=prod_key_3

# CORS origins (update for your domain)
ALLOWED_ORIGINS=https://your-app.com,https://api.your-app.com
```

### Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: 
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Production Checklist

- [ ] **Security**: HTTPS, secure API keys, input validation, rate limiting
- [ ] **Performance**: Compression, CDN, caching, optimized images
- [ ] **Monitoring**: Structured logging, health checks, performance metrics
- [ ] **Scaling**: Load balancing, horizontal scaling, database optimization
- [ ] **Backup**: Regular data backups, disaster recovery procedures

## 🔍 Troubleshooting

### Common Issues

**API Key Errors:**
```
ValueError: No API keys found
```
- Ensure `.env` file exists in project root with valid `GEMINI_API_KEY`
- Check API key format and Google AI Studio permissions
- Verify API key quota and billing status

**New SDK Import Errors:**
```
ImportError: No module named 'google.genai'
```
- Ensure you're using the new SDK: `pip install google-genai>=1.24.0`
- Remove old SDK if present: `pip uninstall google-generativeai`

**File Size Errors:**
```
413 Request Entity Too Large  
```
- Reduce file size or compress images
- Check limits: Images (10MB), PDFs (50MB), CSV (25MB)
- For large datasets, split CSV files into smaller chunks

**Frontend Build Errors:**
```
Module not found or dependency issues
```
- Ensure Node.js 18+ is installed
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**TailwindCSS Not Working:**
```
Styles not applying correctly
```
- Verify PostCSS configuration in `postcss.config.js`
- Check TailwindCSS is in package.json dependencies
- Restart development server after config changes

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

For frontend debugging:
```javascript
// In browser console
localStorage.setItem('debug', 'true')
```

## 📊 Performance

### Typical Processing Times
| Document Type | Size | Model | Processing Time |
|---------------|------|-------|----------------|
| Image (PNG) | 1MB | Flash | 500-1000ms |
| PDF Document | 5MB | Flash | 1500-2500ms |
| CSV File | 2MB | Flash | 300-800ms |
| Multi-File (3 PDFs + 2 CSVs) | 20MB | Flash | 8000-12000ms |
| Complex Financial Analysis | 10 files | Pro | 15000-25000ms |

### Optimization Tips
- **Use Gemini 2.5 Flash** for speed, Pro models for complex analysis
- **Implement request caching** for repeated document analysis  
- **API key rotation** prevents rate limiting and improves reliability
- **File preprocessing** (compression, format conversion) reduces processing time
- **Batch similar documents** for more efficient analysis

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Install dependencies**: Follow setup instructions for both backend and frontend
4. **Make changes**: Update code, tests, and documentation
5. **Test thoroughly**: Run all tests and verify functionality
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Development Guidelines
- Follow existing code style (Python PEP 8, JavaScript Standard)
- Add tests for new features and bug fixes
- Update documentation for API changes
- Use TypeScript interfaces for complex frontend components
- Follow TailwindCSS utility-first approach for styling
- Update prompts configuration for analysis improvements

### Testing Requirements
- Backend: Include unit tests for new services and endpoints
- Frontend: Test new components with user interactions
- Integration: Verify end-to-end functionality
- Performance: Benchmark new features with realistic data

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Interactive API docs at `/docs` endpoint
- **Issues**: Report bugs via GitHub Issues with detailed reproduction steps
- **Discussions**: Join GitHub Discussions for questions and feature requests
- **API Reference**: Complete OpenAPI specification available at `/docs`

## 🔄 Changelog

### Version 2.1.0 (Latest)
- ✨ **New**: CSV file support in multi-file analysis
- ✨ **New**: Enhanced financial schema enforcement (4 mandatory metrics)
- ✨ **New**: Centralized prompts configuration system
- 🔧 **Updated**: Google GenAI SDK v1.24.0+ (latest)
- 🔧 **Updated**: React 19.1 with latest features
- 🔧 **Updated**: TailwindCSS 3.4 integration
- 🐛 **Fixed**: JSON extraction reliability improvements
- 🐛 **Fixed**: File type validation and error handling

### Version 2.0.0
- ✨ Multi-PDF financial analysis with projections
- ✨ Australian FY support and seasonal analysis
- ✨ Advanced risk assessment and scenario planning
- 🔧 API key rotation system
- 🔧 Modern React frontend with animations

---

**Built with ❤️ using FastAPI, React 19, TailwindCSS, and Google Gemini AI**

*Last Updated: January 2025 | Version: 2.1.0*
