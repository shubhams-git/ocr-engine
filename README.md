# OCR Engine API - Financial Projections Service

A FastAPI-based financial analysis service that extracts projection data from financial documents (PDFs, CSVs) and provides structured forecasts for revenue, gross profit, expenses, and net profit across multiple time horizons.

## Project Overview

This service transforms raw financial documents into actionable projection data that can be used for:
- Financial dashboards and visualizations
- Investment analysis and decision making
- Business planning and forecasting
- Risk assessment and scenario modeling

## Codebase Structure

```
ocr-engine/
├── backend/                 # FastAPI backend service
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # API key management and CORS settings
│   ├── models.py           # Pydantic response models
│   ├── prompts.py          # AI prompts for financial analysis
│   ├── middleware.py       # Error handling middleware
│   ├── routers/            # API endpoint definitions
│   │   ├── multi_pdf.py    # Multi-document analysis endpoint
│   │   ├── ocr.py          # Single document OCR endpoint
│   │   ├── health.py       # Health check endpoints
│   │   └── admin.py        # API key management endpoints
│   └── services/           # Business logic
│       ├── multi_pdf_service.py  # Core projection analysis
│       └── ocr_service.py        # Document processing
└── frontend/               # React frontend (optional)
```

## Core Functionality

### 1. Document Processing
- **Input**: PDF financial statements, CSV data files, or mixed document types
- **Processing**: Google Gemini AI extracts and normalizes financial data
- **Output**: Structured JSON with historical data and projections

### 2. Projection Generation
The service automatically generates projections for:
- **1 Year Ahead**: Monthly granularity (12 data points)
- **3 Years Ahead**: Quarterly granularity (12 data points)  
- **5 Years Ahead**: Yearly granularity (12 data points)
- **10 Years Ahead**: Yearly granularity (12 data points)
- **15 Years Ahead**: Yearly granularity (12 data points)

### 3. Financial Metrics
Each projection period contains four mandatory financial metrics:
- **Revenue**: Total income projections
- **Gross Profit**: Revenue minus direct costs
- **Expenses**: Operating and overhead costs
- **Net Profit**: Final profit after all expenses

## API Usage for FastAPI Clients

### Basic Request Structure

```python
import requests
from typing import List

def analyze_financial_documents(file_paths: List[str], api_url: str = "http://localhost:8000"):
    """
    Send financial documents for analysis and get projection data
    """
    # Prepare files for upload
    files = []
    for file_path in file_paths:
        files.append(('files', open(file_path, 'rb')))
    
    # API request parameters
    data = {
        'model': 'gemini-2.5-pro'  # Recommended for accuracy
    }
    
    # Make API call
    response = requests.post(
        f"{api_url}/multi-pdf/analyze",
        files=files,
        data=data,
        timeout=300  # 5 minutes timeout
    )
    
    # Clean up file handles
    for _, file_handle in files:
        file_handle.close()
    
    return response.json()
```

### Response Data Structure

The API returns a comprehensive response with projection data:

```python
{
    "success": True,
    "projections": {
        "specific_projections": {
            "1_year_ahead": {
                "period": "FY2026",
                "granularity": "monthly",
                "revenue": [
                    {"period": "Month 1", "value": 175000, "confidence": "high"},
                    {"period": "Month 2", "value": 180000, "confidence": "high"},
                    # ... 12 months total
                ],
                "gross_profit": [
                    {"period": "Month 1", "value": 70000, "confidence": "high"},
                    {"period": "Month 2", "value": 72000, "confidence": "high"},
                    # ... 12 months total
                ],
                "expenses": [
                    {"period": "Month 1", "value": 135000, "confidence": "high"},
                    {"period": "Month 2", "value": 138000, "confidence": "high"},
                    # ... 12 months total
                ],
                "net_profit": [
                    {"period": "Month 1", "value": 40000, "confidence": "high"},
                    {"period": "Month 2", "value": 42000, "confidence": "high"},
                    # ... 12 months total
                ]
            },
            "3_years_ahead": {
                "period": "FY2028",
                "granularity": "quarterly",
                "revenue": [...],  # 12 quarters
                "gross_profit": [...],
                "expenses": [...],
                "net_profit": [...]
            },
            "5_years_ahead": {
                "period": "FY2030", 
                "granularity": "yearly",
                "revenue": [...],  # 12 years
                "gross_profit": [...],
                "expenses": [...],
                "net_profit": [...]
            },
            "10_years_ahead": {...},
            "15_years_ahead": {...}
        }
    }
}
```

## Data Extraction and Processing

### 1. Extract Projection Totals

```python
def extract_projection_totals(api_response):
    """
    Extract total values for each time period and metric
    """
    if not api_response.get('success'):
        return None
    
    projections = api_response.get('projections', {}).get('specific_projections', {})
    
    results = {}
    for timeframe, data in projections.items():
        results[timeframe] = {
            'period': data.get('period'),
            'granularity': data.get('granularity'),
            'revenue_total': sum(item['value'] for item in data.get('revenue', [])),
            'gross_profit_total': sum(item['value'] for item in data.get('gross_profit', [])),
            'expenses_total': sum(item['value'] for item in data.get('expenses', [])),
            'net_profit_total': sum(item['value'] for item in data.get('net_profit', [])),
            'confidence': data.get('revenue', [{}])[0].get('confidence', 'unknown')
        }
    
    return results

# Usage
projection_totals = extract_projection_totals(api_response)
print(f"1 Year Revenue: ${projection_totals['1_year_ahead']['revenue_total']:,}")
print(f"3 Year Net Profit: ${projection_totals['3_years_ahead']['net_profit_total']:,}")
```

### 2. Extract Time Series Data

```python
def extract_time_series_data(api_response, metric='revenue'):
    """
    Extract time series data for a specific metric across all timeframes
    """
    if not api_response.get('success'):
        return None
    
    projections = api_response.get('projections', {}).get('specific_projections', {})
    
    time_series = {}
    for timeframe, data in projections.items():
        time_series[timeframe] = {
            'periods': [item['period'] for item in data.get(metric, [])],
            'values': [item['value'] for item in data.get(metric, [])],
            'confidence': [item['confidence'] for item in data.get(metric, [])]
        }
    
    return time_series

# Usage
revenue_series = extract_time_series_data(api_response, 'revenue')
expenses_series = extract_time_series_data(api_response, 'expenses')
```

### 3. Get Confidence Levels

```python
def get_confidence_summary(api_response):
    """
    Get confidence levels for each projection timeframe
    """
    accuracy = api_response.get('accuracy_considerations', {})
    confidence_levels = accuracy.get('projection_confidence', {})
    
    return {
        '1_year': confidence_levels.get('1_year_ahead', 'unknown'),
        '3_years': confidence_levels.get('3_years_ahead', 'unknown'),
        '5_years': confidence_levels.get('5_years_ahead', 'unknown'),
        '10_years': confidence_levels.get('10_years_ahead', 'unknown'),
        '15_years': confidence_levels.get('15_years_ahead', 'unknown')
    }
```

## Visualization and Dashboard Integration

### 1. Pie Chart Data Preparation

```python
def prepare_pie_chart_data(projection_totals, timeframe='1_year_ahead'):
    """
    Prepare data for pie chart showing profit breakdown
    """
    data = projection_totals[timeframe]
    
    pie_data = [
        {'label': 'Gross Profit', 'value': data['gross_profit_total']},
        {'label': 'Expenses', 'value': data['expenses_total']},
        {'label': 'Net Profit', 'value': data['net_profit_total']}
    ]
    
    return pie_data
```

### 2. Line Chart Data Preparation

```python
def prepare_line_chart_data(time_series_data, metric='revenue'):
    """
    Prepare data for line chart showing trends over time
    """
    chart_data = []
    
    for timeframe, data in time_series_data.items():
        for i, (period, value) in enumerate(zip(data['periods'], data['values'])):
            chart_data.append({
                'timeframe': timeframe,
                'period': period,
                'value': value,
                'confidence': data['confidence'][i]
            })
    
    return chart_data
```

### 3. Bar Chart Data Preparation

```python
def prepare_bar_chart_data(projection_totals):
    """
    Prepare data for bar chart comparing metrics across timeframes
    """
    timeframes = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
    metrics = ['revenue_total', 'gross_profit_total', 'expenses_total', 'net_profit_total']
    
    bar_data = []
    for metric in metrics:
        series = {
            'metric': metric.replace('_total', '').replace('_', ' ').title(),
            'data': []
        }
        for timeframe in timeframes:
            series['data'].append({
                'timeframe': timeframe.replace('_ahead', '').replace('_', ' ').title(),
                'value': projection_totals[timeframe][metric]
            })
        bar_data.append(series)
    
    return bar_data
```

## Complete Integration Example

```python
import requests
import json
from typing import List

class FinancialProjectionsClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_documents(self, file_paths: List[str]):
        """Analyze financial documents and return projections"""
        files = []
        for file_path in file_paths:
            files.append(('files', open(file_path, 'rb')))
        
        response = requests.post(
            f"{self.base_url}/multi-pdf/analyze",
            files=files,
            data={'model': 'gemini-2.5-pro'},
            timeout=300
        )
        
        # Clean up
        for _, file_handle in files:
            file_handle.close()
        
        return response.json()
    
    def get_dashboard_data(self, api_response):
        """Extract all data needed for dashboard visualizations"""
        if not api_response.get('success'):
            return None
        
        # Extract projection totals
        projection_totals = extract_projection_totals(api_response)
        
        # Extract time series data
        revenue_series = extract_time_series_data(api_response, 'revenue')
        expenses_series = extract_time_series_data(api_response, 'expenses')
        
        # Get confidence levels
        confidence_levels = get_confidence_summary(api_response)
        
        # Prepare visualization data
        pie_data = prepare_pie_chart_data(projection_totals, '1_year_ahead')
        line_data = prepare_line_chart_data(revenue_series, 'revenue')
        bar_data = prepare_bar_chart_data(projection_totals)
        
        return {
            'projection_totals': projection_totals,
            'time_series': {
                'revenue': revenue_series,
                'expenses': expenses_series
            },
            'confidence_levels': confidence_levels,
            'visualization_data': {
                'pie_chart': pie_data,
                'line_chart': line_data,
                'bar_chart': bar_data
            }
        }

# Usage Example
client = FinancialProjectionsClient()

# Analyze documents
result = client.analyze_documents([
    'financial_report_2023.pdf',
    'quarterly_data.csv'
])

# Get dashboard data
dashboard_data = client.get_dashboard_data(result)

# Use data for visualizations
print(f"1 Year Revenue: ${dashboard_data['projection_totals']['1_year_ahead']['revenue_total']:,}")
print(f"Confidence Level: {dashboard_data['confidence_levels']['1_year']}")
```

## Key Data Points for Visualization

### 1. Revenue Analysis
- **Total Revenue**: Sum of all revenue projections for each timeframe
- **Growth Rate**: Month-over-month or quarter-over-quarter growth
- **Trend Direction**: Increasing, decreasing, or stable patterns

### 2. Profitability Analysis  
- **Gross Profit Margin**: Gross profit / Revenue ratio
- **Net Profit Margin**: Net profit / Revenue ratio
- **Expense Ratio**: Expenses / Revenue ratio

### 3. Risk Assessment
- **Confidence Levels**: High, medium, low, very_low for each timeframe
- **Volatility**: Standard deviation of projections
- **Scenario Analysis**: Optimistic vs conservative projections

## Setup Instructions

### 1. Environment Setup
```bash
# Install dependencies
pip install fastapi uvicorn google-genai python-multipart requests

# Set API key
export GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start Service
```bash
cd backend
python main.py
```

Service runs on `http://localhost:8000`

### 3. Test Connection
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())  # Should return {"status": "healthy"}
```

## API Endpoints Summary

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/multi-pdf/analyze` | POST | Main projection analysis | 15-60 seconds |
| `/ocr` | POST | Single document extraction | 1-3 seconds |
| `/health` | GET | Service status | <100ms |
| `/models` | GET | Available AI models | <100ms |

## File Requirements

- **PDFs**: Financial statements, reports (max 50MB each)
- **CSV**: Financial data in tabular format (max 25MB each)
- **Multiple Files**: Up to 10 files per request
- **Supported Formats**: PDF, CSV, PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

This service provides the foundation for building comprehensive financial analysis dashboards and visualization tools by delivering structured projection data across multiple time horizons and financial metrics.
