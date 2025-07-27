# Stage 4: Projection Generation Engine

## Overview

Stage 4 is the final execution step where the strategic blueprint from Stage 3 is transformed into concrete financial projections. This engine is precisely instructed to generate forecasts for the key metrics required for immediate business planning across multiple time horizons.

## The Goal: Targeted & Comprehensive Projections

While the underlying architecture is built for full 3-way forecasting, the current primary objective of Stage 4 is to deliver a clear, actionable view of the company's core profitability drivers.

### Key Projection Outputs
The engine is specifically tasked with generating projections for four critical P&L metrics:
1.  **Revenue**
2.  **Expenses**
3.  **Gross Profit**
4.  **Net Profit**

### Time Horizons & Granularity
The system generates these four metrics across a full range of strategic planning horizons:

```json
{
  "1_year_ahead": {
    "granularity": "monthly",
    "data_points": 12,
    "confidence": "high",
    "use_case": "Operational planning and cash flow management"
  },
  "3_years_ahead": {
    "granularity": "quarterly", 
    "data_points": 12,
    "confidence": "medium",
    "use_case": "Strategic planning and business development"
  },
  "5_years_ahead": {
    "granularity": "yearly",
    "data_points": 5,
    "confidence": "medium",
    "use_case": "Long-term strategic planning"
  },
  "10_years_ahead": {
    "granularity": "yearly",
    "data_points": 10,
    "confidence": "low",
    "use_case": "Investment planning and major decisions"
  },
  "15_years_ahead": {
    "granularity": "yearly",
    "data_points": 15,
    "confidence": "very_low",
    "use_case": "Long-term strategic visioning"
  }
}
```

## How It Works: Executing the Strategy

The Projection Engine takes the `stage4_handover_package` from Stage 3, which contains everything it needs:
-   The selected forecasting methodology (e.g., Prophet, SARIMA).
-   The specific, data-driven assumptions (e.g., cash-constrained growth rate, target DSO).
-   The complete historical dataset for context.

It then applies the methodology and assumptions to the historical data to generate the future-looking projections.

### Sample Output Structure

The final output is a clean, well-structured JSON object containing the requested data for all time horizons.

```json
{
  "projection_methodology": {
    "primary_method_applied": "Prophet",
    "method_adjustments": ["Applied cash-constrained growth assumptions"]
  },
  "base_case_projections": {
    "1_year_ahead": {
      "granularity": "monthly",
      "revenue": [
        {"period": "2026-01", "value": 125000, "confidence": "high"}
      ],
      "expenses": [
        {"period": "2026-01", "value": 75000, "confidence": "high"}
      ],
      "gross_profit": [
        {"period": "2026-01", "value": 50000, "confidence": "high"}
      ],
      "net_profit": [
        {"period": "2026-01", "value": 35000, "confidence": "high"}
      ]
    },
    "5_years_ahead": {
      "granularity": "yearly",
      "revenue": [
        {"period": "2026", "value": 1500000, "confidence": "medium"}
      ],
      "expenses": [
        {"period": "2026", "value": 900000, "confidence": "medium"}
      ],
      "gross_profit": [
        {"period": "2026", "value": 600000, "confidence": "medium"}
      ],
      "net_profit": [
        {"period": "2026", "value": 420000, "confidence": "medium"}
      ]
    }
    // ... projections for 3, 10, and 15 years
  }
}
```

## Key Features of the Projections

### 1. Data-Driven Foundation
- Every projection is a direct result of the deep analysis performed in Stages 2 and 3.
- Assumptions are not generic; they are derived from the company's own historical performance, including its cash flow dynamics.

### 2. Scenario Planning
The engine generates multiple scenarios to account for uncertainty:
- **Base Case**: The most likely outcome based on the analysis.
- **Optimistic**: A best-case scenario, often tied to successful implementation of strategic improvements (e.g., faster cash collection).
- **Conservative**: A cautious scenario that accounts for identified risks.

### 3. Built for the Future: 3-Way Forecasting
- **Current Capability**: Delivers the four most critical P&L metrics for immediate planning.
- **Future Enhancement**: The underlying analysis of P&L, Balance Sheet, and Cash Flow in the preceding stages means the system is already architected to generate full, integrated 3-way forecasts. Adding the final projection layer for the full Cash Flow and Balance Sheet is a natural next step.

## Why This Approach Works

### 1. Focus on Actionable Metrics
- By concentrating on Revenue, Expenses, and Profit, the system provides the most critical data points for immediate strategic, operational, and financial planning.

### 2. Time-Appropriate Granularity
- **Short-term (1 year)**: Monthly detail for budgeting and operational management.
- **Medium-term (3 years)**: Quarterly view for strategic initiatives.
- **Long-term (5-15 years)**: Annual perspective for vision and major investment decisions.

### 3. Confidence-Adjusted Projections
- The system assigns and reports confidence levels for each time horizon, acknowledging that certainty decreases over longer periods. This helps users make appropriately risk-adjusted decisions.

## Final Validation

Before the output is finalized, it undergoes a final check to ensure:
- **Completeness**: All four required metrics are present for all five time horizons.
- **Mathematical Integrity**: Basic checks (e.g., Revenue - Expenses >= Gross Profit) are sound.
- **Consistency**: The projections are consistent with the methodology and assumptions selected in Stage 3.

**Key Takeaway**: Stage 4 is the disciplined execution engine of the system. It takes the rich, data-driven strategy from the preceding stages and generates a clear, comprehensive, and multi-horizon forecast of the key profitability metrics a business needs for effective planning. 