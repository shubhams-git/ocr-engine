# API Reference & Usage Guide

## Overview

This guide shows you how to use the Financial Projection System API to generate comprehensive financial forecasts from your business documents.

## How to Use the System

### 1. Basic Usage

**Endpoint**: `POST /multi-pdf/analyze`

**What you need:**
- Financial documents (PDF or CSV).
- At least one **Profit & Loss statement** and one **Balance Sheet** are required for the analysis to work correctly.
- Documents should be clear, readable, and cover at least 12-24 months of financial history for best results.

**Simple example:**
```bash
curl -X POST "http://localhost:8000/multi-pdf/analyze" \
  -F "files=@fy2022_pl_bs.pdf" \
  -F "files=@fy2023_pl_bs.pdf"
```

### 2. File Requirements

**Supported formats:**
- **PDFs**: Up to 50MB (financial statements, reports).
- **CSVs**: Up to 25MB (budget data, financial tables).

**What works best:**
- Clear, readable financial statements with both P&L and Balance Sheet data.
- Standard accounting formats.
- Multiple periods of data (24+ months preferred for accurate seasonal analysis).

## What You Get Back

### 1. Complete Financial Analysis
The system returns a comprehensive JSON object containing the full 4-stage analysis, including:
- **Stage 1**: Standardized P&L and Balance Sheet data.
- **Stage 2**: Reconstructed historical Cash Flow statements and calculated working capital drivers (DSO, DPO).
- **Stage 3**: Deep business analysis and the selected forecasting strategy.
- **Stage 4**: Final projections for **Revenue, Expenses, Gross Profit, and Net Profit** across all time horizons.

### 2. Sample Response Structure
The response is a rich object containing the results of each stage. The final projections are found in the `projections` key.

```json
{
  "success": true,
  "extracted_data": [
    // ... results from Stage 1
  ],
  "normalized_data": {
    // ... results from Stage 2 (Cash Flow) & Stage 3 (Analysis)
    "cash_flow_integration_analysis": {
      "working_capital_analysis": {
        "calculated_dso": { "historical_average": "52 days" },
        "calculated_dpo": { "historical_average": "38 days" }
      }
    },
    "methodology_optimization": {
      "optimal_methodology_selection": { "primary_method": "Prophet" }
    }
  },
  "projections": {
    // ... results from Stage 4
    "base_case_projections": {
      "1_year_ahead": {
        "granularity": "monthly",
        "revenue": [{"period": "2026-01", "value": 125000, "confidence": "high"}],
        "expenses": [{"period": "2026-01", "value": 75000, "confidence": "high"}],
        "gross_profit": [{"period": "2026-01", "value": 50000, "confidence": "high"}],
        "net_profit": [{"period": "2026-01", "value": 35000, "confidence": "high"}]
      },
      "5_years_ahead": {
        "granularity": "yearly",
        "revenue": [{"period": "2026", "value": 1500000, "confidence": "medium"}]
        // ... other metrics
      }
      // ... other time horizons
    }
  },
  "explanation": "Enhanced 4-stage financial analysis completed...",
  "data_analysis_summary": {
    "architecture_type": "unified_pro_model_optimized_rate_limiting",
    "stage_timings": {
        "stage1_extraction_normalization": 15.2,
        "stage2_cash_flow_generation": 10.5,
        "stage3_comprehensive_analysis": 12.1,
        "stage4_projection_engine": 8.5
    }
  }
}
```

## Key Features

### 1. Data-Driven Projections
- **Actuals-Based**: Forecasts are based on the company's own historical cash flow and working capital performance, not generic assumptions.
- **Australian Business Focus**: Aligns with July-June financial year cycles and local business patterns.

### 2. Intelligent & Resilient Analysis
- **Unified Pro Model**: Uses `gemini-2.5-pro` for all stages, ensuring deep analysis throughout.
- **Smart Rate Limiting**: Prevents API errors and ensures stability.
- **Graceful Fallbacks**: `SuperRobustJSONParser` and `IntelligentMethodologySelector` handle potential API issues to deliver a result.

### 3. Comprehensive Outputs
- **Multi-horizon forecasts**: From 1 to 15 years with appropriate granularity.
- **Detailed breakdowns**: Revenue, expenses, and profits.
- **Deep business insights**: Includes calculated DSO/DPO and cash-constrained growth analysis.
- **Scenario planning**: Provides base, optimistic, and conservative scenarios.

## Understanding Your Results

### 1. Working Capital Drivers
Check the `normalized_data.cash_flow_integration_analysis.working_capital_analysis` section to see the **actual, calculated** DSO, DPO, and Cash Conversion Cycle for the business. This is a key indicator of operational efficiency.

### 2. Selected Methodology
The `normalized_data.methodology_optimization.optimal_methodology_selection` section shows which forecasting method the AI determined was best suited for the company's specific financial patterns.

### 3. Confidence Levels
Each data point in the final projection has a confidence level (`high`, `medium`, `low`, `very_low`). Confidence naturally decreases over longer time horizons.

## Error Handling

### Common Issues and Solutions

**`400 Bad Request: "No Profit & Loss statement detected"`**
- **Cause**: The AI did not identify a P&L statement in the uploaded documents.
- **Solution**: Ensure at least one clear, readable P&L document is included.

**`400 Bad Request: "No Balance Sheet statement detected"`**
- **Cause**: The AI did not identify a Balance Sheet, which is required for cash flow reconstruction.
- **Solution**: Ensure a clear Balance Sheet document covering the same periods as the P&L is included.

**`500 Internal Server Error`**
- **Cause**: A processing error occurred in one of the four stages. This could be due to highly unusual financial data or an API issue.
- **Solution**: Check the logs for details. If the problem persists, review the source documents for clarity and completeness.

**`504 Gateway Timeout`**
- **Cause**: The entire 4-stage process took longer than the server's overall timeout (currently 20 minutes).
- **Solution**: Try again with fewer or less complex documents.

## System Health

### Health Check
```bash
GET /health
```
Returns a simple `{"status": "healthy"}` if the service is running.

**Key Takeaway**: The API is designed to be simple to use while providing an incredibly deep and sophisticated financial analysis. Providing complete, high-quality P&L and Balance Sheet documents is the key to unlocking the full power of the 4-stage engine.
 