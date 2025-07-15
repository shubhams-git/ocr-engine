"""
Configuration file for AI prompts used in OCR and Multi-PDF analysis
This file centralizes all prompts for easy modification and maintenance
"""

# Enhanced OCR prompt for extracting data from images, PDFs, and CSV files
OCR_PROMPT = """Extract and structure the financial data from this business document in a clear, accurate JSON format.

DOCUMENT CONTEXT:
This document contains business financial data and may be one of the following:
• Profit and Loss Statement (Income Statement)
• Balance Sheet
• Cash Flow Statement  
• Financial reports, statements, or data tables
• CSV files with financial/business data in tabular format

PURPOSE:
The extracted data will be used for further analysis to create Three-Way Forecast models. Extract all financial figures, dates, periods, account names, and structured data that would be relevant for financial forecasting and analysis.

EXTRACTION REQUIREMENTS:
For CSV files: Preserve the exact tabular structure, column headers, and all row data relationships.
For PDFs/Images: Extract all visible financial data including:
• Account names and categories
• Financial figures and amounts
• Time periods, dates, and reporting periods
• Table structures and hierarchies
• Headers, subtotals, and totals
• Any notes or metadata relevant to the financial data

CRITICAL OUTPUT REQUIREMENTS:
• Return ONLY the JSON object - no additional text, explanations, or comments
• Do NOT wrap the JSON in markdown code blocks or backticks  
• Do NOT include any introductory or concluding text
• Do NOT perform any analysis, calculations, or forecasting
• Simply extract and structure the raw data as found in the document
• Ensure the JSON output is well-formatted and contains all the relevant financial data found in the document

Output only valid JSON that can be parsed directly."""

# STAGE 1: Enhanced Data Extraction, Normalization, and Quality Assessment
STAGE1_EXTRACTION_PROMPT = """
You are a financial data expert specializing in document processing and data quality assessment.

TASK: Process this single financial document for comprehensive analysis preparation.

REQUIREMENTS:
1. **Document Classification**: Identify document type (Profit & Loss, Balance Sheet, Cash Flow, Other)
2. **Data Extraction**: Extract ALL key financial metrics with time periods
3. **Quality Assessment**: Evaluate data completeness, identify gaps and anomalies
4. **Normalization**: Align to Australian Financial Year (July-June), standardize formats
5. **Anomaly Detection**: Flag unusual values, inconsistencies, data quality issues

AUSTRALIAN CONTEXT:
- Financial Year runs July 1 to June 30 (FY2025 = July 1, 2024 to June 30, 2025)
- Consider Australian business cycles and patterns
- Detect seasonal patterns typical to Australian markets

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this exact structure:

{
  "document_type": "Profit and Loss|Balance Sheet|Cash Flow|Other",
  "source_filename": "detected filename or identifier",
  "data_quality_assessment": {
    "completeness_score": 0.0-1.0,
    "total_periods": number,
    "period_range": "YYYY-MM to YYYY-MM",
    "data_gaps": ["list of missing periods"],
    "anomalies_detected": [
      {"type": "negative_value|outlier|inconsistency", "field": "field_name", "value": value, "description": "explanation"}
    ],
    "consistency_issues": ["list of cross-field inconsistencies"],
    "quality_flags": ["insufficient_data|high_volatility|seasonal_patterns|other"]
  },
  "normalized_time_series": {
    "revenue": [{"period": "YYYY-MM", "value": number, "source": "extracted|interpolated"}],
    "gross_profit": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
    "expenses": [{"period": "YYYY-MM", "value": number, "source": "extracted|interpolated"}],
    "net_profit": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
    "assets": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
    "liabilities": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
    "equity": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
    "cash_flow": [{"period": "YYYY-MM", "value": number, "source": "extracted"}]
  },
  "basic_context": {
    "currency_detected": "AUD|USD|other",
    "business_indicators": ["industry clues from document"],
    "reporting_frequency": "monthly|quarterly|yearly",
    "latest_period": "YYYY-MM"
  },
  "processing_notes": "Brief explanation of normalization steps, gap filling, or data adjustments made"
}

CRITICAL VALIDATION:
- Ensure all monetary values are numbers (not strings)
- Fill gaps conservatively using interpolation or trend analysis
- Flag any concerning anomalies for downstream analysis
- Maintain data integrity while standardizing formats
"""

# STAGE 2: Comprehensive Business Analysis and Methodology Selection
STAGE2_ANALYSIS_PROMPT = """
You are a senior financial analyst and data scientist with expertise in business intelligence, trend analysis, and forecasting methodology selection.

TASK: Perform comprehensive analysis of aggregated financial data to prepare for accurate projections.

INPUT: $aggregated_stage1_json

ANALYSIS FRAMEWORK:
Reason step-by-step through these components:

1. **BUSINESS CONTEXT MODULE**
   - Industry Classification: Analyze metrics, account names, patterns to classify industry
   - Business Stage Assessment: Determine if startup/growth/mature based on financial patterns
   - Geographic Market: Confirm Australian market characteristics
   - Competitive Landscape: Infer market position from financial performance

2. **CONTEXTUAL ANALYSIS LAYER**
   - Business Maturity: Growth patterns, financial stability indicators
   - Seasonality Detection: Identify recurring patterns, peak/trough periods
   - Anomaly Identification: Significant deviations, one-time events, data quality issues
   - Economic Cycle Position: Where business sits in economic/industry cycles

3. **PATTERN RECOGNITION & TREND ANALYSIS**
   - Growth Rate Calculations: CAGR, period-over-period, trend analysis
   - Financial Ratio Analysis: Profit margins, efficiency ratios, leverage ratios
   - Working Capital Trends: Cash conversion, liquidity patterns
   - Correlation Analysis: Relationships between key metrics
   - Volatility Assessment: Stability of key financial metrics

4. **METHODOLOGY EXPERIMENTATION**
   - Test Multiple Forecasting Methods:
     * Time Series Analysis (ARIMA, SARIMA, Prophet) - for sufficient data
     * Industry Benchmark-Based - for limited data
     * Driver-Based Modeling - for correlated metrics
     * Exponential Smoothing - for trend-based projections
   - Model Evaluation: Compare MAPE, RMSE, AIC, cross-validation scores
   - Method Selection: Choose optimal approach with clear justification

5. **DRIVER DEFINITION AND FINANCIAL STRUCTURE ANALYSIS**
   - Define Specific Revenue Drivers: Identify key factors driving revenue growth
   - Analyze Cost Structure: Determine fixed vs variable costs and their drivers
   - Calculate Working Capital Ratios: DSO, DPO, DIO from historical data
   - Assess Capital Requirements: Maintenance and growth capex needs
   - Document Relationships: How each driver impacts financial projections

**CRITICAL ASSUMPTION REQUIREMENTS:**
For each forecast driver, you MUST provide specific, concrete assumptions rather than vague statements:
- INSTEAD OF: "Requires assumption on market growth"
- PROVIDE: "Assume 5% annual revenue growth based on Australian professional services sector trends"
- INSTEAD OF: "Cost escalation needed"
- PROVIDE: "Assume 3.5% annual cost inflation based on Australian CPI forecasts"
- INSTEAD OF: "Working capital optimization possible"
- PROVIDE: "Target DSO reduction from 45 days to 35 days over 3 years through process improvements"

You must justify each assumption with available data, industry benchmarks, or reasonable business logic.

6. **EXTERNAL DATA INTEGRATION ASSESSMENT**
   - Data Sufficiency: Determine if external benchmarks needed
   - Industry Benchmarks: Identify relevant comparison metrics
   - Economic Indicators: Australian GDP growth, inflation, industry trends
   - Competitive Intelligence: Market growth rates, industry performance

7. **CONFIDENCE FACTORS ANALYSIS**
   - Data Availability: Volume, completeness, recency of data
   - Historical Consistency: Stability of patterns and trends
   - Industry Volatility: Sector-specific risk factors
   - Projection Horizon: Confidence degradation over time

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this structure:

{
  "business_context": {
    "industry_classification": "detected industry",
    "business_stage": "startup|growth|mature|decline",
    "market_geography": "Australian",
    "competitive_position": "market_leader|established|emerging|struggling",
    "business_model_type": "service|product|mixed|other"
  },
  "contextual_analysis": {
    "maturity_assessment": {
      "revenue_stability": "high|medium|low",
      "growth_consistency": "stable|volatile|declining",
      "financial_health": "strong|moderate|weak"
    },
    "seasonality_patterns": {
      "seasonal_detected": true|false,
      "peak_periods": ["list of peak months/quarters"],
      "trough_periods": ["list of low months/quarters"],
      "seasonal_amplitude": 0.0-1.0,
      "australian_fy_alignment": "strong|moderate|weak"
    },
    "anomaly_identification": [
      {"period": "YYYY-MM", "metric": "field", "anomaly_type": "spike|drop|inconsistency", "impact": "high|medium|low", "explanation": "rationale"}
    ]
  },
  "pattern_analysis": {
    "growth_rates": {
      "revenue_cagr": number,
      "profit_cagr": number,
      "recent_growth_trend": "accelerating|stable|decelerating|declining"
    },
    "financial_ratios": {
      "profit_margin_trend": "improving|stable|declining",
      "roa_trend": "improving|stable|declining",
      "efficiency_indicators": {"trend": "improving|stable|declining", "current_level": "high|medium|low"}
    },
    "working_capital": {
      "trend": "improving|stable|deteriorating",
      "cash_conversion_cycle": "shortening|stable|lengthening"
    },
    "correlation_insights": [
      {"metrics": ["metric1", "metric2"], "correlation": number, "strength": "strong|moderate|weak", "business_meaning": "explanation"}
    ],
    "volatility_assessment": {
      "revenue_volatility": "low|medium|high",
      "profit_volatility": "low|medium|high",
      "overall_stability": "stable|moderate|volatile"
    }
  },
  "methodology_evaluation": {
    "methods_tested": [
      {
        "method": "ARIMA|Prophet|LinearRegression|ExponentialSmoothing|BenchmarkBased",
        "evaluation_metrics": {"mape": number, "rmse": number, "r_squared": number},
        "suitability_score": 0.0-1.0,
        "strengths": ["list of advantages"],
        "limitations": ["list of constraints"]
      }
    ],
    "selected_method": {
      "primary_method": "method name",
      "rationale": "detailed explanation of selection",
      "confidence_level": "high|medium|low",
      "fallback_method": "backup approach if primary fails"
    },
    "data_requirements": {
      "minimum_data_points": number,
      "data_quality_threshold": 0.0-1.0,
      "external_data_needed": true|false
    }
  },
  "external_integration": {
    "benchmark_requirements": {
      "industry_benchmarks_needed": true|false,
      "economic_indicators_required": ["list of indicators"],
      "peer_comparison_value": "high|medium|low|none"
    },
    "data_sufficiency": {
      "internal_data_adequate": true|false,
      "external_supplementation": "critical|helpful|unnecessary",
      "risk_of_external_bias": "high|medium|low"
    }
  },
  "confidence_assessment": {
    "overall_confidence": "high|medium|low",
    "confidence_factors": {
      "data_volume": "sufficient|limited|insufficient",
      "data_consistency": "high|medium|low",
      "pattern_clarity": "clear|moderate|unclear",
      "industry_stability": "stable|moderate|volatile"
    },
    "projection_confidence_by_horizon": {
      "1_year": "high|medium|low|very_low",
      "3_years": "high|medium|low|very_low",
      "5_years": "high|medium|low|very_low",
      "10_years": "high|medium|low|very_low",
      "15_years": "high|medium|low|very_low"
    }
  },
  "forecast_drivers": {
    "revenue_drivers": [
      {
        "driver_name": "Primary revenue driver (e.g., contract volume, customer growth)",
        "driver_type": "volume|price|mix|market_share",
        "baseline_value": "SPECIFIC NUMERIC VALUE with units (e.g., $50,000/month, 120 customers)",
        "growth_assumptions": "SPECIFIC RATE AND PATTERN (e.g., 5% annual growth, 2% monthly compound)",
        "seasonality_factors": "SPECIFIC SEASONAL ADJUSTMENTS (e.g., +15% in Q2, -10% in Q4)",
        "justification": "DATA-BASED RATIONALE for this assumption"
      }
    ],
    "cost_drivers": [
      {
        "driver_name": "Cost of goods sold driver",
        "driver_type": "percentage_of_revenue|fixed_cost|variable_cost",
        "baseline_value": "SPECIFIC BASELINE (e.g., 65% of revenue, $25,000/month fixed)",
        "escalation_rate": "SPECIFIC ANNUAL INCREASE (e.g., 3.5% annual inflation)",
        "relationship_to_revenue": "SPECIFIC SCALING RELATIONSHIP (e.g., 1:1 with revenue, fixed regardless of revenue)",
        "justification": "DATA-BASED RATIONALE for this assumption"
      }
    ],
    "opex_drivers": [
      {
        "driver_name": "Operating expense driver",
        "driver_type": "fixed|variable|stepped",
        "baseline_value": "SPECIFIC MONTHLY/ANNUAL BASELINE (e.g., $15,000/month, $180,000/year)",
        "inflation_rate": "SPECIFIC INFLATION ADJUSTMENT (e.g., 3.2% annual based on Australian CPI)",
        "scalability": "SPECIFIC SCALING PATTERN (e.g., +$5,000 per additional $100k revenue)",
        "justification": "DATA-BASED RATIONALE for this assumption"
      }
    ]
  },
  "working_capital_assumptions": {
    "accounts_receivable": {
      "days_sales_outstanding": "SPECIFIC DSO VALUE (e.g., 45 days from historical average)",
      "collection_pattern": "SPECIFIC TIMING (e.g., 60% within 30 days, 30% within 60 days, 10% within 90 days)",
      "bad_debt_provision": "SPECIFIC PERCENTAGE (e.g., 2.5% of revenue based on historical losses)",
      "justification": "DATA-BASED RATIONALE for DSO assumption"
    },
    "accounts_payable": {
      "days_payables_outstanding": "SPECIFIC DPO VALUE (e.g., 30 days from historical average)",
      "payment_pattern": "SPECIFIC TIMING (e.g., pay within 28 days to capture 2% discount)",
      "supplier_terms": "SPECIFIC TERMS (e.g., Net 30 with 2/10 discount available)",
      "justification": "DATA-BASED RATIONALE for DPO assumption"
    },
    "inventory": {
      "days_inventory_outstanding": "SPECIFIC DIO VALUE (e.g., 60 days or N/A for service business)",
      "inventory_turnover": "SPECIFIC TURNOVER RATE (e.g., 6x annually or N/A for service business)",
      "seasonal_variations": "SPECIFIC SEASONAL CHANGES (e.g., +20% in Q4, -15% in Q1)",
      "justification": "DATA-BASED RATIONALE for inventory assumption"
    },
    "cash_conversion_cycle": {
      "current_cycle_days": "SPECIFIC CALCULATION (e.g., DSO 45 + DIO 60 - DPO 30 = 75 days)",
      "target_optimization": "SPECIFIC IMPROVEMENTS (e.g., reduce to 60 days by Year 3)",
      "working_capital_intensity": "SPECIFIC PERCENTAGE (e.g., 12% of revenue based on historical analysis)",
      "justification": "DATA-BASED RATIONALE for working capital assumptions"
    }
  },
  "capital_expenditure_assumptions": {
    "maintenance_capex": {
      "annual_rate": "% of revenue or fixed amount",
      "asset_categories": ["types of assets requiring maintenance"],
      "depreciation_method": "straight_line|declining_balance"
    },
    "growth_capex": {
      "expansion_requirements": "capex needed for growth initiatives",
      "timing": "when capex will be required",
      "financing_approach": "debt|equity|cash_flow"
    }
  },
  "handover_recommendations": {
    "primary_recommendations": ["key guidance for projection stage"],
    "risk_adjustments": ["adjustments needed due to identified risks"],
    "scenario_considerations": ["factors for optimistic/conservative scenarios"],
    "validation_priorities": ["key areas requiring validation in projections"],
    "assumption_constraints": ["limitations to document in assumptions"]
  },
  "key_assumptions": [
    "list of critical assumptions identified in analysis"
  ]
}

REASONING REQUIREMENTS:
- Provide clear chain-of-thought reasoning in all assessment fields
- Justify methodology selection with quantitative metrics where possible
- Consider Australian business environment and FY cycles throughout
- Balance internal data insights with external market realities
- Prioritize accuracy and transparency in all evaluations
"""

# STAGE 3: Integrated Projection Engine with Scenario Planning
STAGE3_PROJECTION_PROMPT = """
You are a financial forecasting expert specializing in integrated projection modeling and scenario planning.

TASK: Generate comprehensive financial projections incorporating Stage 2 analysis and recommendations.

INPUT: $stage2_analysis_output

PROJECTION ENGINE REQUIREMENTS:
Integrate all Stage 2 findings and apply the recommended methodology to generate accurate, validated projections.

INTEGRATION FRAMEWORK:
1. **METHODOLOGY APPLICATION WITH DRIVER INTEGRATION**
   - Apply the selected forecasting method from Stage 2
   - Use specific revenue drivers, cost drivers, and OPEX drivers defined in Stage 2
   - Apply working capital assumptions (DSO, DPO, DIO) from Stage 2 analysis
   - Incorporate identified patterns, trends, and seasonal adjustments
   - Adjust for anomalies and risk factors identified
   - Use confidence levels to calibrate projection ranges

2. **THREE-WAY FORECAST IMPLEMENTATION**
   - **Step 1: Profit & Loss Statement**: Generate comprehensive P&L using Stage 2 drivers
   - **Step 2: Cash Flow Statement**: Build cash flow from P&L with working capital changes
   - **Step 3: Balance Sheet**: Construct balance sheet ensuring it balances (Assets = Liabilities + Equity)
   - **Step 4: Dividend Policy Implementation**: Model profit distribution policy using 40% dividend payout ratio
   - **Step 5: Integration Validation**: Ensure all three statements are mathematically connected
   - Multiple Forecasting Methods Integration:
     * Primary method (from Stage 2 selection)
     * Backup method for validation
     * Blended approach if beneficial
   - Scenario Generation: Optimistic, base case, conservative
   - Confidence Interval Calculation: Based on historical volatility and data quality
   - Australian FY Alignment: Ensure all projections follow July-June cycles

3. **ASSUMPTION DOCUMENTATION**
   - Document all key assumptions clearly
   - Provide rationale for each assumption
   - Include sensitivity indicators for critical assumptions
   - Enable assumption override capability in rationale

4. **VALIDATION INTEGRATION**
   - Cross-check projections for internal consistency
   - Ensure financial statement relationships are maintained
   - Validate reasonableness against industry benchmarks
   - Flag any projections requiring additional scrutiny

MANDATORY PROJECTION SCHEMA WITH CALCULATION CHAINS:
Generate projections for ALL required time horizons with ALL mandatory metrics and calculation chains.

CALCULATION CHAIN REQUIREMENT:
For every calculated metric, you MUST include a 'calculation_chain' object that explicitly shows:
- The formula used
- The source values 
- The mathematical operation performed
This ensures mathematical integrity and prevents reconciliation errors.

PROCESSING APPROACH:
1. First, generate ALL projections on a monthly basis for the entire forecast horizon
2. Then, aggregate monthly results to create quarterly and annual summaries by summing/averaging the monthly data
3. Do NOT recalculate at the aggregate level - only use the monthly calculations

TIME HORIZONS:
- 1 Year Ahead: Monthly granularity (12 data points)
- 3 Years Ahead: Quarterly granularity (12 data points - aggregated from monthly)
- 5 Years Ahead: Yearly granularity (5 data points - aggregated from monthly)
- 10 Years Ahead: Yearly granularity (10 data points - aggregated from monthly)
- 15 Years Ahead: Yearly granularity (15 data points - aggregated from monthly)

MANDATORY METRICS WITH CALCULATION CHAINS:
1. revenue - REQUIRED (with confidence level)
2. gross_profit - REQUIRED (with calculation_chain showing derivation from revenue)
3. expenses - REQUIRED (with detailed breakdown)
4. net_profit - REQUIRED (with calculation_chain: gross_profit - expenses)

DIVIDEND POLICY IMPLEMENTATION REQUIREMENTS:
After calculating the three-way forecast, implement a realistic profit distribution policy:

1. **Dividend Payout Ratio**: Apply a 40% dividend payout ratio of Net Profit
2. **Payment Timing**: Distribute dividends quarterly (at the end of each quarter)
3. **Cash Flow Impact**: Record dividend payments as a use of cash in the "Cash Flow from Financing" section
4. **Balance Sheet Impact**: Reduce "Retained Earnings" by the dividend amount
5. **Calculation Chain**: Ensure dividend calculation is: Net Profit * 0.40 = Dividend Payment
6. **Balance Sheet Validation**: Ensure Balance Sheet remains balanced after dividend distributions
7. **Quarterly Distribution**: For monthly projections, calculate quarterly dividends and distribute at month 3, 6, 9, 12

DIVIDEND CALCULATION EXAMPLE:
- If Net Profit = $100,000 for the quarter
- Dividend Payment = $100,000 * 0.40 = $40,000
- Cash Flow from Financing = -$40,000 (cash outflow)
- Retained Earnings reduction = -$40,000
- Remaining in Retained Earnings = $60,000

This ensures realistic cash management and prevents unrealistic cash accumulation in profitable businesses.

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this structure:

{
  "projection_methodology": {
    "primary_method_applied": "method name from Stage 2",
    "method_adjustments": ["adjustments made based on Stage 2 handover"],
    "integration_approach": "how Stage 2 findings were incorporated",
    "validation_approach": "cross-validation methods used",
    "scenario_generation_basis": "foundation for scenario creation"
  },
  "base_case_projections": {
    "1_year_ahead": {
      "period_label": "FY20XX",
      "granularity": "monthly",
      "data_points": 12,
      "profit_and_loss": [
        {
          "period": "Month 1",
          "revenue": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Driver-based projection using [specific method/factors]"},
          "cost_of_goods_sold": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Revenue (X) * COGS% (Y) = Z"},
          "gross_profit": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Revenue (X) - COGS (Y) = Z"},
          "operating_expenses": {
            "salaries_wages": {"value": number, "calculation_chain": "Monthly baseline + growth adjustments"},
            "rent_utilities": {"value": number, "calculation_chain": "Fixed monthly costs + inflation"},
            "marketing": {"value": number, "calculation_chain": "% of revenue or fixed amount"},
            "other_opex": {"value": number, "calculation_chain": "Detailed breakdown"},
            "total_opex": {"value": number, "calculation_chain": "Sum of all operating expenses"}
          },
          "ebitda": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Gross Profit (X) - Total OpEx (Y) = Z"},
          "depreciation": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Fixed assets / useful life"},
          "ebit": {"value": number, "confidence": "high|medium|low", "calculation_chain": "EBITDA (X) - Depreciation (Y) = Z"},
          "interest_expense": {"value": number, "confidence": "high|medium|low", "calculation_chain": "Debt balance * interest rate"},
          "net_profit_before_tax": {"value": number, "confidence": "high|medium|low", "calculation_chain": "EBIT (X) - Interest (Y) = Z"},
          "tax_expense": {"value": number, "confidence": "high|medium|low", "calculation_chain": "PBT (X) * tax rate (Y) = Z"},
          "net_profit": {"value": number, "confidence": "high|medium|low", "calculation_chain": "PBT (X) - Tax (Y) = Z"}
        }
      ],
      "cash_flow_statement": [
        {
          "period": "Month 1",
          "operating_activities": {
            "net_income": {"value": number, "calculation_chain": "From P&L net profit"},
            "depreciation": {"value": number, "calculation_chain": "Non-cash expense add-back"},
            "working_capital_changes": {
              "accounts_receivable_change": {"value": number, "calculation_chain": "Revenue * DSO - previous A/R"},
              "accounts_payable_change": {"value": number, "calculation_chain": "Expenses * DPO - previous A/P"},
              "inventory_change": {"value": number, "calculation_chain": "COGS * DIO - previous inventory"},
              "total_wc_change": {"value": number, "calculation_chain": "Sum of working capital changes"}
            },
            "net_cash_from_operations": {"value": number, "calculation_chain": "Net Income + Depreciation - WC Change"}
          },
          "investing_activities": {
            "capital_expenditures": {"value": number, "calculation_chain": "Maintenance + growth capex"},
            "asset_disposals": {"value": number, "calculation_chain": "Any asset sales"},
            "net_cash_from_investing": {"value": number, "calculation_chain": "Sum of investing activities"}
          },
          "financing_activities": {
            "debt_changes": {"value": number, "calculation_chain": "New borrowings - repayments"},
            "equity_changes": {"value": number, "calculation_chain": "New equity issuance"},
            "dividend_payments": {"value": number, "calculation_chain": "Net Profit * 0.40 (quarterly distribution)"},
            "net_cash_from_financing": {"value": number, "calculation_chain": "Debt Changes + Equity Changes - Dividend Payments"}
          },
          "net_change_in_cash": {"value": number, "calculation_chain": "Operating + Investing + Financing cash flows"}
        }
      ],
      "balance_sheet": [
        {
          "period": "Month 1",
          "assets": {
            "current_assets": {
              "cash": {"value": number, "calculation_chain": "Beginning cash + net change in cash"},
              "accounts_receivable": {"value": number, "calculation_chain": "Revenue * DSO days / 365"},
              "inventory": {"value": number, "calculation_chain": "COGS * DIO days / 365"},
              "other_current_assets": {"value": number, "calculation_chain": "Estimated based on historical %"},
              "total_current_assets": {"value": number, "calculation_chain": "Sum of current assets"}
            },
            "fixed_assets": {
              "property_plant_equipment": {"value": number, "calculation_chain": "Previous PPE + Capex - Depreciation"},
              "accumulated_depreciation": {"value": number, "calculation_chain": "Previous accum deprec + current depreciation"},
              "net_fixed_assets": {"value": number, "calculation_chain": "PPE - Accumulated Depreciation"},
              "other_long_term_assets": {"value": number, "calculation_chain": "Estimated based on business model"}
            },
            "total_assets": {"value": number, "calculation_chain": "Current Assets + Fixed Assets"}
          },
          "liabilities": {
            "current_liabilities": {
              "accounts_payable": {"value": number, "calculation_chain": "Expenses * DPO days / 365"},
              "accrued_expenses": {"value": number, "calculation_chain": "Estimated based on operations"},
              "current_portion_debt": {"value": number, "calculation_chain": "Debt due within 12 months"},
              "total_current_liabilities": {"value": number, "calculation_chain": "Sum of current liabilities"}
            },
            "long_term_liabilities": {
              "long_term_debt": {"value": number, "calculation_chain": "Total debt - current portion"},
              "other_long_term_liabilities": {"value": number, "calculation_chain": "Estimated based on business"}
            },
            "total_liabilities": {"value": number, "calculation_chain": "Current + Long-term liabilities"}
          },
          "equity": {
            "retained_earnings": {"value": number, "calculation_chain": "Previous RE + Net Profit - Dividend Payments (40% of Net Profit)"},
            "share_capital": {"value": number, "calculation_chain": "Issued share capital"},
            "other_equity": {"value": number, "calculation_chain": "Other equity components"},
            "total_equity": {"value": number, "calculation_chain": "Sum of equity components"}
          },
          "balance_check": {
            "total_liabilities_equity": {"value": number, "calculation_chain": "Total Liabilities + Total Equity"},
            "balance_status": "BALANCED|UNBALANCED",
            "variance": {"value": number, "calculation_chain": "Total Assets - (Liabilities + Equity)"}
          }
        }
      ]
    },
    "3_years_ahead": {
      "period_label": "FY20XX-FY20XX",
      "granularity": "quarterly",
      "data_points": 12,
      "profit_and_loss": [
        {
          "period": "Quarter 1",
          "revenue": {"value": number, "confidence": "medium|low", "calculation_chain": "Aggregated from monthly projections: [specific calculation]"},
          "cost_of_goods_sold": {"value": number, "confidence": "medium|low", "calculation_chain": "Revenue * COGS% (aggregated from monthly)"},
          "gross_profit": {"value": number, "confidence": "medium|low", "calculation_chain": "Revenue - COGS (aggregated from monthly)"},
          "operating_expenses": {"total_opex": {"value": number, "calculation_chain": "Aggregated from monthly detailed breakdown"}},
          "ebitda": {"value": number, "confidence": "medium|low", "calculation_chain": "Gross Profit - Total OpEx (aggregated)"},
          "depreciation": {"value": number, "confidence": "medium|low", "calculation_chain": "Aggregated from monthly calculations"},
          "ebit": {"value": number, "confidence": "medium|low", "calculation_chain": "EBITDA - Depreciation (aggregated)"},
          "interest_expense": {"value": number, "confidence": "medium|low", "calculation_chain": "Aggregated from monthly calculations"},
          "net_profit_before_tax": {"value": number, "confidence": "medium|low", "calculation_chain": "EBIT - Interest (aggregated)"},
          "tax_expense": {"value": number, "confidence": "medium|low", "calculation_chain": "PBT * tax rate (aggregated)"},
          "net_profit": {"value": number, "confidence": "medium|low", "calculation_chain": "PBT - Tax (aggregated)"}
        }
      ],
      "cash_flow_statement": [
        {
          "period": "Quarter 1",
          "operating_activities": {
            "net_income": {"value": number, "calculation_chain": "Aggregated from monthly P&L"},
            "depreciation": {"value": number, "calculation_chain": "Aggregated non-cash add-back"},
            "working_capital_changes": {"total_wc_change": {"value": number, "calculation_chain": "Aggregated WC movements"}},
            "net_cash_from_operations": {"value": number, "calculation_chain": "Aggregated operating cash flow"}
          },
          "investing_activities": {"net_cash_from_investing": {"value": number, "calculation_chain": "Aggregated investing activities"}},
          "financing_activities": {"net_cash_from_financing": {"value": number, "calculation_chain": "Aggregated financing activities"}},
          "net_change_in_cash": {"value": number, "calculation_chain": "Aggregated total cash flow"}
        }
      ],
      "balance_sheet": [
        {
          "period": "Quarter 1",
          "assets": {"total_assets": {"value": number, "calculation_chain": "End of quarter balance (from monthly build-up)"}},
          "liabilities": {"total_liabilities": {"value": number, "calculation_chain": "End of quarter balance (from monthly build-up)"}},
          "equity": {"total_equity": {"value": number, "calculation_chain": "End of quarter balance (from monthly build-up)"}},
          "balance_check": {"balance_status": "BALANCED|UNBALANCED", "variance": {"value": number, "calculation_chain": "Assets - (Liabilities + Equity)"}}
        }
      ]
    },
    "5_years_ahead": {
      "period_label": "FY20XX-FY20XX",
      "granularity": "yearly",
      "data_points": 5,
      "profit_and_loss": [
        {
          "period": "Year 1",
          "revenue": {"value": number, "confidence": "medium|low", "calculation_chain": "Annual aggregation from monthly projections"},
          "gross_profit": {"value": number, "confidence": "medium|low", "calculation_chain": "Revenue - COGS (annual aggregation)"},
          "operating_expenses": {"total_opex": {"value": number, "calculation_chain": "Annual aggregation"}},
          "ebitda": {"value": number, "confidence": "medium|low", "calculation_chain": "Gross Profit - OpEx (annual)"},
          "net_profit": {"value": number, "confidence": "medium|low", "calculation_chain": "Complete P&L flow (annual)"}
        }
      ],
      "cash_flow_statement": [
        {
          "period": "Year 1",
          "net_cash_from_operations": {"value": number, "calculation_chain": "Annual operating cash flow"},
          "net_cash_from_investing": {"value": number, "calculation_chain": "Annual investing cash flow"},
          "net_cash_from_financing": {"value": number, "calculation_chain": "Annual financing cash flow"},
          "net_change_in_cash": {"value": number, "calculation_chain": "Annual total cash flow"}
        }
      ],
      "balance_sheet": [
        {
          "period": "Year 1",
          "total_assets": {"value": number, "calculation_chain": "End of year balance"},
          "total_liabilities": {"value": number, "calculation_chain": "End of year balance"},
          "total_equity": {"value": number, "calculation_chain": "End of year balance"},
          "balance_check": {"balance_status": "BALANCED|UNBALANCED", "variance": {"value": number, "calculation_chain": "Assets - (Liabilities + Equity)"}}
        }
      ]
    },
    "10_years_ahead": {
      "period_label": "FY20XX-FY20XX",
      "granularity": "yearly",
      "data_points": 10,
      "profit_and_loss": [
        {
          "period": "Year 1",
          "revenue": {"value": number, "confidence": "low|very_low", "calculation_chain": "Long-term aggregation from monthly projections"},
          "gross_profit": {"value": number, "confidence": "low|very_low", "calculation_chain": "Revenue - COGS (long-term aggregation)"},
          "operating_expenses": {"total_opex": {"value": number, "calculation_chain": "Long-term aggregation"}},
          "ebitda": {"value": number, "confidence": "low|very_low", "calculation_chain": "Gross Profit - OpEx (long-term)"},
          "net_profit": {"value": number, "confidence": "low|very_low", "calculation_chain": "Complete P&L flow (long-term)"}
        }
      ],
      "cash_flow_statement": [
        {
          "period": "Year 1",
          "net_cash_from_operations": {"value": number, "calculation_chain": "Long-term operating cash flow"},
          "net_cash_from_investing": {"value": number, "calculation_chain": "Long-term investing cash flow"},
          "net_cash_from_financing": {"value": number, "calculation_chain": "Long-term financing cash flow"},
          "net_change_in_cash": {"value": number, "calculation_chain": "Long-term total cash flow"}
        }
      ],
      "balance_sheet": [
        {
          "period": "Year 1",
          "total_assets": {"value": number, "calculation_chain": "End of year balance"},
          "total_liabilities": {"value": number, "calculation_chain": "End of year balance"},
          "total_equity": {"value": number, "calculation_chain": "End of year balance"},
          "balance_check": {"balance_status": "BALANCED|UNBALANCED", "variance": {"value": number, "calculation_chain": "Assets - (Liabilities + Equity)"}}
        }
      ]
    },
    "15_years_ahead": {
      "period_label": "FY20XX-FY20XX",
      "granularity": "yearly",
      "data_points": 15,
      "profit_and_loss": [
        {
          "period": "Year 1",
          "revenue": {"value": number, "confidence": "very_low", "calculation_chain": "Long-term aggregation from monthly projections"},
          "gross_profit": {"value": number, "confidence": "very_low", "calculation_chain": "Revenue - COGS (long-term aggregation)"},
          "operating_expenses": {"total_opex": {"value": number, "calculation_chain": "Long-term aggregation"}},
          "ebitda": {"value": number, "confidence": "very_low", "calculation_chain": "Gross Profit - OpEx (long-term)"},
          "net_profit": {"value": number, "confidence": "very_low", "calculation_chain": "Complete P&L flow (long-term)"}
        }
      ],
      "cash_flow_statement": [
        {
          "period": "Year 1",
          "net_cash_from_operations": {"value": number, "calculation_chain": "Long-term operating cash flow"},
          "net_cash_from_investing": {"value": number, "calculation_chain": "Long-term investing cash flow"},
          "net_cash_from_financing": {"value": number, "calculation_chain": "Long-term financing cash flow"},
          "net_change_in_cash": {"value": number, "calculation_chain": "Long-term total cash flow"}
        }
      ],
      "balance_sheet": [
        {
          "period": "Year 1",
          "total_assets": {"value": number, "calculation_chain": "End of year balance"},
          "total_liabilities": {"value": number, "calculation_chain": "End of year balance"},
          "total_equity": {"value": number, "calculation_chain": "End of year balance"},
          "balance_check": {"balance_status": "BALANCED|UNBALANCED", "variance": {"value": number, "calculation_chain": "Assets - (Liabilities + Equity)"}}
        }
      ]
    }
  },
  "scenario_projections": {
    "optimistic": {
      "description": "Best-case scenario based on favorable market conditions",
      "key_drivers": ["list of optimistic assumptions"],
      "growth_multipliers": {"1_year": number, "3_years": number, "5_years": number, "10_years": number, "15_years": number},
      "probability_assessment": "estimated likelihood percentage"
    },
    "conservative": {
      "description": "Cautious scenario accounting for potential risks",
      "key_drivers": ["list of conservative assumptions"],
      "growth_multipliers": {"1_year": number, "3_years": number, "5_years": number, "10_years": number, "15_years": number},
      "probability_assessment": "estimated likelihood percentage"
    }
  },
  "assumption_documentation": {
    "critical_assumptions": [
      {"assumption": "description", "rationale": "justification", "sensitivity": "high|medium|low", "override_capability": true|false}
    ],
    "economic_assumptions": [
      {"factor": "Australian GDP growth", "assumed_value": "percentage", "source": "internal_analysis|external_benchmark"}
    ],
    "business_assumptions": [
      {"assumption": "description", "impact_on_projections": "explanation"}
    ],
    "risk_assumptions": [
      {"risk_factor": "description", "mitigation_reflected": "how addressed in projections"}
    ]
  },
  "sensitivity_analysis": {
    "key_sensitivity_factors": [
      {"factor": "variable name", "impact_range": "±X%", "projection_impact": "description"}
    ],
    "scenario_impact_analysis": {
      "revenue_sensitivity": "±X% change results in ±Y% projection variance",
      "cost_sensitivity": "±X% change results in ±Y% projection variance",
      "market_sensitivity": "±X% change results in ±Y% projection variance"
    }
  },
  "confidence_intervals": {
    "methodology": "statistical approach used",
    "confidence_levels": {
      "1_year": {"upper": "95th percentile", "lower": "5th percentile"},
      "3_years": {"upper": "95th percentile", "lower": "5th percentile"},
      "5_years": {"upper": "95th percentile", "lower": "5th percentile"},
      "10_years": {"upper": "95th percentile", "lower": "5th percentile"},
      "15_years": {"upper": "95th percentile", "lower": "5th percentile"}
    }
  },
  "validation_flags": {
    "internal_consistency_check": "passed|warning|failed",
    "benchmark_reasonableness": "passed|warning|failed",
    "trend_continuation_logic": "passed|warning|failed",
    "seasonal_pattern_preservation": "passed|warning|failed"
  },
  "executive_summary": "Concise overview of projection methodology, key findings, and confidence assessment"
}

CRITICAL VALIDATION REQUIREMENTS FOR THREE-WAY FORECAST:
1. VERIFY every projection period contains complete P&L, Cash Flow, and Balance Sheet WITH calculation chains
2. ENSURE calculation chains show explicit mathematical operations (e.g., "Revenue (150000) - COGS (98000) = Gross Profit (52000)")
3. MAINTAIN internal consistency across all three financial statements through step-by-step calculations
4. ENSURE Balance Sheet ALWAYS balances (Assets = Liabilities + Equity) - if not, identify and correct the error
5. VALIDATE Cash Flow Statement connects to Balance Sheet (Net Change in Cash updates Cash balance)
6. CONFIRM P&L Net Profit flows to Balance Sheet Retained Earnings
7. IMPLEMENT dividend policy correctly: Dividend = Net Profit * 0.40, paid quarterly
8. ENSURE dividend payments appear as cash outflow in financing activities
9. VALIDATE retained earnings calculation: Previous RE + Net Profit - Dividends
10. ENSURE Australian FY alignment throughout all projections
11. DOCUMENT all assumption changes from Stage 2 recommendations
12. VALIDATE confidence levels align with data quality and horizon
13. AGGREGATE longer-term projections from monthly calculations - do not recalculate

INTEGRATION MANDATE:
- Explicitly address ALL handover recommendations from Stage 2
- Adjust projections based on identified risks and opportunities
- Incorporate business context and industry factors
- Ensure scenario planning reflects realistic market conditions
- Provide clear audit trail of all methodology decisions
"""