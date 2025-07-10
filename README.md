# OCR Engine API - Financial Projections Service

A powerful financial analysis API built with **FastAPI** and **Google Gemini AI** that transforms financial documents into comprehensive projections and insights. Perfect for fintech applications, accounting software, and business intelligence platforms.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi) ![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?logo=google&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Quick Start for Developers

### Base URL
```
http://localhost:8000
```

### Authentication
Set your Google Gemini API key in environment variables:
```env
GEMINI_API_KEY=your_api_key_here
```

### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Core API Endpoints

### 1. Multi-Document Financial Analysis
**Endpoint:** `POST /multi-pdf/analyze`

Transform multiple financial documents into comprehensive projections with 1, 3, 5, 10, and 15-year forecasts.

```http
POST /multi-pdf/analyze
Content-Type: multipart/form-data

files: [PDF/CSV files]
model: gemini-2.5-flash (optional)
```

**Note:** For the most accurate financial projections, it is recommended to set the model to `gemini-2.5-pro`.

#### Example Request
```bash
curl -X POST "http://localhost:8000/multi-pdf/analyze" \
  -F "files=@financial_report_2023.pdf" \
  -F "files=@balance_sheet.csv" \
  -F "files=@income_statement.pdf" \
  -F "model=gemini-2.5-flash"
```

#### Example Response
```json
{
  "success": true,
  "summary": "Analysis of 3 financial documents shows strong growth trajectory...",
  "data_analysis_summary": {
    "period_granularity_detected": "monthly",
    "total_data_points": 36,
    "time_span": "January 2022 to December 2024",
    "seasonality_detected": true,
    "optimal_forecast_horizon": "3-5 years"
  },
  "projections": {
    "methodology": "SARIMA time series analysis with seasonal decomposition",
    "base_period": "December 2024 (FY2025)",
    "australian_fy_note": "Australian Financial Year runs from July 1 to June 30",
    "specific_projections": {
      "1_year_ahead": {
        "period": "FY2026",
        "granularity": "monthly",
        "data_points": 12,
        "revenue": [
          {"period": "Month 1", "value": 175000, "confidence": "high"},
          {"period": "Month 2", "value": 180000, "confidence": "high"}
        ],
        "gross_profit": [
          {"period": "Month 1", "value": 70000, "confidence": "high"},
          {"period": "Month 2", "value": 72000, "confidence": "high"}
        ],
        "expenses": [
          {"period": "Month 1", "value": 135000, "confidence": "high"},
          {"period": "Month 2", "value": 138000, "confidence": "high"}
        ],
        "net_profit": [
          {"period": "Month 1", "value": 40000, "confidence": "high"},
          {"period": "Month 2", "value": 42000, "confidence": "high"}
        ]
      },
      "3_years_ahead": {
        "period": "FY2028",
        "granularity": "quarterly", 
        "data_points": 12,
        "revenue": [...],
        "gross_profit": [...],
        "expenses": [...],
        "net_profit": [...]
      },
      "5_years_ahead": { "period": "FY2030", ... },
      "10_years_ahead": { "period": "FY2035", ... },
      "15_years_ahead": { "period": "FY2040", ... }
    },
    "assumptions": [
      "Australian economic conditions remain stable",
      "Business continues current operational model",
      "No major regulatory changes"
    ],
    "scenarios": {
      "optimistic": {
        "description": "Accelerated growth scenario",
        "growth_multiplier_1_3yr": 1.3,
        "growth_multiplier_5_10yr": 1.2
      },
      "conservative": {
        "description": "Slower growth scenario", 
        "growth_multiplier_1_3yr": 0.8,
        "growth_multiplier_5_10yr": 0.7
      }
    }
  },
  "normalized_data": {
    "time_series": {
      "revenue": [
        {"period": "2024-01", "value": 140000, "data_source": "extracted"},
        {"period": "2024-02", "value": 135000, "data_source": "extracted"}
      ],
      "growth_rates": {
        "revenue_monthly_avg": 0.025,
        "revenue_cagr": 0.18
      }
    },
    "seasonality_analysis": {
      "seasonal_patterns_detected": true,
      "peak_months": ["November", "December"],
      "trough_months": ["January", "February"]
    }
  },
  "accuracy_considerations": {
    "projection_confidence": {
      "1_year_ahead": "high",
      "3_years_ahead": "medium", 
      "5_years_ahead": "medium",
      "10_years_ahead": "low",
      "15_years_ahead": "very_low"
    },
    "risk_factors": [
      "Economic downturns could disrupt growth patterns",
      "Competition could impact long-term trajectory"
    ]
  },
  "data_quality_score": 0.92,
  "methodology": {
    "model_chosen": "SARIMA",
    "data_quality_score": 0.92,
    "validation_metrics": {
      "mape": 0.082,
      "rmse": 14500,
      "r_squared": 0.89
    }
  }
}
```

### 2. Single Document OCR
**Endpoint:** `POST /ocr`

Extract structured data from individual documents.

```http
POST /ocr
Content-Type: multipart/form-data

file: [PDF/Image/CSV file]
model: gemini-2.5-flash (optional)
```

**Note:** For the most accurate financial projections, it is recommended to set the model to `gemini-2.5-pro`.

#### Example Response
```json
{
  "success": true,
  "data": "{\n  \"company\": \"ABC Corp\",\n  \"revenue\": 1500000,\n  \"expenses\": 1200000\n}",
  "error": null
}
```

### 3. System Status
**Endpoint:** `GET /health`

Check service availability and model status.

```json
{
  "status": "healthy",
  "service": "OCR API"
}
```

**Endpoint:** `GET /models`

Get available AI models and capabilities.

```json
{
  "models": [
    {
      "id": "gemini-2.5-flash",
      "name": "Gemini 2.5 Flash", 
      "description": "Fast and efficient (Recommended)"
    },
    {
      "id": "gemini-2.5-pro",
      "name": "Gemini 2.5 Pro",
      "description": "Most capable model for complex tasks"
    }
  ],
  "default": "gemini-2.5-flash"
}
```

## Integration Examples

### Python Client
```python
import requests
import json

class OCRProjectionsClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_financial_documents(self, file_paths, model="gemini-2.5-pro"):
        """Analyze multiple financial documents and get projections"""
        files = []
        for path in file_paths:
            files.append(('files', open(path, 'rb')))
        
        data = {'model': model}
        
        response = requests.post(
            f"{self.base_url}/multi-pdf/analyze",
            files=files,
            data=data,
            timeout=300
        )
        
        # Close file handles
        for _, file_handle in files:
            file_handle.close()
            
        return response.json()
    
    def get_projections_summary(self, analysis_result):
        """Extract key projection metrics"""
        if not analysis_result.get('success'):
            return None
            
        projections = analysis_result.get('projections', {})
        specific = projections.get('specific_projections', {})
        
        return {
            'methodology': projections.get('methodology'),
            'confidence_levels': analysis_result.get('accuracy_considerations', {}).get('projection_confidence'),
            'yearly_forecasts': {
                year: {
                    'period': data.get('period'),
                    'revenue_total': sum(item['value'] for item in data.get('revenue', [])),
                    'profit_total': sum(item['value'] for item in data.get('net_profit', [])),
                    'confidence': data.get('revenue', [{}])[0].get('confidence', 'unknown')
                }
                for year, data in specific.items()
            }
        }

# Usage example
client = OCRProjectionsClient()

# Analyze documents
result = client.analyze_financial_documents([
    'financial_report.pdf',
    'balance_sheet.csv'
])

# Get projection summary
summary = client.get_projections_summary(result)
print(f"5-year revenue forecast: ${summary['yearly_forecasts']['5_years_ahead']['revenue_total']:,}")
```



## Response Schema Reference

### Projection Data Structure
Each projection period contains arrays of data points with this structure:

```typescript
interface ProjectionDataPoint {
  period: string;           // "Month 1", "Quarter 1", "Year 1", etc.
  value: number;           // Financial value in AUD
  confidence: "high" | "medium" | "low" | "very_low";
}

interface ProjectionPeriod {
  period: string;          // "FY2026", "FY2028", etc.
  granularity: "monthly" | "quarterly" | "yearly";
  data_points: number;     // Number of data points
  revenue: ProjectionDataPoint[];      // MANDATORY
  gross_profit: ProjectionDataPoint[]; // MANDATORY  
  expenses: ProjectionDataPoint[];     // MANDATORY
  net_profit: ProjectionDataPoint[];   // MANDATORY
}
```

### Confidence Levels
- **high** (>80%): Strong data foundation, reliable short-term projections
- **medium** (60-80%): Good data quality with some uncertainty factors
- **low** (<60%): Limited data or high uncertainty in projections  
- **very_low** (<40%): Long-term extrapolation with high uncertainty

### Australian Financial Year Support
- **FY Format**: FY2025 = July 1, 2024 to June 30, 2025
- **Automatic Detection**: System detects document periods and aligns projections
- **Seasonal Analysis**: Accounts for Australian business cycles and patterns

## Setup & Development

### Requirements
- Python 3.8+
- Google Gemini API Key

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd ocr-engine

# Backend setup
cd backend
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Start server
python main.py
```

Server runs on `http://localhost:8000`

### Docker Deployment
```bash
# Build and run
docker build -t ocr-engine .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key ocr-engine
```

## Use Cases

### Fintech Applications
- **Portfolio Analysis**: Analyze startup financial documents for investment decisions
- **Credit Scoring**: Extract financial metrics for loan approval algorithms
- **Financial Planning**: Generate projections for personal finance apps

### Business Intelligence
- **Competitive Analysis**: Compare financial performance across multiple companies
- **Market Research**: Analyze industry trends from financial reports
- **Due Diligence**: Automated financial document analysis for M&A

### Accounting Software
- **Automated Forecasting**: Generate financial projections from historical data
- **Audit Support**: Extract and validate financial data from various sources
- **Compliance Reporting**: Standardize financial data across different formats

## Rate Limits & Performance

| Operation | Rate Limit | Typical Response Time |
|-----------|------------|----------------------|
| Single OCR | 100/minute | 1-3 seconds |
| Multi-PDF Analysis | 10/minute | 15-60 seconds |
| System Status | 1000/minute | <100ms |

### File Limits
- **PDFs**: Max 50MB each, up to 10 files per request
- **CSV**: Max 25MB each, up to 10 files per request  
- **Images**: Max 10MB each (single OCR only)

## Security & Best Practices

### API Key Management
- Store API keys securely in environment variables
- Rotate keys regularly for production systems
- Use separate keys for development/production environments

### Input Validation
- All file uploads are validated for type and size
- Malicious content detection for uploaded documents
- Rate limiting prevents abuse

### Data Privacy
- Documents are processed in memory only
- No persistent storage of uploaded files
- All processing happens server-side with Google AI

## Support & Contributing

- **API Issues**: Check `/health` endpoint for service status
- **Documentation**: Interactive docs at `/docs`
- **Bug Reports**: Submit GitHub issues with reproduction steps
- **Feature Requests**: Open GitHub discussions

---

**Built for developers who need reliable financial projections from document data.**

*Latest Version: 2.1.0 | API Version: v1*
