# Stage 2 & 3: Cash Flow Reconstruction & Deep Analysis

This document covers the analytical core of the projection engine: Stage 2 and Stage 3. These stages work together to transform the standardized data from Stage 1 into a complete, analysis-ready financial history and a robust forecasting strategy.

---

## Stage 2: Historical Cash Flow Reconstruction

### Overview
Stage 2 elevates the analysis from simple data extraction to true financial modeling. Its primary function is to create a **complete 3-statement historical view** of the business by generating a historical Cash Flow statement. This provides a deep understanding of the company's actual operational efficiency and cash generation capabilities.

### What Stage 2 Does

#### 1. Cash Flow Generation
- **Method**: Uses the **indirect method** to reconstruct a historical Cash Flow statement from the standardized P&L and Balance Sheet data provided by Stage 1.
- **Process**: It calculates cash flows from Operating, Investing, and Financing activities.
- **Validation**: Critically, it validates the output by ensuring the calculated **Net Change in Cash** matches the change in the **Cash & Cash Equivalents** account on the Balance Sheet.

#### 2. Data-Driven Working Capital Analysis
- **No More Guesswork**: Instead of using generic industry assumptions (e.g., "assume customers pay in 45 days"), Stage 2 calculates the **actual, historical working capital drivers** from the company's own data.
- **Key Metrics Calculated**:
  - **Days Sales Outstanding (DSO)**: How long it actually takes customers to pay.
  - **Days Payables Outstanding (DPO)**: How long the company actually takes to pay its suppliers.
  - **Cash Conversion Cycle (CCC)**: The actual time it takes to convert investments in inventory and other resources into cash.

### Why Stage 2 is a Game-Changer

- **Foundation of Truth**: It builds the forecast on the rock-solid foundation of the company's complete financial history, not just its profit and loss.
- **Reveals Operational Health**: A company can be profitable on paper but have poor cash flow. This stage exposes the reality of the company's ability to generate and manage cash.
- **Enables Data-Driven Assumptions**: The calculated, actual drivers (DSO, DPO, etc.) become the basis for credible, defensible forecasting assumptions in the next stage.

### What You Get from Stage 2

A comprehensive JSON object containing the complete, 3-statement historical financials.

```json
{
  "cash_flow_generation_results": {
    "method_used": "indirect_method_from_standard_fields",
    "historical_cash_flows": [
      {
        "period": "2023-01",
        "operating_cash_flow": {"value": 25000},
        "investing_cash_flow": {"value": -10000},
        "financing_cash_flow": {"value": 0},
        "cash_flow_summary": {
          "total_cash_flow": {"value": 15000},
          "actual_cash_change": {"value": 15000},
          "validation_status": "PASS"
        }
      }
    ]
  },
  "cash_flow_integration_analysis": {
    "working_capital_analysis": {
      "calculated_dso": {
        "historical_average": "52 days",
        "trend": "stable"
      },
      "calculated_dpo": {
        "historical_average": "38 days",
        "trend": "improving"
      },
      "cash_conversion_cycle": {
        "historical_average": "67 days"
      }
    }
  }
}
```

---

## Stage 3: Deep Analysis & Forecasting Strategy

### Overview
With a complete 3-statement history, Stage 3 acts as an expert financial strategist. It performs a deep analysis of the integrated data to understand the "why" behind the numbers and formulates a robust, data-driven strategy for the projection engine in Stage 4.

### What Stage 3 Does

#### 1. Integrated Financial Analysis
- **Quality of Earnings**: It analyzes the relationship between Net Income and Operating Cash Flow. Are the company's profits backed by real cash?
- **Growth Sustainability**: It assesses whether the company's historical growth was self-funded or reliant on external financing. This determines a realistic, **cash-constrained growth rate** for the future.
- **Capital Efficiency**: It calculates metrics like Return on Invested Capital (ROIC) to understand how effectively the company uses its capital to generate profit and cash.

#### 2. Forecasting Methodology Optimization
- **Holistic Testing**: The AI tests various forecasting methods (e.g., Prophet, SARIMA, Linear Regression) not just on their ability to predict revenue, but on their ability to create a stable and logical **integrated 3-statement forecast**.
- **Best-Fit Selection**: It selects the methodology that is most compatible with the company's unique combination of profitability, seasonality, and cash flow patterns.

#### 3. Strategic Assumption Framework
- **Data-Driven, Not Assumed**: This is the critical output. Stage 3 develops the specific, strategic assumptions that will guide the projection engine.
- **Example Assumptions**:
  - **Revenue Growth**: "Project revenue growth at 8% annually, a rate which historical cash flows can sustainably support without external funding."
  - **Working Capital**: "Model a strategic improvement in DSO from the historical average of 52 days to an optimized target of 45 days over the next 24 months."
  - **Capital Expenditure**: "Assume maintenance CAPEX will remain consistent at 3.2% of revenue, based on historical analysis of cash flow from investing activities."

### What You Get from Stage 3

A definitive "handover package" for the projection engine, containing the complete strategy.

```json
{
  "methodology_optimization": {
    "optimal_methodology_selection": {
      "primary_method": "Prophet",
      "rationale": "Best fit for the business's seasonal revenue and cash flow patterns.",
      "confidence_level": "high"
    }
  },
  "strategic_assumption_framework": {
    "revenue_growth_strategy": {
      "cash_flow_constrained_growth": "8% annually",
      "justification": "Supported by historical operating cash flow generation."
    },
    "working_capital_strategy": {
      "target_dso": "45 days",
      "optimization_timeline": "24 months"
    }
  },
  "stage4_handover_package": {
    "projection_requirements_defined": true,
    "validated_assumptions_ready": true
  }
}
```

**Key Takeaway**: Stage 2 and 3 form the analytical heart of the system. They build a complete and validated historical financial reality for the business, and then use that reality to craft a sophisticated, data-driven, and defensible strategy for creating the final projections in Stage 4. 