# Validation & Quality Assurance

## Overview

Our validation framework is a multi-stage process designed to ensure the integrity, consistency, and business logic of the financial analysis from start to finish. Each of the four stages in our architecture has a specific quality assurance role.

## Why Validation Matters

- **Ensuring Accuracy**: Verifies that the analysis is mathematically sound and financially logical at each step.
- **Building Confidence**: Provides clear quality indicators, allowing users to trust the final output.
- **Data-Driven Integrity**: Ensures that the final projections are directly traceable to the validated historical data.

## Our 4-Stage Validation System

### Stage 1: Data Standardization Validation
**Location**: `OCRService`

**What it checks:**
- **File Integrity**: Validates file format (PDF, CSV) and size.
- **Standard Field Coverage**: This is the most critical check. It measures the percentage of the **25 guaranteed standard fields** that were successfully mapped from the source documents. A high score is essential to proceed.
- **Data Quality**: The AI assesses the completeness of the extracted data and flags anomalies (e.g., negative revenue, major inconsistencies).

**Output**: A `data_quality_assessment` object for each file, with a strong focus on the standard field coverage score.

### Stage 2: Cash Flow Reconciliation
**Location**: `BusinessAnalysisService`

**What it checks:**
- **The Fundamental Law of Cash Flow**: This is a critical mathematical reconciliation. The service ensures that the reconstructed cash flow statement is correct by verifying:
  - **Total Cash Flow (Operating + Investing + Financing) = Change in Cash on the Balance Sheet**
- **Variance Analysis**: It calculates the variance for each historical period. Any period with a variance greater than a small threshold (e.g., $1,000) is flagged for review.

**Output**: A `cash_flow_quality_assessment` that shows the validation status (Pass/Fail) for each historical period, ensuring the 3-statement historical model is mathematically sound.

### Stage 3: Business Logic & Strategy Validation
**Location**: `AnalysisService`

**What it checks:**
- **Holistic Reasonableness**: The AI acts as a senior financial analyst, reviewing the complete 3-statement historical data for logical consistency.
- **Quality of Earnings**: It validates the relationship between reported profits (P&L) and actual cash generation (Cash Flow).
- **Assumption Validation**: It ensures that the strategic assumptions it develops (e.g., target DSO, sustainable growth rate) are directly supported by the validated historical data from Stage 2.

**Output**: A validated forecasting strategy where every assumption is data-driven and defensible.

### Stage 4: Projection Completeness Check
**Location**: `ProjectionService` & `MultiPDFService`

**What it checks:**
- **Completeness**: This final check verifies that the AI has successfully generated all required data points.
- **Mandatory Metrics**: It ensures projections for **Revenue, Expenses, Gross Profit, and Net Profit** are present.
- **All Time Horizons**: It confirms that data for **1, 3, 5, 10, and 15-year** horizons has been generated.

**Output**: A final, complete set of projections that meets the specific output requirements of the system.

---

### A Note on Post-Projection Validation

To improve system stability and prevent timeouts caused by additional complex API calls, **local post-projection validation (which involved re-balancing a projected balance sheet) has been disabled.** The current validation focus is on ensuring the integrity of the historical data and the logic of the forecasting strategy, which provides a strong foundation for the final AI-generated projections.

## Quality Scoring

The overall quality of the final output is a reflection of the success of the validation at each of the four stages. A high-quality result depends on:
- **High Standard Field Coverage** in Stage 1.
- **Successful Cash Flow Reconciliation** in Stage 2.
- **Logical and Data-Driven Strategy** in Stage 3.
- **Complete Generation of Projections** in Stage 4.

**Key Takeaway**: Our validation framework is integrated directly into the 4-stage processing pipeline. It builds a chain of trust, starting with standardized source data, reconciling it into a complete historical view, building a logical strategy upon it, and finally ensuring the final projections are complete. 