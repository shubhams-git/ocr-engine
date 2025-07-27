# API Reference & Usage Guide

## Overview

This guide shows you how to use the Financial Projection System API to generate comprehensive financial forecasts from your business documents.

## How to Use the System

### 1. Basic Usage

**Endpoint**: `POST /analysis/analyze`

**What you need:**
- Financial documents (PDF or CSV).
- At least one **Profit & Loss statement** and one **Balance Sheet** are required for the analysis to work correctly.
- Documents should be clear, readable, and cover at least 12-24 months of financial history for best results.

**Simple example:**
```bash
curl -X POST "http://localhost:8000/analysis/analyze" \
  -F "files=@fy2022_pl_bs.pdf" \
  -F "files=@fy2023_pl_bs.pdf"
```

### 2. Specifying a Projection Start Date
You can specify a start date for the projections using the `projection_start_date` parameter.

```bash
curl -X POST "http://localhost:8000/analysis/analyze" \
  -F "files=@fy2022_pl_bs.pdf" \
  -F "files=@fy2023_pl_bs.pdf" \
  -F "projection_start_date=2026-01-01"
```

### 3. File Requirements

**Supported formats:**
- **PDFs**: Up to 50MB (financial statements, reports).
- **CSVs**: Up to 25MB (budget data, financial tables).

**What works best:**
- Clear, readable financial statements with both P&L and Balance Sheet data.
- Standard accounting formats.
- Multiple periods of data (24+ months preferred for accurate seasonal analysis).

## What You Get Back

### 1. Complete Financial Analysis
The system returns a comprehensive JSON object containing the full 5-stage analysis, including:
- **Stage 1**: Standardized P&L and Balance Sheet data.
- **Stage 2**: Reconstructed historical Cash Flow statements and calculated working capital drivers (DSO, DPO).
- **Stage 3**: Deep business analysis and the selected forecasting strategy.
- **Stage 3.5**: Strategic enhancement factors with detailed rationale.
- **Stage 4**: Final projections for **Revenue, Expenses, Gross Profit, and Net Profit** across all time horizons, including a "Base Case" and an "Enhanced Case".

### 2. Sample Response Structure
The response is a rich object containing the results of each stage. The final projections are found in the `projections` key.

```json
{
  "success": true,
  "extracted_data": [ ... ],
  "normalized_data": { ... },
  "projections": {
    "base_case_projections": { ... },
    "enhanced_case_projections": { ... },
    "commentary_and_rationale": { ... }
  },
  "explanation": "Enhanced 5-stage financial analysis completed...",
  "data_analysis_summary": { ... }
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
- **Scenario planning**: Provides base, enhanced, optimistic, and conservative scenarios.

## Understanding Your Results

### 1. Working Capital Drivers
Check the `normalized_data.cash_flow_integration_analysis.working_capital_analysis` section to see the **actual, calculated** DSO, DPO, and Cash Conversion Cycle for the business.

### 2. Selected Methodology
The `normalized_data.methodology_optimization.optimal_methodology_selection` section shows which forecasting method the AI determined was best suited for the company's specific financial patterns.

### 3. Commentary and Rationale
The `projections.commentary_and_rationale` section provides a detailed explanation of the differences between the Base and Enhanced cases, as well as the seasonality adjustments made.

## Error Handling

### Common Issues and Solutions

**`400 Bad Request: "No Profit & Loss statement detected"`**
- **Cause**: The AI did not identify a P&L statement in the uploaded documents.
- **Solution**: Ensure at least one clear, readable P&L document is included.

**`400 Bad Request: "No Balance Sheet statement detected"`**
- **Cause**: The AI did not identify a Balance Sheet, which is required for cash flow reconstruction.
- **Solution**: Ensure a clear Balance Sheet document covering the same periods as the P&L is included.

**`500 Internal Server Error`**
- **Cause**: A processing error occurred in one of the five stages.
- **Solution**: Check the logs for details. If the problem persists, review the source documents for clarity and completeness.

**`504 Gateway Timeout`**
- **Cause**: The entire 5-stage process took longer than the server's overall timeout (currently 20 minutes).
- **Solution**: Try again with fewer or less complex documents.

## System Health

### Health Check
```bash
GET /health
```
Returns a simple `{"status": "healthy"}` if the service is running.

**Key Takeaway**: The API is designed to be simple to use while providing an incredibly deep and sophisticated financial analysis. Providing complete, high-quality P&L and Balance Sheet documents is the key to unlocking the full power of the 5-stage engine.