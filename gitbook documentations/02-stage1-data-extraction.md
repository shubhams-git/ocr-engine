# Stage 1: Data Extraction & Normalization

## Overview

Stage 1 is the foundation of our financial projection system. It takes raw financial documents and transforms them into clean, structured data that our AI models can analyze effectively.

## What Stage 1 Does

### 1. Document Processing
- **Accepts Multiple Formats**: PDFs (up to 50MB), CSVs (up to 25MB), Images (up to 10MB)
- **Extracts Financial Data**: Revenue, expenses, profit, assets, liabilities, equity
- **Handles Various Document Types**: P&L statements, balance sheets, cash flow statements, budget reports

### 2. Data Normalization
- **Australian Financial Year Alignment**: Converts all dates to July-June cycles (FY2025 = July 2024 to June 2025)
- **Consistent Time Series**: Creates monthly data points for all financial metrics
- **Currency Standardization**: Defaults to AUD with multi-currency support

### 3. Quality Assessment
- **Completeness Score**: Measures how much of the expected data was found (0-100%)
- **Anomaly Detection**: Identifies unusual values, negative revenues, or inconsistent data
- **Gap Analysis**: Finds missing time periods or incomplete data

## Key Requirements

### Mandatory Documents
- **Profit & Loss Statement**: Required for generating projections
- **Balance Sheet**: Recommended for better accuracy
- **Cash Flow Statement**: Optional but improves working capital analysis

### Quality Standards
- **Minimum 60% completeness** for reliable projections
- **At least 12 months of data** for meaningful analysis
- **Clear, readable financial statements** with standard formatting

## What You Get from Stage 1

### Structured Output
```json
{
  "document_type": "Profit and Loss",
  "data_quality_assessment": {
    "completeness_score": 0.95,
    "period_range": "2024-01 to 2024-12"
  },
  "normalized_time_series": {
    "revenue": [
      {"period": "2024-01", "value": 150000},
      {"period": "2024-02", "value": 165000}
    ],
    "expenses": [
      {"period": "2024-01", "value": 120000},
      {"period": "2024-02", "value": 125000}
    ],
    "net_profit": [
      {"period": "2024-01", "value": 30000},
      {"period": "2024-02", "value": 40000}
    ]
  }
}
```

### Business Context
- **Industry Indicators**: Clues about business type from document content
- **Reporting Frequency**: Monthly, quarterly, or yearly patterns
- **Currency Detection**: Automatically identifies currency used

## Why Stage 1 Matters

### Foundation for Accuracy
- **Clean Data = Better Projections**: High-quality extraction leads to more reliable forecasts
- **Consistent Format**: Standardized data structure enables sophisticated analysis
- **Quality Scoring**: Helps assess confidence in final projections

### Australian Business Focus
- **Local Patterns**: Understands Australian business cycles and reporting standards
- **EOFY Alignment**: Properly handles end-of-financial-year effects
- **Regional Context**: Considers local market conditions and regulations

## Common Challenges We Handle

### Document Variability
- **Different Formats**: PDFs, spreadsheets, scanned images
- **Varying Layouts**: Custom report formats, different accounting software
- **Quality Issues**: Blurry scans, non-standard number formats

### Data Gaps
- **Missing Periods**: Interpolates reasonable values for missing months
- **Incomplete Information**: Flags gaps and adjusts confidence accordingly
- **Inconsistent Reporting**: Normalizes different reporting frequencies

## Next Steps

Stage 1 output flows directly into Stage 2 for business analysis. The structured, quality-assessed data enables our AI to:
- Classify your business type and maturity
- Identify growth patterns and seasonality
- Select the optimal forecasting methodology
- Generate specific, justified assumptions for projections

**Key Takeaway**: Stage 1 transforms messy financial documents into clean, structured data that forms the foundation for accurate multi-year financial projections. 