# API Reference & Usage Guide

## Overview

This guide shows you how to use the OCR-based Financial Projection System to generate comprehensive financial forecasts from your business documents.

## How to Use the System

### 1. Basic Usage

**Endpoint**: `POST /multi-pdf`

**What you need:**
- Financial documents (PDF, CSV, or images)
- At least one Profit & Loss statement
- Documents should be clear and readable

**Simple example:**
```bash
curl -X POST "http://localhost:8000/multi-pdf" \
  -F "files=@q1-financial-statement.pdf" \
  -F "files=@q2-financial-statement.pdf" \
  -F "files=@budget-data.csv"
```

### 2. File Requirements

**Supported formats:**
- **PDFs**: Up to 50MB (financial statements, reports)
- **CSVs**: Up to 25MB (budget data, financial tables)
- **Images**: Up to 10MB (scanned documents)

**What works best:**
- Clear, readable financial statements
- Standard accounting formats
- Multiple periods of data (12+ months preferred)
- Consistent number formatting

## What You Get Back

### 1. Complete Financial Analysis
The system returns comprehensive projections including:
- **Revenue forecasts** for 1, 3, 5, 10, and 15 years
- **Expense projections** with detailed breakdowns
- **Gross profit** and **net profit** across all time horizons
- **Business intelligence** about your industry and growth patterns

### 2. Time Horizon Breakdown
```json
{
  "1_year_ahead": {
    "granularity": "monthly",
    "data_points": 12,
    "confidence": "high"
  },
  "3_years_ahead": {
    "granularity": "quarterly",
    "data_points": 12,
    "confidence": "medium"
  },
  "5_years_ahead": {
    "granularity": "yearly",
    "data_points": 5,
    "confidence": "medium"
  },
  "10_years_ahead": {
    "granularity": "yearly",
    "data_points": 10,
    "confidence": "low"
  },
  "15_years_ahead": {
    "granularity": "yearly",
    "data_points": 15,
    "confidence": "very_low"
  }
}
```

### 3. Sample Response Structure
```json
{
  "success": true,
  "data_quality_score": 0.92,
  "business_context": {
    "industry_classification": "Professional Services",
    "business_stage": "growth",
    "competitive_position": "established"
  },
  "projections": {
    "1_year_ahead": {
      "revenue": [
        {"month": "2024-07", "value": 150000},
        {"month": "2024-08", "value": 157500}
      ],
      "gross_profit": [
        {"month": "2024-07", "value": 52500},
        {"month": "2024-08", "value": 55125}
      ],
      "net_profit": [
        {"month": "2024-07", "value": 12250},
        {"month": "2024-08", "value": 13563}
      ]
    },
    "5_years_ahead": {
      "revenue": [
        {"year": "FY2025", "value": 1950000},
        {"year": "FY2026", "value": 2047500}
      ],
      "gross_profit": [
        {"year": "FY2025", "value": 682500},
        {"year": "FY2026", "value": 716625}
      ],
      "net_profit": [
        {"year": "FY2025", "value": 175000},
        {"year": "FY2026", "value": 193750}
      ]
    }
  },
  "scenarios": {
    "base_case": "Most likely outcome",
    "optimistic": "25% uplift scenario",
    "conservative": "25% reduction scenario"
  }
}
```

## Key Features

### 1. Australian Business Focus
- **Financial Year Alignment**: July-June cycles
- **Local Seasonality**: Understands Australian business patterns
- **Tax and Dividend Policy**: 25% tax rate, 40% dividend payout

### 2. Intelligent Analysis
- **Industry Classification**: Automatically identifies your business type
- **Growth Pattern Recognition**: Identifies trends and seasonality
- **Methodology Selection**: Chooses the best forecasting approach

### 3. Quality Assurance
- **Data Quality Score**: 0-100% quality rating
- **Confidence Levels**: Different confidence for different time horizons
- **Validation Checks**: Mathematical and business logic validation

### 4. Comprehensive Outputs
- **Multi-horizon forecasts**: From 1 to 15 years
- **Detailed breakdowns**: Revenue, expenses, profits
- **Business insights**: Industry analysis and growth drivers
- **Scenario planning**: Multiple outcome scenarios

## Understanding Your Results

### 1. Quality Score Interpretation
- **90-100%**: Excellent quality, high confidence
- **80-89%**: Good quality, minor issues
- **70-79%**: Acceptable quality, some concerns
- **Below 70%**: Poor quality, needs better data

### 2. Confidence Levels
- **1 Year**: High confidence based on recent trends
- **3 Years**: Medium confidence, some uncertainty
- **5 Years**: Medium confidence, business cycle effects
- **10-15 Years**: Low confidence, many variables

### 3. Business Context
The system identifies:
- **Industry type**: Professional services, manufacturing, technology, etc.
- **Business stage**: Startup, growth, mature, decline
- **Competitive position**: Market leader, established, emerging
- **Growth patterns**: Seasonal effects, trends, volatility

## Common Use Cases

### 1. Business Planning
- **Operational planning**: Use 1-year monthly projections
- **Strategic planning**: Use 3-5 year projections
- **Investment decisions**: Use 5-15 year projections

### 2. Stakeholder Communication
- **Investor presentations**: Professional financial projections
- **Loan applications**: Comprehensive financial forecasts
- **Board reporting**: Quality-assured business projections

### 3. Performance Monitoring
- **Budget vs. actual**: Compare projections to real results
- **Variance analysis**: Understand projection accuracy
- **Model refinement**: Improve future projections

## Error Handling

### Common Issues and Solutions

**File too large:**
- Solution: Reduce file size or split into multiple files
- PDF limit: 50MB, CSV limit: 25MB, Image limit: 10MB

**No P&L statement detected:**
- Solution: Include at least one clear profit & loss statement
- Ensure financial data is clearly visible and readable

**Poor quality score:**
- Solution: Provide more complete financial data
- Include 12+ months of historical data for better analysis

**Processing timeout:**
- Solution: Reduce number of files or file complexity
- System timeout: 10 minutes maximum processing time

## Best Practices

### 1. Document Preparation
- **Use clear, readable documents**
- **Include multiple time periods** (12+ months)
- **Provide complete financial statements**
- **Use consistent number formatting**

### 2. File Organization
- **Name files descriptively** (e.g., "Q1-2024-PL.pdf")
- **Include document dates** for proper sequencing
- **Group related documents** together

### 3. Data Quality
- **Ensure completeness**: Include all relevant financial metrics
- **Check accuracy**: Verify numbers before uploading
- **Maintain consistency**: Use same accounting methods across periods

## Advanced Features

### 1. Scenario Analysis
The system automatically generates:
- **Base case**: Most likely outcome
- **Optimistic scenario**: 25% uplift in key metrics
- **Conservative scenario**: 25% reduction in key metrics

### 2. Transparent Calculations
Every projection includes:
- **Calculation explanations**: How each number was derived
- **Source traceability**: Track back to original data
- **Assumption documentation**: Clear reasoning for projections

### 3. Australian Business Intelligence
- **Industry benchmarking**: Compare to industry standards
- **Seasonal adjustment**: Account for Australian business cycles
- **Economic context**: Consider local market conditions

## System Health

### Health Check
```bash
GET /health
```

Returns system status and service availability.

### Response Time
- **Typical processing**: 2-5 minutes
- **Maximum timeout**: 10 minutes
- **File processing**: Parallel processing for multiple files

## Integration Tips

### 1. Automated Workflows
- **Batch processing**: Analyze multiple companies
- **Scheduled analysis**: Regular projection updates
- **API integration**: Build projections into your systems

### 2. Data Management
- **Version control**: Track different projection versions
- **Data backup**: Store important analysis results
- **Comparison tracking**: Monitor projection accuracy over time

### 3. Business Intelligence
- **Dashboard creation**: Build executive dashboards
- **Report generation**: Create standardized reports
- **Trend analysis**: Track business performance over time

**Key Takeaway**: The system transforms your financial documents into comprehensive, multi-horizon projections that provide clear insights into your business's future revenue, expenses, gross profit, and net profit across 1, 3, 5, 10, and 15-year timeframes. 