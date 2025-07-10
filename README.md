# OCR Engine API - Financial Projections Service

A FastAPI-based microservice that transforms financial documents (PDFs, CSVs) into structured projection data using Google Gemini AI. Designed for integration with other FastAPI backends that need automated financial forecasting capabilities.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi) ![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?logo=google&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Overview

This service processes financial documents and returns standardized projection data with **4 core financial metrics** across **5 time horizons**:

### Financial Metrics (Always Included)
- **Revenue**: Income from sales/services
- **Gross Profit**: Revenue minus cost of goods sold
- **Expenses**: Operating and administrative costs
- **Net Profit**: Bottom-line profit after all expenses

### Time Horizons (Fixed Intervals)
- **1 Year Ahead**: Monthly granularity (12 data points)
- **3 Years Ahead**: Quarterly granularity (12 data points) 
- **5 Years Ahead**: Yearly granularity (12 data points)
- **10 Years Ahead**: Yearly granularity (12 data points)
- **15 Years Ahead**: Yearly granularity (12 data points)

## Codebase Structure

```
ocr-engine/
├── backend/                    # FastAPI service
│   ├── main.py                # FastAPI app entry point
│   ├── routers/               # API endpoints
│   │   ├── multi_pdf.py       # Main projection endpoint
│   │   └── ocr.py            # Single document OCR
│   ├── services/              # Business logic
│   │   ├── multi_pdf_service.py  # Document analysis & projections
│   │   └── ocr_service.py        # Document text extraction
│   ├── models.py              # Pydantic response models
│   ├── prompts.py             # AI prompts for financial analysis
│   └── config.py              # API key management
└── frontend/                  # React UI (optional)
```

### Key Components for Integration

1. **`/multi-pdf/analyze` endpoint**: Main service for projection data
2. **`MultiPDFAnalysisResponse` model**: Structured response format
3. **`multi_pdf_service.py`**: Core projection logic using Gemini AI
4. **`prompts.py`**: Financial analysis prompts ensuring consistent output

## Service URL & Authentication

```bash
# Default service URL
BASE_URL = "http://localhost:8000"

# Required environment variable
GEMINI_API_KEY = "your_google_gemini_api_key"
```

## Core Integration Pattern

### 1. Basic Request Structure

```http
POST /multi-pdf/analyze
Content-Type: multipart/form-data

files: [financial_documents.pdf/csv]
model: gemini-2.5-pro (recommended for accuracy)
```

### 2. Projection Data Response Structure

The service returns projection data in this standardized format:

```json
{
  "success": true,
  "projections": {
    "specific_projections": {
      "1_year_ahead": {
        "period": "FY2026",
        "granularity": "monthly",
        "data_points": 12,
        "revenue": [
          {"period": "Month 1", "value": 175000, "confidence": "high"},
          {"period": "Month 2", "value": 180000, "confidence": "high"},
          // ... 10 more months
        ],
        "gross_profit": [
          {"period": "Month 1", "value": 70000, "confidence": "high"},
          {"period": "Month 2", "value": 72000, "confidence": "high"},
          // ... 10 more months
        ],
        "expenses": [
          {"period": "Month 1", "value": 135000, "confidence": "high"},
          {"period": "Month 2", "value": 138000, "confidence": "high"},
          // ... 10 more months
        ],
        "net_profit": [
          {"period": "Month 1", "value": 40000, "confidence": "high"},
          {"period": "Month 2", "value": 42000, "confidence": "high"},
          // ... 10 more months
        ]
      },
      "3_years_ahead": {
        "period": "FY2028",
        "granularity": "quarterly",
        "data_points": 12,
        "revenue": [...], // 12 quarterly projections
        "gross_profit": [...],
        "expenses": [...],
        "net_profit": [...]
      },
      "5_years_ahead": {
        "period": "FY2030",
        "granularity": "yearly", 
        "data_points": 12,
        "revenue": [...], // 12 yearly projections
        "gross_profit": [...],
        "expenses": [...],
        "net_profit": [...]
      },
      "10_years_ahead": { /* same structure */ },
      "15_years_ahead": { /* same structure */ }
    }
  }
}
```

## FastAPI Client Integration

### Complete Client Class

```python
import httpx
import asyncio
from typing import List, Dict, Optional
from fastapi import HTTPException

class FinancialProjectionsClient:
    """Client for integrating OCR Engine projections into FastAPI backends"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 300.0  # 5 minutes for document processing
        
    async def get_financial_projections(
        self, 
        file_paths: List[str], 
        model: str = "gemini-2.5-pro"
    ) -> Dict:
        """
        Get financial projections from documents
        
        Returns structured projection data with 4 metrics across 5 time periods
        """
        files = []
        try:
            # Prepare files for upload
            for path in file_paths:
                with open(path, 'rb') as f:
                    files.append(('files', (path, f.read(), 'application/pdf')))
            
            data = {'model': model}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/multi-pdf/analyze",
                    files=files,
                    data=data
                )
                
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Projection service error: {response.text}"
                )
                
            return response.json()
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get projections: {str(e)}"
            )
    
    def extract_projection_data(self, response: Dict) -> Dict:
        """
        Extract clean projection data for each time period and metric
        
        Returns: {
            "1_year": {"revenue": [...], "gross_profit": [...], "expenses": [...], "net_profit": [...]},
            "3_year": {"revenue": [...], "gross_profit": [...], "expenses": [...], "net_profit": [...]},
            "5_year": {"revenue": [...], "gross_profit": [...], "expenses": [...], "net_profit": [...]},
            "10_year": {"revenue": [...], "gross_profit": [...], "expenses": [...], "net_profit": [...]},
            "15_year": {"revenue": [...], "gross_profit": [...], "expenses": [...], "net_profit": [...]}
        }
        """
        if not response.get('success'):
            raise ValueError(f"Analysis failed: {response.get('error', 'Unknown error')}")
        
        projections = response.get('projections', {}).get('specific_projections', {})
        
        # Map time periods to clean names
        time_mapping = {
            "1_year_ahead": "1_year",
            "3_years_ahead": "3_year", 
            "5_years_ahead": "5_year",
            "10_years_ahead": "10_year",
            "15_years_ahead": "15_year"
        }
        
        extracted_data = {}
        
        for period_key, clean_name in time_mapping.items():
            if period_key in projections:
                period_data = projections[period_key]
                
                extracted_data[clean_name] = {
                    "period_info": {
                        "period": period_data.get("period"),
                        "granularity": period_data.get("granularity"),
                        "data_points": period_data.get("data_points")
                    },
                    "revenue": period_data.get("revenue", []),
                    "gross_profit": period_data.get("gross_profit", []),
                    "expenses": period_data.get("expenses", []),
                    "net_profit": period_data.get("net_profit", [])
                }
        
        return extracted_data
    
    def calculate_totals(self, projection_data: Dict) -> Dict:
        """
        Calculate total values for each metric across all time periods
        
        Returns summary totals for easy comparison
        """
        totals = {}
        
        for time_period, data in projection_data.items():
            totals[time_period] = {}
            
            for metric in ["revenue", "gross_profit", "expenses", "net_profit"]:
                metric_data = data.get(metric, [])
                total_value = sum(item.get("value", 0) for item in metric_data)
                avg_confidence = self._calculate_avg_confidence(metric_data)
                
                totals[time_period][metric] = {
                    "total": total_value,
                    "average_confidence": avg_confidence,
                    "data_points_count": len(metric_data)
                }
        
        return totals
    
    def _calculate_avg_confidence(self, metric_data: List[Dict]) -> str:
        """Helper to calculate average confidence level"""
        if not metric_data:
            return "unknown"
        
        confidence_scores = {"high": 4, "medium": 3, "low": 2, "very_low": 1}
        score_to_confidence = {4: "high", 3: "medium", 2: "low", 1: "very_low"}
        
        total_score = 0
        count = 0
        
        for item in metric_data:
            confidence = item.get("confidence", "medium")
            if confidence in confidence_scores:
                total_score += confidence_scores[confidence]
                count += 1
        
        if count == 0:
            return "medium"
        
        avg_score = round(total_score / count)
        return score_to_confidence.get(avg_score, "medium")
```

### FastAPI Endpoint Integration Example

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import tempfile
import os

app = FastAPI()
projections_client = FinancialProjectionsClient()

@app.post("/analyze-financials")
async def analyze_financial_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to analyze financial documents and return projection data
    """
    temp_files = []
    
    try:
        # Save uploaded files temporarily
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        # Get projections from OCR Engine service
        raw_response = await projections_client.get_financial_projections(temp_files)
        
        # Extract clean projection data
        projection_data = projections_client.extract_projection_data(raw_response)
        
        # Calculate totals for summary
        totals = projections_client.calculate_totals(projection_data)
        
        return {
            "success": True,
            "projection_data": projection_data,
            "summary_totals": totals,
            "methodology": raw_response.get("projections", {}).get("methodology"),
            "confidence_info": raw_response.get("accuracy_considerations", {}).get("projection_confidence", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

@app.get("/projection-summary/{time_period}")
async def get_projection_summary(time_period: str):
    """
    Get summary for a specific time period (1_year, 3_year, 5_year, 10_year, 15_year)
    """
    # This would typically fetch from your database where you've stored projection results
    # Example response structure:
    return {
        "time_period": time_period,
        "metrics": {
            "revenue": {"total": 2500000, "confidence": "high"},
            "gross_profit": {"total": 1000000, "confidence": "high"}, 
            "expenses": {"total": 1800000, "confidence": "high"},
            "net_profit": {"total": 700000, "confidence": "high"}
        },
        "granularity": "monthly" if time_period == "1_year" else "quarterly" if time_period == "3_year" else "yearly"
    }
```

## Usage Examples

### Simple Projection Retrieval

```python
# Initialize client
client = FinancialProjectionsClient()

# Get projections
response = await client.get_financial_projections([
    "financial_report_2024.pdf",
    "balance_sheet.csv"
])

# Extract structured data
projection_data = client.extract_projection_data(response)

# Access specific metrics
revenue_1_year = projection_data["1_year"]["revenue"]
profit_5_year = projection_data["5_year"]["net_profit"]

# Get totals
totals = client.calculate_totals(projection_data)
total_5_year_revenue = totals["5_year"]["revenue"]["total"]
```

### Confidence-Based Decision Making

```python
def evaluate_projection_reliability(projection_data):
    """Evaluate which projections are most reliable"""
    reliable_projections = {}
    
    for time_period, data in projection_data.items():
        period_reliability = {}
        
        for metric in ["revenue", "gross_profit", "expenses", "net_profit"]:
            metric_data = data[metric]
            high_confidence_count = sum(
                1 for item in metric_data 
                if item.get("confidence") in ["high", "medium"]
            )
            
            reliability_score = high_confidence_count / len(metric_data) if metric_data else 0
            period_reliability[metric] = {
                "reliability_score": reliability_score,
                "recommended": reliability_score >= 0.7
            }
        
        reliable_projections[time_period] = period_reliability
    
    return reliable_projections
```

## Response Data Guarantees

The service **guarantees** that every successful response contains:

1. **All 4 Financial Metrics**: revenue, gross_profit, expenses, net_profit
2. **All 5 Time Periods**: 1, 3, 5, 10, 15 years ahead
3. **Consistent Data Structure**: Each metric has array of {"period", "value", "confidence"}
4. **Australian FY Alignment**: Periods automatically aligned to July-June financial years
5. **Confidence Scoring**: Every data point includes confidence level

## Error Handling

```python
try:
    response = await client.get_financial_projections(file_paths)
    projection_data = client.extract_projection_data(response)
except HTTPException as e:
    # Handle API errors (network, service down, etc.)
    logger.error(f"Service error: {e.detail}")
except ValueError as e:
    # Handle analysis errors (invalid documents, processing failed)
    logger.error(f"Analysis error: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

## Service Setup

### Requirements
- Python 3.8+
- Google Gemini API key
- FastAPI backend (your main service)

### Quick Start
```bash
# Start OCR Engine service
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your_api_key
python main.py  # Runs on http://localhost:8000
```

### Health Check
```python
# Verify service is running
async with httpx.AsyncClient() as client:
    health = await client.get("http://localhost:8000/health")
    print(health.json())  # {"status": "healthy", "service": "OCR API"}
```

## Performance & Limits

- **Processing Time**: 15-60 seconds for multi-document analysis
- **File Limits**: Up to 10 files, 50MB each (PDFs), 25MB each (CSVs)
- **Rate Limits**: 10 requests/minute for projection analysis
- **Timeout**: 5-minute timeout for complex document processing

---

**Designed for FastAPI developers who need structured financial projection data from documents.**

*Service Version: 2.1.0 | Compatible with FastAPI 0.68+*
