# Stage 1: Data Extraction & Standardization

## Overview

Stage 1 is the critical first step in the financial projection engine. Its sole purpose is to ingest raw financial documents (PDFs and CSVs) and transform them into a perfectly structured and standardized dataset. This creates the essential foundation for the advanced financial analysis that follows.

## What Stage 1 Does

### 1. Document Processing
- **Accepts Multiple Formats**: PDFs (up to 50MB) and CSVs (up to 25MB).
- **Extracts All Financial Data**: Captures every line item from Profit & Loss and Balance Sheet statements.
- **Unified AI Model**: Uses the powerful `gemini-2.5-pro` model to ensure the highest accuracy in data extraction.

### 2. Data Standardization
- **The 25 Standard Fields**: This is the core function of Stage 1. It intelligently maps the varied chart of accounts from the source documents into **25 guaranteed standard fields** (10 for P&L, 15 for Balance Sheet). This ensures every analysis starts from a consistent, universal structure.
- **Australian Financial Year Alignment**: Converts all dates to July-June cycles (e.g., FY2025 = July 2024 to June 2025).
- **Granularity Preservation**: While mapping to standards, it preserves all original, granular line items in a `raw_extraction` block. This detail is crucial for the cash flow reconstruction in Stage 2.

### 3. Quality Assessment
- **Standard Field Coverage**: Measures the percentage of the 25 standard fields that were successfully found and mapped.
- **Completeness Score**: Assesses the overall quality and completeness of the extracted data.
- **Anomaly Detection**: Identifies unusual values or inconsistencies that could impact the analysis.

## Key Requirements

### Mandatory Documents
- **Profit & Loss Statement**: Required for any meaningful analysis.
- **Balance Sheet**: **Crucially required** for the cash flow reconstruction in Stage 2. The system cannot proceed without it.

### Quality Standards
- **High Standard Field Coverage**: A high percentage is needed for the next stages to function correctly.
- **At least 12-24 months of data** for accurate pattern detection and cash flow analysis.
- **Clear, readable financial statements** with standard formatting.

## What You Get from Stage 1

### A Standardized Financial Dataset
The output is a highly structured JSON object, not just raw data.

```json
{
  "document_type": "Profit and Loss",
  "source_filename": "financials_2023.pdf",
  "data_quality_assessment": {
    "completeness_score": 0.98,
    "standard_field_coverage": {
      "total_standard_fields_found": "23 out of 25",
      "coverage_percentage": "92.0%"
    }
  },
  "standard_field_mapping": {
    "profit_and_loss_standards": {
      "revenue": {
        "mapped_from": ["Sales Revenue", "Other Income"],
        "time_series": [{"period": "2023-01", "value": 150000}]
      },
      // ... other 9 P&L standard fields
    },
    "balance_sheet_standards": {
      "assets": {
        "total_cash_equivalents": {
          "mapped_from": ["Cash at Bank", "Petty Cash"],
          "time_series": [{"period": "2023-01", "value": 50000}]
        },
        // ... other 14 Balance Sheet standard fields
      }
    }
  },
  "raw_extraction": {
    "all_line_items": {
      "pl_accounts": ["Sales Revenue", "Other Income", "Rent Expense", ...],
      "bs_accounts": ["Cash at Bank", "Accounts Receivable", ...]
    }
  }
}
```

## Why Stage 1 Matters

### The Foundation for Everything
- **Enables Cash Flow Reconstruction**: Without a standardized Balance Sheet and P&L, the critical analysis in Stage 2 is impossible.
- **Ensures Consistency**: Every analysis, regardless of the input files, starts from the same reliable data structure.
- **Guarantees Quality**: The focus on standard field coverage ensures the data is complete enough for a credible forecast.

## Next Steps

The standardized P&L and Balance Sheet data from Stage 1 is the direct and essential input for Stage 2. This allows the next stage to:
- **Reconstruct a historical Cash Flow statement** using the indirect method.
- **Calculate actual, data-driven working capital drivers** like DSO and DPO.
- **Create a complete 3-statement view** of the company's historical performance.

**Key Takeaway**: Stage 1 is a powerful data processing and standardization engine. It transforms messy, inconsistent financial documents into a clean, reliable, and universally structured dataset, making advanced analysis like historical cash flow reconstruction possible.