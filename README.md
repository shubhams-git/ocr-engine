# OCR Engine - Financial Document Analysis Service

A FastAPI-based financial analysis service that extracts, analyzes, and generates comprehensive projections from financial documents using AI-powered document processing.

## What It Does

The OCR Engine is a sophisticated financial analysis service that:

- **Extracts data** from financial documents (PDFs, images, CSV files)
- **Analyzes business context** using advanced AI to understand industry patterns, seasonality, and financial health
- **Generates comprehensive projections** with 3-way financial forecasts (P&L, Cash Flow, Balance Sheet)
- **Provides multiple scenarios** (optimistic, base case, conservative) with confidence levels
- **Supports Australian Financial Year** calculations and business patterns
- **Offers both single document OCR** and **multi-document analysis** capabilities

## Architecture

### 3-Stage Enhanced Processing Pipeline

1. **Stage 1: Data Extraction & Normalization**
   - Document classification and data extraction
   - Quality assessment and anomaly detection
   - Australian FY alignment and standardization

2. **Stage 2: Business Intelligence Analysis**
   - Business context identification (industry, stage, market position)
   - Pattern recognition and trend analysis
   - Forecasting methodology selection
   - Working capital and driver analysis

3. **Stage 3: Projection Engine**
   - Multi-horizon financial projections (1, 3, 5, 10, 15 years)
   - 3-way forecast generation (P&L, Cash Flow, Balance Sheet)
   - Scenario planning and sensitivity analysis
   - Validation and reconciliation

## Project Structure

```
ocr-engine/
├── backend/                    # FastAPI backend service
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic response models
│   ├── prompts.py             # AI prompts configuration
│   ├── routers/               # API endpoints
│   │   ├── ocr.py            # Single document OCR
│   │   ├── multi_pdf.py      # Multi-document analysis
│   │   ├── health.py         # Health checks
│   │   └── admin.py          # Testing and admin endpoints
│   └── services/              # Business logic
│       ├── ocr_service.py           # Document processing
│       ├── multi_pdf_service.py     # Multi-document analysis
│       ├── business_analysis_service.py  # Stage 2 analysis
│       └── projection_service.py    # Stage 3 projections
├── frontend/                   # React frontend (optional)
│   ├── src/
│   │   ├── components/        # React components
│   │   └── services/          # API client
│   └── package.json
├── .env.template              # Environment variables template
└── requirements.txt           # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Node.js 16+ (for frontend)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-engine
   ```

2. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Configure API Keys**
   ```bash
   # In .env file
   GEMINI_API_KEY=your_gemini_api_key_here
   # Or for multiple keys (recommended for production)
   GEMINI_API_KEY_1=key1
   GEMINI_API_KEY_2=key2
   GEMINI_API_KEY_3=key3
   ```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ocr` | POST | Single document OCR processing |
| `/multi-pdf/analyze` | POST | Multi-document financial analysis |
| `/health` | GET | Service health check |
| `/models` | GET | Available AI models |

### Testing Endpoints (Admin)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/test/stage1` | POST | Test Stage 1 processing |
| `/admin/test/stage2` | POST | Test Stage 2 analysis |
| `/admin/test/stage3` | POST | Test Stage 3 projections |
| `/admin/test/full-process` | POST | Test complete pipeline |

## Integration with Existing FastAPI Applications

### Option 1: Direct Router Integration

```python
from fastapi import FastAPI
from ocr_engine.backend.routers import ocr, multi_pdf, health

app = FastAPI()

# Include OCR Engine routers
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(multi_pdf.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
```

### Option 2: Service Integration

```python
from ocr_engine.backend.services.multi_pdf_service import EnhancedMultiPDFService

# Initialize service
analysis_service = EnhancedMultiPDFService()

# Use in your endpoints
@app.post("/your-endpoint/analyze")
async def analyze_documents(files: List[UploadFile]):
    files_data = [(file.filename, await file.read()) for file in files]
    result = await analysis_service.analyze_multiple_files(files_data)
    return result
```

### Option 3: Microservice Integration

```python
import httpx

class OCREngineClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def analyze_documents(self, files: List[bytes], model: str = "gemini-2.5-flash"):
        files_data = [("files", file) for file in files]
        response = await self.client.post(
            f"{self.base_url}/multi-pdf/analyze",
            files=files_data,
            data={"model": model}
        )
        return response.json()
```

## API Usage Examples

### Single Document OCR

```python
import requests

def process_single_document(file_path: str):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'model': 'gemini-2.5-flash'}
        
        response = requests.post(
            'http://localhost:8000/ocr',
            files=files,
            data=data
        )
        
        return response.json()
```

### Multi-Document Analysis

```python
import requests

def analyze_financial_documents(file_paths: List[str]):
    files = []
    for file_path in file_paths:
        files.append(('files', open(file_path, 'rb')))
    
    data = {'model': 'gemini-2.5-pro'}
    
    response = requests.post(
        'http://localhost:8000/multi-pdf/analyze',
        files=files,
        data=data,
        timeout=300  # 5 minutes timeout
    )
    
    # Clean up file handles
    for _, file_handle in files:
        file_handle.close()
    
    return response.json()
```

## Response Structure

### Multi-Document Analysis Response

```json
{
  "success": true,
  "extracted_data": [...],
  "normalized_data": {
    "business_context": {...},
    "pattern_analysis": {...},
    "time_series": {...}
  },
  "projections": {
    "base_case_projections": {
      "1_year_ahead": {
        "period_label": "FY2025",
        "granularity": "monthly",
        "profit_and_loss": [...],
        "cash_flow_statement": [...],
        "balance_sheet": [...]
      }
    },
    "scenario_projections": {
      "optimistic": {...},
      "conservative": {...}
    }
  },
  "data_quality_assessment": {...},
  "accuracy_considerations": {...},
  "methodology": "...",
  "explanation": "..."
}
```

## Configuration

### Environment Variables

```bash
# API Configuration
GEMINI_API_KEY=your_api_key
GEMINI_API_KEY_1=key1  # Multiple keys for load balancing
GEMINI_API_KEY_2=key2
GEMINI_API_KEY_3=key3

# Timeouts
API_TIMEOUT=300
OVERALL_PROCESS_TIMEOUT=600
MAX_RETRIES=3
RETRY_DELAY=1

# CORS (for frontend)
CORS_ORIGINS=["http://localhost:5173", "https://yourdomain.com"]
```

### Model Configuration

Available models:
- `gemini-2.5-pro` - Most capable for complex analysis
- `gemini-2.5-flash` - Fast and efficient (recommended)
- `gemini-2.0-flash` - Latest experimental model
- `gemini-1.5-flash` - Fast and reliable
- `gemini-1.5-pro` - Advanced reasoning capabilities

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Test Single Document Processing

```bash
curl -X POST \
  http://localhost:8000/admin/test/stage1 \
  -F "file=@test_document.pdf" \
  -F "model=gemini-2.5-flash"
```

### Test Multi-Document Analysis

```bash
curl -X POST \
  http://localhost:8000/admin/test/full-process \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "model=gemini-2.5-pro"
```

## Supported File Types

- **PDFs**: Financial statements, reports (max 50MB)
- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP (max 10MB)
- **CSV**: Structured financial data (max 25MB)
- **Multiple Files**: Up to 10 files per request

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO
API_TIMEOUT=300
CORS_ORIGINS=["https://yourdomain.com"]

# Multiple API keys for load balancing
GEMINI_API_KEY_1=key1
GEMINI_API_KEY_2=key2
GEMINI_API_KEY_3=key3
```

## Monitoring

### Health Endpoints

- `GET /health` - Basic health check
- `GET /admin/health/detailed` - Detailed system health
- `GET /admin/performance/metrics` - Performance metrics

### Logging

The service includes comprehensive logging:
- Request/response logging
- API call tracking
- Stage progression monitoring
- Error tracking and debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure GEMINI_API_KEY is set in environment
   - Check API key has sufficient quota
   - Verify API key permissions

2. **File Upload Issues**
   - Check file size limits (50MB PDF, 10MB images, 25MB CSV)
   - Verify file format is supported
   - Ensure proper Content-Type headers

3. **Processing Timeouts**
   - Increase API_TIMEOUT for large files
   - Use gemini-2.5-flash for faster processing
   - Consider splitting large document sets

### Support

For issues and questions:
1. Check the logs for detailed error messages
2. Use the `/admin/health/detailed` endpoint for system diagnostics
3. Test individual stages using the admin endpoints
4. Review the API documentation at `http://localhost:8000/docs`

## Performance Optimization

### Recommended Settings

```python
# For high-volume usage
GEMINI_API_KEY_1=key1
GEMINI_API_KEY_2=key2
GEMINI_API_KEY_3=key3
MAX_RETRIES=2
RETRY_DELAY=0.5
API_TIMEOUT=180

# Use faster models for production
DEFAULT_MODEL=gemini-2.5-flash
```

### Scaling Considerations

- Use multiple API keys for load balancing
- Implement Redis caching for repeated analyses
- Consider async processing for large document sets
- Monitor API usage and implement rate limiting
