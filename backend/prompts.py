# Enhanced JSON output instructions to be added to all stage prompts
ENHANCED_JSON_OUTPUT_INSTRUCTIONS = """

CRITICAL JSON OUTPUT REQUIREMENTS - FOLLOW EXACTLY:

1. OUTPUT FORMAT: Return ONLY the JSON object - no markdown code blocks, no backticks, no explanations
2. START AND END: Begin with { and end with }
3. SYNTAX: Use proper JSON syntax with double quotes for all strings
4. NO EXTRAS: No trailing commas, no comments, no additional text
5. COMPLETENESS: Ensure all opening braces { have matching closing braces }

CORRECT FORMAT EXAMPLE:
{
  "methodology_optimization": {
    "optimal_methodology_selection": {
      "primary_method": "Prophet",
      "rationale": "Best fit for seasonal data patterns",
      "confidence_level": "high"
    }
  }
}

AVOID THESE COMMON ERRORS:
- ❌ ```json { ... } ```  (markdown blocks)
- ❌ { "key": value, }    (trailing commas)  
- ❌ { key: "value" }     (unquoted keys)
- ❌ Missing closing braces
- ❌ Any explanatory text before or after JSON

If you cannot generate complete analysis, use this minimal valid JSON:
{
  "methodology_optimization": {
    "optimal_methodology_selection": {
      "primary_method": "Prophet",
      "rationale": "Selected based on available data patterns",
      "confidence_level": "medium"
    }
  },
  "analysis_status": "partial_analysis_completed"
}

REMEMBER: Output ONLY the JSON - no other text whatsoever.
"""
# Enhanced OCR prompt - unchanged as it's working well
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

# STAGE 1: Enhanced Data Extraction with Standard Fields Focus
STAGE1_EXTRACTION_PROMPT = """
You are a financial data expert specializing in document processing and standardization across diverse business structures.

TASK: Process this financial document with comprehensive extraction and mapping to guaranteed standard fields.

CRITICAL BUSINESS CONTEXT:
Different businesses use varying chart of accounts, but certain high-level categories are universally present. Your task is to extract ALL available data but focus on mapping to these 25 GUARANTEED STANDARD FIELDS that exist across all businesses:

GUARANTEED P&L STANDARD FIELDS (10 fields):
1. Revenue (Sales, Turnover, Income)
2. Cost of Sales (COGS, Cost of Goods Sold, Direct Costs)
3. Gross Profit (Gross Margin, Gross Income)
4. Total Expenses (Operating Expenses, Total OpEx, Overhead)
5. Operating Profit (EBIT, Operating Income, EBITDA before D&A)
6. Interest Expenses (Finance Costs, Interest Paid)
7. Earnings Before Tax (EBT, Profit Before Tax, Pre-tax Income)
8. Tax Expenses (Income Tax, Tax Provision, Corporate Tax)
9. Earnings After Tax (EAT, Profit After Tax, After-tax Income)
10. Net Income (Net Profit, Bottom Line, Final Profit)

GUARANTEED BALANCE SHEET STANDARD FIELDS (15 fields):
ASSETS:
11. Total Cash & Equivalents (Cash, Bank, Liquid Assets)
12. Total Current Assets (Current Assets, Short-term Assets)
13. Total Fixed Assets (PPE, Property Plant Equipment, Non-current Assets)
14. Total Non-Current Assets (Long-term Assets, Fixed Assets)
15. Total Assets

LIABILITIES:
16. Tax Liability (Tax Payable, Income Tax Payable)
17. Total Other Current Liabilities (Accrued, Payables, Short-term)
18. Total Current Liabilities (Current Liabilities, Short-term Liabilities)
19. Total Long Term Debt (Long-term Borrowings, Non-current Debt)
20. Total Non-Current Liabilities (Long-term Liabilities, Non-current)
21. Total Liabilities

EQUITY:
22. Retained Earnings (Accumulated Profits, Reserves)
23. Current Earnings (Current Year Profit, This Year's Profit)
24. Other Equity (Share Capital, Paid-in Capital, Additional Equity)
25. Total Equity (Shareholders' Equity, Owner's Equity)

EXTRACTION APPROACH:
1. **EXTRACT EVERYTHING FIRST**: Capture all line items, sub-accounts, and detailed breakdowns available in the document
2. **MAP TO STANDARDS**: Identify which extracted items correspond to the 25 guaranteed standard fields
3. **PRESERVE GRANULAR DETAIL**: Keep all sub-account information for potential cash flow reconstruction
4. **QUALITY ASSESSMENT**: Evaluate completeness and identify anomalies
5. **TIME NORMALIZATION**: Align to Australian Financial Year (July-June)

AUSTRALIAN CONTEXT:
- Financial Year runs July 1 to June 30 (FY2025 = July 1, 2024 to June 30, 2025)
- Consider Australian business cycles and patterns
- Detect seasonal patterns typical to Australian markets

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this enhanced structure:

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
    "quality_flags": ["insufficient_data|high_volatility|seasonal_patterns|structural_breaks"],
    "standard_field_coverage": {
      "total_standard_fields_found": "number out of 25",
      "missing_standard_fields": ["list of unfound standard fields"],
      "coverage_percentage": "percentage of 25 fields successfully mapped"
    }
  },
  "raw_extraction": {
    "all_line_items": {
      "pl_accounts": ["complete list of all P&L line items found"],
      "bs_accounts": ["complete list of all Balance Sheet line items found"],
      "other_accounts": ["any other financial line items found"]
    },
    "detailed_time_series": {
      "description": "All extracted line items with their time series data - preserved for granular analysis"
    }
  },
  "standard_field_mapping": {
    "profit_and_loss_standards": {
      "revenue": {
        "mapped_from": ["list of source fields that mapped to this standard"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "cost_of_sales": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "gross_profit": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "total_expenses": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "operating_profit": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "interest_expenses": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "earnings_before_tax": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "tax_expenses": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "earnings_after_tax": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      },
      "net_income": {
        "mapped_from": ["source fields"],
        "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted|calculated"}],
        "confidence": "high|medium|low"
      }
    },
    "balance_sheet_standards": {
      "assets": {
        "total_cash_equivalents": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_current_assets": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_fixed_assets": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_non_current_assets": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_assets": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        }
      },
      "liabilities": {
        "tax_liability": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_other_current_liabilities": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_current_liabilities": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_long_term_debt": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_non_current_liabilities": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_liabilities": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        }
      },
      "equity": {
        "retained_earnings": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "current_earnings": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "other_equity": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        },
        "total_equity": {
          "mapped_from": ["source fields"],
          "time_series": [{"period": "YYYY-MM", "value": number, "source": "extracted"}],
          "confidence": "high|medium|low"
        }
      }
    }
  },
  "legacy_normalized_time_series": {
    "description": "Maintained for backward compatibility",
    "revenue": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "gross_profit": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "expenses": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "net_profit": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "assets": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "liabilities": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "equity": [{"period": "YYYY-MM", "value": number, "source": "mapped_from_standards"}],
    "cash_flow": []
  },
  "basic_context": {
    "currency_detected": "AUD|USD|other",
    "business_indicators": ["industry clues from document"],
    "reporting_frequency": "monthly|quarterly|yearly",
    "latest_period": "YYYY-MM"
  },
  "processing_notes": "Explanation of extraction process, standard field mapping decisions, and any data quality issues encountered"
}

CRITICAL MAPPING INSTRUCTIONS:
1. **PRIORITIZE STANDARD FIELD MAPPING**: Focus effort on correctly identifying and mapping the 25 guaranteed fields
2. **PRESERVE ALL RAW DATA**: Never discard granular line items - they may be needed for cash flow reconstruction
3. **CONFIDENCE SCORING**: Rate mapping confidence based on how clearly the source field matches the standard
4. **FALLBACK CALCULATIONS**: If a standard field isn't directly available, calculate it from available components
5. **QUALITY FLAGS**: Flag any structural breaks, inconsistencies, or anomalies that could affect cash flow reconstruction
6. **MAINTAIN LEGACY**: Keep the old normalized_time_series structure for backward compatibility

VALIDATION REQUIREMENTS:
- Standard field coverage should be >80% for acceptable quality
- Balance sheet must validate: Assets = Liabilities + Equity
- P&L relationships must be logical: Revenue - Costs = Profit
- Time series should be complete with minimal gaps
- Flag any period-over-period changes >200% for investigation
""" + ENHANCED_JSON_OUTPUT_INSTRUCTIONS

# STAGE 2: Cash Flow Generation from Standard Fields  
STAGE2_CASH_FLOW_PROMPT = """
You are a cash flow reconstruction specialist with expertise in indirect method cash flow statement preparation and comprehensive financial analysis integration.

TASK: Generate complete historical cash flow statements from Stage 1 standard fields AND perform comprehensive business analysis to prepare for projections.

INPUT: $stage1_standard_field_data

INTEGRATED PROCESSING APPROACH:
This stage combines cash flow generation with business analysis to ensure NO DATA OR CONTEXT LOSS between stages. You will:

1. **RECONSTRUCT HISTORICAL CASH FLOWS** from the 25 standard fields
2. **ANALYZE BUSINESS PATTERNS** using both P&L, Balance Sheet, AND generated cash flows  
3. **PREPARE COMPREHENSIVE HANDOVER** with all insights, patterns, and recommendations for Stage 3

PART A: CASH FLOW GENERATION FROM STANDARD FIELDS

Use the INDIRECT METHOD to reconstruct historical cash flows from P&L and Balance Sheet standard fields:

OPERATING ACTIVITIES = Net Income + Non-cash Items ± Working Capital Changes
INVESTING ACTIVITIES = Capital Expenditures - Asset Disposals  
FINANCING ACTIVITIES = Debt Changes + Equity Changes - Dividends

DETAILED CALCULATION APPROACH:

1. **OPERATING CASH FLOW RECONSTRUCTION**:
   - Start with Net Income (from standard fields)
   - Add back Depreciation (estimated from Fixed Assets changes)
   - Calculate Working Capital Changes:
     * ΔWorking Capital = (ΔCurrent Assets - ΔCash) - ΔCurrent Liabilities
     * Use Total Current Assets, Total Cash & Equivalents, Total Current Liabilities

2. **INVESTING CASH FLOW RECONSTRUCTION**:
   - Calculate Capital Expenditures: ΔFixed Assets + Estimated Depreciation
   - Identify any asset disposals from negative capex periods

3. **FINANCING CASH FLOW RECONSTRUCTION**:  
   - Debt Changes: ΔTotal Long Term Debt
   - Equity Changes: ΔTotal Equity - ΔRetained Earnings from operations
   - Dividend Estimation: Net Income - ΔRetained Earnings

4. **CASH FLOW VALIDATION**:
   - Total Cash Flow = Operating + Investing + Financing
   - Must equal: ΔTotal Cash & Equivalents from Balance Sheet
   - Flag periods with variance >$1,000 for investigation

PART B: COMPREHENSIVE BUSINESS ANALYSIS WITH CASH FLOW INTEGRATION

Now perform complete business analysis using P&L, Balance Sheet, AND your generated cash flows:

1. **COMPREHENSIVE BUSINESS CONTEXT MODULE**
   - Industry Classification: Enhanced with cash flow pattern analysis
   - Business Stage Assessment: Include cash generation capability
   - Cash Flow Health: Assess cash generation vs. profitability alignment
   - Working Capital Management: Analyze actual patterns from reconstructed cash flows

2. **CASH FLOW PATTERN ANALYSIS**
   - Operating Cash Flow Consistency: Analyze CF vs. Net Income patterns
   - Working Capital Behavior: Calculate ACTUAL DSO, DPO, Cash Conversion Cycle
   - Capex Patterns: Identify maintenance vs. growth investment
   - Financing Patterns: Debt utilization, dividend policy consistency
   - Seasonal Cash Flow Effects: Identify cash flow seasonality vs. profit seasonality

3. **ENHANCED PATTERN RECOGNITION**
   - Include cash flow correlations in trend analysis
   - Cash-based ratios: OCF/Revenue, FCF/Net Income, ROIC
   - Cash flow sustainability: Can the business fund operations and growth?
   - Quality of earnings: How much of profit converts to cash?

4. **METHODOLOGY EXPERIMENTATION WITH CASH FLOW DATA**
   - Test forecasting methods on both profit and cash flow metrics
   - Evaluate methods based on cash flow predictability
   - Consider cash flow constraints in growth projections
   - Assess working capital optimization opportunities

5. **REAL WORKING CAPITAL DRIVER DEFINITION**
   - Calculate ACTUAL DSO from Accounts Receivable patterns (not assumed 45 days)
   - Calculate ACTUAL DPO from Accounts Payable patterns (not assumed 30 days)  
   - Determine ACTUAL Cash Conversion Cycle from historical data
   - Identify working capital optimization opportunities and timing

6. **DATA-BASED ASSUMPTION REQUIREMENTS**
   All assumptions must be based on ACTUAL historical patterns from your cash flow reconstruction:
   - ACTUAL DSO: "Historical average DSO is 52 days, project improvement to 45 days over 2 years"
   - ACTUAL Capex: "Historical capex averages 3.2% of revenue, expect this to continue"
   - ACTUAL Dividend Policy: "Company has paid average 35% of profits as dividends"
   - ACTUAL Working Capital: "Cash conversion cycle historically 67 days, target 55 days"

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this comprehensive structure:

{
  "stage2_processing_summary": {
    "cash_flow_generation_completed": true,
    "business_analysis_completed": true,
    "data_handover_prepared": true,
    "context_preservation_status": "complete"
  },
  "cash_flow_generation_results": {
    "method_used": "indirect_method_from_standard_fields",
    "depreciation_estimation": {
      "method": "percentage_of_fixed_assets|trend_analysis",
      "annual_rate_used": "percentage applied",
      "justification": "rationale for depreciation estimate"
    },
    "historical_cash_flows": [
      {
        "period": "YYYY-MM",
        "operating_activities": {
          "net_income": {
            "value": number,
            "source": "standard_field_net_income",
            "calculation_chain": "Direct mapping from P&L standard fields"
          },
          "depreciation_addback": {
            "value": number,
            "source": "estimated_from_fixed_assets",
            "calculation_chain": "Fixed Assets * Annual Depreciation Rate / 12"
          },
          "working_capital_changes": {
            "current_assets_ex_cash_change": {
              "value": number,
              "calculation_chain": "(Current Assets - Cash) Period N - (Current Assets - Cash) Period N-1"
            },
            "current_liabilities_change": {
              "value": number,
              "calculation_chain": "Current Liabilities Period N - Current Liabilities Period N-1"
            },
            "total_working_capital_change": {
              "value": number,
              "calculation_chain": "-(Current Assets Ex Cash Change - Current Liabilities Change)"
            }
          },
          "operating_cash_flow": {
            "value": number,
            "calculation_chain": "Net Income + Depreciation + Working Capital Change"
          }
        },
        "investing_activities": {
          "fixed_assets_change": {
            "value": number,
            "calculation_chain": "Fixed Assets Period N - Fixed Assets Period N-1"
          },
          "estimated_capex": {
            "value": number,
            "calculation_chain": "-(Fixed Assets Change + Depreciation)"
          },
          "investing_cash_flow": {
            "value": number,
            "calculation_chain": "Sum of investing activities"
          }
        },
        "financing_activities": {
          "debt_change": {
            "value": number,
            "calculation_chain": "Long Term Debt Period N - Long Term Debt Period N-1"
          },
          "equity_change_ex_earnings": {
            "value": number,
            "calculation_chain": "(Total Equity - Retained Earnings) Period N - (Total Equity - Retained Earnings) Period N-1"
          },
          "estimated_dividends": {
            "value": number,
            "calculation_chain": "Net Income - (Retained Earnings Period N - Retained Earnings Period N-1)"
          },
          "financing_cash_flow": {
            "value": number,
            "calculation_chain": "Debt Change + Equity Change - Estimated Dividends"
          }
        },
        "cash_flow_summary": {
          "total_cash_flow": {
            "value": number,
            "calculation_chain": "Operating CF + Investing CF + Financing CF"
          },
          "actual_cash_change": {
            "value": number,
            "calculation_chain": "Cash & Equivalents Period N - Cash & Equivalents Period N-1"
          },
          "variance": {
            "value": number,
            "calculation_chain": "Total Cash Flow - Actual Cash Change"
          },
          "variance_percentage": {
            "value": number,
            "calculation_chain": "Variance / Actual Cash Change * 100"
          },
          "validation_status": "PASS|WARNING|FAIL",
          "validation_threshold": "$1,000 or 5% of cash change"
        }
      }
    ],
    "cash_flow_quality_assessment": {
      "periods_validated": "number of periods with PASS status",
      "periods_with_warnings": "number of periods with WARNING status", 
      "periods_failed": "number of periods with FAIL status",
      "overall_validation_rate": "percentage of periods that passed validation",
      "major_variances": [
        {
          "period": "YYYY-MM",
          "variance_amount": number,
          "potential_causes": ["list of possible reasons for variance"],
          "investigation_recommended": true|false
        }
      ]
    }
  },
  "business_context": {
    "industry_classification": "detected industry with cash flow pattern evidence",
    "business_stage": "startup|growth|mature|decline",
    "market_geography": "Australian",
    "competitive_position": "market_leader|established|emerging|struggling",
    "business_model_type": "service|product|mixed|other",
    "cash_generation_capability": "strong|moderate|weak"
  },
  "contextual_analysis": {
    "maturity_assessment": {
      "revenue_stability": "high|medium|low",
      "growth_consistency": "stable|volatile|declining",
      "financial_health": "strong|moderate|weak",
      "cash_flow_consistency": "highly_consistent|moderately_consistent|inconsistent"
    },
    "seasonality_patterns": {
      "seasonal_detected": true|false,
      "peak_periods": ["list of peak months/quarters"],
      "trough_periods": ["list of low months/quarters"],
      "seasonal_amplitude": 0.0-1.0,
      "australian_fy_alignment": "strong|moderate|weak",
      "cash_flow_seasonality": "matches_profit|different_pattern|no_seasonality"
    },
    "anomaly_identification": [
      {"period": "YYYY-MM", "metric": "field", "anomaly_type": "spike|drop|inconsistency", "impact": "high|medium|low", "explanation": "rationale", "cash_flow_impact": "description"}
    ]
  },
  "cash_flow_integration_analysis": {
    "operating_cash_flow_quality": {
      "cf_to_net_income_ratio": "average ratio over historical periods",
      "consistency_score": "how consistent is OCF relative to profits", 
      "quality_assessment": "high|medium|low quality earnings",
      "seasonality_alignment": "does CF seasonality match profit seasonality"
    },
    "working_capital_analysis": {
      "calculated_dso": {
        "historical_average": "ACTUAL DSO calculated from data",
        "trend": "improving|stable|deteriorating",
        "target_opportunity": "recommended DSO target and timeline",
        "calculation_method": "methodology used to calculate DSO from cash flows"
      },
      "calculated_dpo": {
        "historical_average": "ACTUAL DPO calculated from data", 
        "trend": "improving|stable|deteriorating",
        "optimization_potential": "recommended DPO target and timeline",
        "calculation_method": "methodology used to calculate DPO from cash flows"
      },
      "cash_conversion_cycle": {
        "historical_average": "ACTUAL CCC calculated from data",
        "best_period": "best CCC achieved and when",
        "worst_period": "worst CCC and potential causes",
        "optimization_roadmap": "specific steps to improve CCC"
      }
    },
    "capex_analysis": {
      "maintenance_vs_growth": {
        "maintenance_capex_estimate": "percentage of revenue for maintenance",
        "growth_capex_periods": "periods where growth investments were made",
        "capex_efficiency": "revenue growth achieved per dollar of capex"
      },
      "depreciation_validation": {
        "estimated_vs_calculated": "how accurate was the depreciation estimate",
        "recommended_depreciation_rate": "optimal rate for future projections",
        "asset_life_implications": "typical asset life implied by depreciation"
      }
    },
    "financing_behavior_analysis": {
      "debt_utilization_patterns": "how and when does the business use debt",
      "equity_funding_history": "patterns of equity raises or contributions", 
      "dividend_policy_consistency": "actual dividend payout ratios and timing",
      "cash_retention_strategy": "how much cash does business typically hold"
    }
  },
  "pattern_analysis": {
    "growth_rates": {
      "revenue_cagr": number,
      "profit_cagr": number,
      "recent_growth_trend": "accelerating|stable|decelerating|declining",
      "cash_flow_growth_correlation": "how well does cash flow growth match profit growth"
    },
    "financial_ratios": {
      "profit_margin_trend": "improving|stable|declining",
      "roa_trend": "improving|stable|declining",
      "efficiency_indicators": {"trend": "improving|stable|declining", "current_level": "high|medium|low"},
      "cash_conversion_efficiency": "OCF/Net Income trend and current level"
    },
    "working_capital": {
      "trend": "improving|stable|deteriorating",
      "cash_conversion_cycle": "shortening|stable|lengthening",
      "working_capital_intensity": "percentage of revenue tied up in working capital"
    },
    "correlation_insights": [
      {"metrics": ["metric1", "metric2"], "correlation": number, "strength": "strong|moderate|weak", "business_meaning": "explanation", "cash_flow_relevance": "how this affects cash flow projections"}
    ],
    "volatility_assessment": {
      "revenue_volatility": "low|medium|high",
      "profit_volatility": "low|medium|high",
      "cash_flow_volatility": "low|medium|high",
      "overall_stability": "stable|moderate|volatile"
    }
  },
  "methodology_evaluation": {
    "methods_tested": [
      {
        "method": "ARIMA|Prophet|LinearRegression|ExponentialSmoothing|DriverBased",
        "evaluation_metrics": {"mape": number, "rmse": number, "r_squared": number},
        "suitability_score": 0.0-1.0,
        "strengths": ["list of advantages"],
        "limitations": ["list of constraints"],
        "cash_flow_compatibility": "how well does this method work with cash flow patterns"
      }
    ],
    "selected_method": {
      "primary_method": "method name",
      "rationale": "detailed explanation including cash flow considerations",
      "confidence_level": "high|medium|low",
      "fallback_method": "backup approach if primary fails"
    },
    "data_requirements": {
      "minimum_data_points": number,
      "data_quality_threshold": 0.0-1.0,
      "external_data_needed": true|false
    }
  },
  "comprehensive_forecast_drivers": {
    "revenue_drivers": [
      {
        "driver_name": "Primary revenue driver",
        "driver_type": "volume|price|mix|market_share",
        "baseline_value": "SPECIFIC VALUE from historical analysis including cash impact",
        "growth_assumptions": "SPECIFIC RATE based on historical trends and cash flow capacity",
        "seasonality_factors": "ACTUAL seasonal patterns from historical data",
        "cash_flow_constraints": "How cash flow patterns may limit revenue growth",
        "justification": "DATA-BASED rationale using historical P&L AND cash flow patterns"
      }
    ],
    "working_capital_drivers": {
      "accounts_receivable_management": {
        "historical_dso": "ACTUAL calculated DSO from cash flow analysis",
        "target_dso": "SPECIFIC improvement target and timeline",
        "collection_improvements": "SPECIFIC initiatives to improve collections",
        "bad_debt_assumptions": "ACTUAL historical bad debt rates",
        "justification": "Based on historical cash flow analysis"
      },
      "accounts_payable_optimization": {
        "historical_dpo": "ACTUAL calculated DPO from cash flow analysis", 
        "target_dpo": "SPECIFIC optimization target and approach",
        "supplier_negotiation_opportunities": "SPECIFIC DPO improvements available",
        "early_payment_discounts": "Analysis of discount opportunities",
        "justification": "Based on historical payment pattern analysis"
      },
      "cash_conversion_optimization": {
        "current_ccc": "ACTUAL historical cash conversion cycle from analysis",
        "target_ccc": "SPECIFIC improvement target over time",
        "improvement_roadmap": "Quarter-by-quarter improvement plan",
        "cash_flow_impact": "Projected cash flow improvement from CCC optimization",
        "justification": "Based on working capital component analysis"
      }
    },
    "capex_planning_drivers": {
      "maintenance_capex": {
        "historical_rate": "ACTUAL capex as % of revenue from cash flow analysis",
        "asset_replacement_schedule": "Based on depreciation analysis",
        "maintenance_requirements": "SPECIFIC maintenance capex needed",
        "justification": "Based on historical capex and depreciation patterns"
      },
      "growth_capex": {
        "growth_investment_history": "When and how much the business invested for growth",
        "capex_efficiency_analysis": "Historical revenue growth per dollar of capex",
        "future_growth_requirements": "SPECIFIC capex needed for projected growth",
        "timing_optimization": "Optimal timing of growth investments based on cash flow",
        "justification": "Based on historical relationship between capex and growth"
      }
    }
  },
  "cash_flow_based_assumptions": {
    "operating_cash_generation": {
      "ocf_margin_target": "ACTUAL historical OCF/Revenue ratio with improvement plan", 
      "working_capital_intensity": "ACTUAL working capital as % of revenue with optimization plan",
      "cash_generation_sustainability": "Assessment of sustainable cash generation capability"
    },
    "investment_capacity": {
      "self_funding_capability": "Can business fund growth from operations based on historical patterns?",
      "debt_capacity_analysis": "Debt servicing capability based on historical cash flows",
      "external_funding_requirements": "When and how much external funding needed"
    },
    "dividend_policy_assumptions": {
      "historical_payout_ratio": "ACTUAL dividend payout ratio from cash flow analysis",
      "sustainable_payout_ratio": "Recommended payout ratio based on cash generation",
      "dividend_growth_potential": "Can dividends grow with profits sustainably?"
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
      "industry_stability": "stable|moderate|volatile",
      "cash_flow_validation_rate": "percentage of periods that validated successfully"
    },
    "projection_confidence_by_horizon": {
      "1_year": "high|medium|low|very_low",
      "3_years": "high|medium|low|very_low",
      "5_years": "high|medium|low|very_low",
      "10_years": "high|medium|low|very_low",
      "15_years": "high|medium|low|very_low"
    }
  },
  "comprehensive_handover_to_stage3": {
    "complete_historical_dataset": {
      "pl_data_available": true,
      "bs_data_available": true,
      "cf_data_available": true,
      "all_standard_fields_mapped": "list of 25 fields status"
    },
    "validated_assumptions_ready": {
      "actual_dso_calculated": "specific DSO value and trend",
      "actual_dpo_calculated": "specific DPO value and trend", 
      "actual_ccc_calculated": "specific CCC value and optimization plan",
      "actual_capex_patterns": "specific capex rates and timing",
      "actual_dividend_policy": "specific payout ratios and timing"
    },
    "business_intelligence_complete": {
      "industry_classification_final": "definitive industry classification",
      "business_stage_assessment": "definitive stage with supporting evidence",
      "growth_capacity_analysis": "cash-flow constrained growth analysis",
      "risk_factors_identified": ["comprehensive risk assessment"],
      "opportunities_identified": ["specific improvement opportunities"]
    },
    "methodology_recommendations": {
      "primary_forecasting_method": "selected method with full justification",
      "scenario_planning_approach": "recommended scenario framework",
      "sensitivity_testing_priorities": ["key variables to test"],
      "validation_checkpoints": ["critical validation points for Stage 3"]
    },
    "data_quality_final_assessment": {
      "overall_data_quality_score": "final quality rating 0-100%",
      "cash_flow_reconstruction_success_rate": "percentage of periods validated",
      "standard_field_coverage_final": "percentage of 25 fields successfully mapped",
      "projection_readiness_status": "ready|needs_attention|insufficient_data"
    }
  },
  "key_assumptions": [
    "list of all critical assumptions with cash flow validation"
  ]
}

CRITICAL REQUIREMENTS FOR COMPLETE INTEGRATION:
1. **NO DATA LOSS**: All Stage 1 data must be preserved and enhanced with cash flow insights
2. **NO CONTEXT LOSS**: All business intelligence must be comprehensive and carried forward
3. **CASH FLOW FOUNDATION**: All assumptions must be based on reconstructed cash flow patterns
4. **REAL PATTERN FOCUS**: Replace all industry assumptions with ACTUAL calculated values
5. **COMPREHENSIVE HANDOVER**: Stage 3 must receive complete dataset with all insights and validated assumptions

This integrated approach ensures Stage 3 receives authentic, complete financial data with no loss of insights or context.
""" + ENHANCED_JSON_OUTPUT_INSTRUCTIONS

# STAGE 3: Comprehensive Business Analysis and Forecasting Methodology
STAGE3_ANALYSIS_PROMPT = """
You are a senior financial analyst and forecasting strategist with expertise in comprehensive business analysis and methodology selection.

TASK: Perform comprehensive business analysis using the complete financial dataset (P&L, Balance Sheet, and Cash Flows) from Stage 2 to prepare optimal forecasting strategy.

INPUT: $stage2_comprehensive_analysis_data

COMPREHENSIVE ANALYSIS FRAMEWORK:
You now have access to COMPLETE financial picture including validated historical cash flows and ACTUAL working capital patterns. Use this comprehensive dataset to perform deep business analysis.

CORE ANALYSIS MODULES:

1. **ADVANCED BUSINESS INTELLIGENCE**
   - Industry Classification Validation: Confirm industry using cash flow patterns
   - Competitive Position Assessment: Enhanced with cash generation analysis
   - Business Model Deep Dive: Cash flow characteristics by business model type
   - Market Position Validation: Cash sustainability analysis

2. **FINANCIAL PERFORMANCE DEEP ANALYSIS**
   - Quality of Earnings: OCF vs Net Income consistency analysis
   - Cash Generation Sustainability: Long-term cash generation capability
   - Working Capital Optimization: Detailed CCC improvement opportunities
   - Capital Efficiency: ROIC, ROCE, and cash-based returns analysis

3. **ADVANCED PATTERN RECOGNITION**
   - Multi-dimensional Correlation Analysis: Revenue, Profit, Cash Flow relationships
   - Seasonal Pattern Integration: Profit vs Cash Flow seasonality alignment
   - Growth Sustainability Analysis: Cash-constrained vs Unconstrained growth
   - Volatility Assessment: Risk-adjusted performance evaluation

4. **FORECASTING METHODOLOGY OPTIMIZATION**
   - Method Testing with Cash Flow Integration: Test methods on all three statements
   - Cash Flow Predictability Assessment: Which forecasting approaches work best for cash flows
   - Integrated Validation: Methods must work for P&L AND cash flows
   - Scenario Planning Framework: Multi-variable scenario construction

5. **STRATEGIC ASSUMPTION DEVELOPMENT**
   Build all assumptions on ACTUAL data from Stage 2 cash flow reconstruction:
   - **Revenue Growth Capacity**: Based on historical cash generation and reinvestment patterns
   - **Working Capital Strategy**: Based on ACTUAL DSO, DPO, CCC with specific improvement plans
   - **Capital Investment Planning**: Based on ACTUAL capex patterns and cash generation capacity
   - **Financing Strategy**: Based on ACTUAL debt utilization and dividend policy patterns

6. **INTEGRATED RISK ASSESSMENT**
   - Cash Flow Risk: Periods of cash stress and causes
   - Working Capital Risk: Cash conversion cycle volatility
   - Growth Risk: Cash flow constraints on expansion
   - Market Risk: Industry and competitive cash flow benchmarks

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this enhanced structure:

{
  "stage3_processing_summary": {
    "comprehensive_analysis_completed": true,
    "methodology_selection_completed": true,
    "assumptions_validated": true,
    "forecasting_strategy_prepared": true,
    "stage4_handover_ready": true
  },
  "advanced_business_intelligence": {
    "industry_classification_validated": {
      "final_industry": "definitive industry classification",
      "cash_flow_evidence": "how cash flows confirm industry classification",
      "peer_benchmarking_opportunities": "available industry comparisons",
      "industry_specific_risks": ["risks specific to this industry"]
    },
    "competitive_position_enhanced": {
      "market_position": "market_leader|established|emerging|struggling",
      "cash_generation_advantage": "competitive advantage from cash generation patterns",
      "market_share_sustainability": "can current market position be sustained with available cash?",
      "competitive_threats": ["threats to competitive position"]
    },
    "business_model_analysis": {
      "model_type_confirmed": "service|product|mixed|platform|other",
      "cash_flow_characteristics": "typical cash flow patterns for this business model",
      "scalability_assessment": "how scalable is this model based on cash patterns",
      "model_optimization_opportunities": ["business model improvement opportunities"]
    }
  },
  "financial_performance_deep_dive": {
    "quality_of_earnings_analysis": {
      "ocf_net_income_correlation": "statistical correlation between OCF and Net Income",
      "earnings_quality_score": "0-100 score based on cash conversion",
      "accounting_quality_indicators": ["red flags or positive indicators"],
      "earnings_sustainability": "sustainable|improving|deteriorating"
    },
    "cash_generation_sustainability": {
      "long_term_cash_generation_trend": "improving|stable|declining",
      "cash_generation_consistency": "coefficient of variation in OCF",
      "reinvestment_requirements": "cash required for maintaining current performance",
      "free_cash_flow_analysis": "after required reinvestment, available free cash flow"
    },
    "working_capital_optimization_detailed": {
      "current_efficiency_assessment": {
        "dso_efficiency": "current DSO vs industry benchmark",
        "dpo_efficiency": "current DPO vs optimization potential", 
        "inventory_efficiency": "if applicable, inventory turnover efficiency",
        "overall_ccc_efficiency": "current CCC vs optimized potential"
      },
      "optimization_roadmap": {
        "short_term_improvements": "0-12 months: specific initiatives",
        "medium_term_improvements": "1-3 years: strategic improvements",
        "long_term_optimization": "3+ years: fundamental process changes",
        "cash_flow_impact_projection": "projected cash flow improvement from optimization"
      }
    },
    "capital_efficiency_analysis": {
      "return_on_invested_capital": "ROIC calculation and trend",
      "cash_return_on_assets": "cash-based ROA calculation",
      "asset_utilization_efficiency": "how efficiently are assets generating cash",
      "capital_allocation_effectiveness": "how well is the business allocating capital"
    }
  },
  "advanced_pattern_recognition": {
    "multi_dimensional_correlations": [
      {
        "variables": ["revenue", "operating_cash_flow", "working_capital"],
        "correlation_strength": "statistical correlation coefficient",
        "business_interpretation": "what this correlation means for forecasting",
        "forecasting_implications": "how to use this correlation in projections"
      }
    ],
    "seasonal_pattern_integration": {
      "revenue_seasonality": "seasonal pattern in revenue",
      "cash_flow_seasonality": "seasonal pattern in cash flows",
      "seasonality_alignment": "do revenue and cash flow seasons align?",
      "working_capital_seasonality": "seasonal working capital requirements",
      "forecasting_implications": "how seasonality affects projections"
    },
    "growth_sustainability_analysis": {
      "historical_growth_vs_cash_generation": "could historical growth be funded internally?",
      "future_growth_constraints": "what growth rate can cash flows sustainably support?",
      "external_funding_requirements": "when and how much external funding needed for growth?",
      "sustainable_growth_rate": "calculated sustainable growth rate based on cash patterns"
    }
  },
  "methodology_optimization": {
    "integrated_method_testing": [
      {
        "method": "ARIMA|Prophet|LinearRegression|ExponentialSmoothing|DriverBased",
        "pl_performance": {"mape": number, "rmse": number, "r_squared": number},
        "cash_flow_performance": {"mape": number, "rmse": number, "r_squared": number},
        "integrated_score": "combined performance across all statements",
        "suitability_assessment": "how well does this method work for 3-way forecasting"
      }
    ],
    "optimal_methodology_selection": {
      "primary_method": "selected method with full justification",
      "method_customization": "how to customize method for this specific business",
      "validation_approach": "how to validate projections across all three statements",
      "scenario_planning_integration": "how to build scenarios with this method"
    },
    "forecasting_confidence_framework": {
      "confidence_drivers": ["factors that increase/decrease confidence"],
      "horizon_confidence_degradation": "how confidence changes over time horizons",
      "key_uncertainty_factors": ["main sources of forecast uncertainty"],
      "confidence_calibration": "how to calibrate confidence levels"
    }
  },
  "strategic_assumption_framework": {
    "revenue_growth_strategy": {
      "historical_growth_analysis": "detailed analysis of historical revenue growth patterns",
      "cash_flow_constrained_growth": "maximum growth rate supportable by internal cash generation",
      "market_opportunity_vs_cash_capacity": "market growth opportunities vs cash capacity to capture them",
      "specific_growth_assumptions": [
        {
          "assumption": "specific growth rate and pattern",
          "cash_flow_support": "how historical cash flows support this assumption",
          "risk_factors": "what could cause this assumption to fail",
          "validation_metrics": "how to track if assumption is playing out"
        }
      ]
    },
    "working_capital_strategy": {
      "current_state_assessment": "detailed current working capital efficiency",
      "optimization_initiatives": [
        {
          "initiative": "specific working capital improvement",
          "implementation_timeline": "when and how to implement",
          "cash_flow_impact": "projected cash flow improvement",
          "implementation_risk": "risk factors for this initiative"
        }
      ],
      "strategic_targets": {
        "target_dso": "specific DSO target with timeline",
        "target_dpo": "specific DPO target with timeline",
        "target_ccc": "specific Cash Conversion Cycle target",
        "overall_working_capital_strategy": "integrated working capital approach"
      }
    },
    "capital_investment_strategy": {
      "maintenance_capex_requirements": {
        "historical_maintenance_rate": "actual maintenance capex as % of revenue",
        "asset_replacement_schedule": "when major assets need replacement",
        "maintenance_capex_projection": "projected maintenance requirements"
      },
      "growth_investment_strategy": {
        "historical_growth_capex_efficiency": "revenue generated per dollar of growth capex",
        "future_growth_investment_requirements": "capex needed for projected growth",
        "investment_timing_optimization": "when to make growth investments for optimal cash flow"
      },
      "financing_strategy": {
        "self_funding_capacity": "what growth can be self-funded",
        "external_funding_requirements": "when and how much external funding needed",
        "debt_capacity_analysis": "debt capacity based on cash flow coverage"
      }
    }
  },
  "integrated_scenario_framework": {
    "scenario_construction_methodology": {
      "base_case_definition": "most likely scenario with probability assessment",
      "optimistic_scenario_drivers": "key variables that create upside scenarios",
      "conservative_scenario_drivers": "key variables that create downside scenarios",
      "stress_test_scenarios": "extreme scenarios for risk assessment"
    },
    "scenario_variable_relationships": [
      {
        "primary_variable": "key driver variable",
        "dependent_variables": "variables that move with primary",
        "correlation_assumptions": "how variables move together",
        "cash_flow_implications": "how scenario affects cash flows"
      }
    ],
    "scenario_probability_assessment": {
      "base_case_probability": "percentage probability",
      "optimistic_probability": "percentage probability", 
      "conservative_probability": "percentage probability",
      "probability_justification": "rationale for probability assignments"
    }
  },
  "risk_assessment_comprehensive": {
    "cash_flow_risks": [
      {
        "risk_factor": "specific cash flow risk",
        "probability": "likelihood of occurrence",
        "impact": "potential impact on cash flows",
        "mitigation_strategies": "how to mitigate this risk",
        "monitoring_indicators": "early warning signs"
      }
    ],
    "business_model_risks": [
      {
        "risk_factor": "business model vulnerability",
        "cash_flow_impact": "how this affects cash generation",
        "strategic_response": "strategic options to address risk"
      }
    ],
    "market_risks": [
      {
        "risk_factor": "market or competitive risk",
        "financial_impact": "impact on financial performance",
        "cash_flow_sensitivity": "how sensitive are cash flows to this risk"
      }
    ]
  },
  "stage4_handover_package": {
    "complete_dataset_ready": {
      "historical_pl_complete": true,
      "historical_bs_complete": true,
      "historical_cf_complete": true,
      "all_ratios_calculated": true,
      "all_patterns_identified": true
    },
    "validated_assumptions_ready": {
      "all_assumptions_data_based": true,
      "working_capital_assumptions_calculated": true,
      "growth_assumptions_cash_validated": true,
      "investment_assumptions_historical_based": true
    },
    "methodology_ready": {
      "optimal_method_selected": "method name",
      "method_parameters_defined": true,
      "validation_framework_prepared": true,
      "scenario_framework_ready": true
    },
    "business_intelligence_complete": {
      "industry_analysis_final": true,
      "competitive_position_final": true,
      "business_model_analysis_final": true,
      "risk_assessment_complete": true
    },
    "projection_requirements_defined": {
      "time_horizons_specified": ["1_year", "3_years", "5_years", "10_years", "15_years"],
      "granularity_requirements": "monthly/quarterly/yearly by horizon",
      "validation_requirements": "3-way integration requirements",
      "quality_standards": "minimum quality thresholds"
    }
  },
  "key_insights_summary": [
    "Top 5-7 key insights that will drive projection accuracy"
  ]
}

CRITICAL REQUIREMENTS FOR STAGE 3:
1. **COMPREHENSIVE ANALYSIS**: Use all available data from P&L, Balance Sheet, and Cash Flows
2. **DATA-DRIVEN ASSUMPTIONS**: Every assumption must be based on actual historical patterns
3. **INTEGRATED METHODOLOGY**: Selected method must work for all three financial statements
4. **CASH FLOW FOCUS**: All analysis must consider cash flow implications
5. **COMPLETE HANDOVER**: Stage 4 must receive everything needed for accurate projections
6. **NO CONTEXT LOSS**: All insights, patterns, and intelligence must be preserved

This comprehensive analysis ensures Stage 4 has everything needed for authentic, integrated 3-way forecasting.
""" + ENHANCED_JSON_OUTPUT_INSTRUCTIONS

# STAGE 4: Enhanced Projection Engine with Complete Data Requirements
STAGE4_PROJECTION_PROMPT = """
You are a financial forecasting expert creating comprehensive 3-way financial projections.

INPUT ANALYSIS: $stage3_comprehensive_business_analysis

CRITICAL REQUIREMENT: Generate complete financial projections for ALL time horizons with specific data points.

YOU MUST GENERATE ALL FOUR FINANCIAL METRICS FOR ALL FIVE TIME HORIZONS:
- Revenue data for all time periods
- Expenses data for all time periods  
- Gross Profit data for all time periods
- Net Profit data for all time periods

TIME HORIZONS REQUIRED:
1. 1 year ahead (monthly data - 12 data points)
2. 3 years ahead (quarterly data - 12 data points) 
3. 5 years ahead (yearly data - 5 data points)
4. 10 years ahead (yearly data - 10 data points)
5. 15 years ahead (yearly data - 15 data points)

MANDATORY JSON STRUCTURE - MUST INCLUDE ALL SECTIONS:

{
  "projection_methodology": {
    "primary_method_applied": "method_name",
    "method_adjustments": ["specific adjustments made"],
    "integration_approach": "how data was integrated",
    "validation_approach": "validation methods used"
  },
  "base_case_projections": {
    "1_year_ahead": {
      "period_label": "FY2026",
      "granularity": "monthly", 
      "data_points": 12,
      "revenue": [
        {"period": "2026-01", "value": 125000, "confidence": "high"},
        {"period": "2026-02", "value": 127500, "confidence": "high"},
        {"period": "2026-03", "value": 130000, "confidence": "high"},
        {"period": "2026-04", "value": 132500, "confidence": "high"},
        {"period": "2026-05", "value": 135000, "confidence": "high"},
        {"period": "2026-06", "value": 137500, "confidence": "high"},
        {"period": "2026-07", "value": 140000, "confidence": "high"},
        {"period": "2026-08", "value": 142500, "confidence": "high"},
        {"period": "2026-09", "value": 145000, "confidence": "high"},
        {"period": "2026-10", "value": 147500, "confidence": "high"},
        {"period": "2026-11", "value": 150000, "confidence": "high"},
        {"period": "2026-12", "value": 152500, "confidence": "high"}
      ],
      "expenses": [
        {"period": "2026-01", "value": 75000, "confidence": "high"},
        {"period": "2026-02", "value": 76500, "confidence": "high"},
        {"period": "2026-03", "value": 78000, "confidence": "high"},
        {"period": "2026-04", "value": 79500, "confidence": "high"},
        {"period": "2026-05", "value": 81000, "confidence": "high"},
        {"period": "2026-06", "value": 82500, "confidence": "high"},
        {"period": "2026-07", "value": 84000, "confidence": "high"},
        {"period": "2026-08", "value": 85500, "confidence": "high"},
        {"period": "2026-09", "value": 87000, "confidence": "high"},
        {"period": "2026-10", "value": 88500, "confidence": "high"},
        {"period": "2026-11", "value": 90000, "confidence": "high"},
        {"period": "2026-12", "value": 91500, "confidence": "high"}
      ],
      "gross_profit": [
        {"period": "2026-01", "value": 50000, "confidence": "high"},
        {"period": "2026-02", "value": 51000, "confidence": "high"},
        {"period": "2026-03", "value": 52000, "confidence": "high"},
        {"period": "2026-04", "value": 53000, "confidence": "high"},
        {"period": "2026-05", "value": 54000, "confidence": "high"},
        {"period": "2026-06", "value": 55000, "confidence": "high"},
        {"period": "2026-07", "value": 56000, "confidence": "high"},
        {"period": "2026-08", "value": 57000, "confidence": "high"},
        {"period": "2026-09", "value": 58000, "confidence": "high"},
        {"period": "2026-10", "value": 59000, "confidence": "high"},
        {"period": "2026-11", "value": 60000, "confidence": "high"},
        {"period": "2026-12", "value": 61000, "confidence": "high"}
      ],
      "net_profit": [
        {"period": "2026-01", "value": 35000, "confidence": "high"},
        {"period": "2026-02", "value": 35700, "confidence": "high"},
        {"period": "2026-03", "value": 36400, "confidence": "high"},
        {"period": "2026-04", "value": 37100, "confidence": "high"},
        {"period": "2026-05", "value": 37800, "confidence": "high"},
        {"period": "2026-06", "value": 38500, "confidence": "high"},
        {"period": "2026-07", "value": 39200, "confidence": "high"},
        {"period": "2026-08", "value": 39900, "confidence": "high"},
        {"period": "2026-09", "value": 40600, "confidence": "high"},
        {"period": "2026-10", "value": 41300, "confidence": "high"},
        {"period": "2026-11", "value": 42000, "confidence": "high"},
        {"period": "2026-12", "value": 42700, "confidence": "high"}
      ]
    },
    "3_years_ahead": {
      "period_label": "FY2026-FY2028",
      "granularity": "quarterly",
      "data_points": 12,
      "revenue": [
        {"period": "2026-Q1", "value": 375000, "confidence": "medium"},
        {"period": "2026-Q2", "value": 382500, "confidence": "medium"},
        {"period": "2026-Q3", "value": 390000, "confidence": "medium"},
        {"period": "2026-Q4", "value": 397500, "confidence": "medium"},
        {"period": "2027-Q1", "value": 405000, "confidence": "medium"},
        {"period": "2027-Q2", "value": 412500, "confidence": "medium"},
        {"period": "2027-Q3", "value": 420000, "confidence": "medium"},
        {"period": "2027-Q4", "value": 427500, "confidence": "medium"},
        {"period": "2028-Q1", "value": 435000, "confidence": "medium"},
        {"period": "2028-Q2", "value": 442500, "confidence": "medium"},
        {"period": "2028-Q3", "value": 450000, "confidence": "medium"},
        {"period": "2028-Q4", "value": 457500, "confidence": "medium"}
      ],
      "expenses": [
        {"period": "2026-Q1", "value": 225000, "confidence": "medium"},
        {"period": "2026-Q2", "value": 229500, "confidence": "medium"},
        {"period": "2026-Q3", "value": 234000, "confidence": "medium"},
        {"period": "2026-Q4", "value": 238500, "confidence": "medium"},
        {"period": "2027-Q1", "value": 243000, "confidence": "medium"},
        {"period": "2027-Q2", "value": 247500, "confidence": "medium"},
        {"period": "2027-Q3", "value": 252000, "confidence": "medium"},
        {"period": "2027-Q4", "value": 256500, "confidence": "medium"},
        {"period": "2028-Q1", "value": 261000, "confidence": "medium"},
        {"period": "2028-Q2", "value": 265500, "confidence": "medium"},
        {"period": "2028-Q3", "value": 270000, "confidence": "medium"},
        {"period": "2028-Q4", "value": 274500, "confidence": "medium"}
      ],
      "gross_profit": [
        {"period": "2026-Q1", "value": 150000, "confidence": "medium"},
        {"period": "2026-Q2", "value": 153000, "confidence": "medium"},
        {"period": "2026-Q3", "value": 156000, "confidence": "medium"},
        {"period": "2026-Q4", "value": 159000, "confidence": "medium"},
        {"period": "2027-Q1", "value": 162000, "confidence": "medium"},
        {"period": "2027-Q2", "value": 165000, "confidence": "medium"},
        {"period": "2027-Q3", "value": 168000, "confidence": "medium"},
        {"period": "2027-Q4", "value": 171000, "confidence": "medium"},
        {"period": "2028-Q1", "value": 174000, "confidence": "medium"},
        {"period": "2028-Q2", "value": 177000, "confidence": "medium"},
        {"period": "2028-Q3", "value": 180000, "confidence": "medium"},
        {"period": "2028-Q4", "value": 183000, "confidence": "medium"}
      ],
      "net_profit": [
        {"period": "2026-Q1", "value": 105000, "confidence": "medium"},
        {"period": "2026-Q2", "value": 107100, "confidence": "medium"},
        {"period": "2026-Q3", "value": 109200, "confidence": "medium"},
        {"period": "2026-Q4", "value": 111300, "confidence": "medium"},
        {"period": "2027-Q1", "value": 113400, "confidence": "medium"},
        {"period": "2027-Q2", "value": 115500, "confidence": "medium"},
        {"period": "2027-Q3", "value": 117600, "confidence": "medium"},
        {"period": "2027-Q4", "value": 119700, "confidence": "medium"},
        {"period": "2028-Q1", "value": 121800, "confidence": "medium"},
        {"period": "2028-Q2", "value": 123900, "confidence": "medium"},
        {"period": "2028-Q3", "value": 126000, "confidence": "medium"},
        {"period": "2028-Q4", "value": 128100, "confidence": "medium"}
      ]
    },
    "5_years_ahead": {
      "period_label": "FY2026-FY2030", 
      "granularity": "yearly",
      "data_points": 5,
      "revenue": [
        {"period": "2026", "value": 1500000, "confidence": "medium"},
        {"period": "2027", "value": 1545000, "confidence": "medium"},
        {"period": "2028", "value": 1591350, "confidence": "low"},
        {"period": "2029", "value": 1639091, "confidence": "low"},
        {"period": "2030", "value": 1688263, "confidence": "low"}
      ],
      "expenses": [
        {"period": "2026", "value": 900000, "confidence": "medium"},
        {"period": "2027", "value": 927000, "confidence": "medium"},
        {"period": "2028", "value": 954810, "confidence": "low"},
        {"period": "2029", "value": 983454, "confidence": "low"},
        {"period": "2030", "value": 1012958, "confidence": "low"}
      ],
      "gross_profit": [
        {"period": "2026", "value": 600000, "confidence": "medium"},
        {"period": "2027", "value": 618000, "confidence": "medium"},
        {"period": "2028", "value": 636540, "confidence": "low"},
        {"period": "2029", "value": 655636, "confidence": "low"},
        {"period": "2030", "value": 675305, "confidence": "low"}
      ],
      "net_profit": [
        {"period": "2026", "value": 420000, "confidence": "medium"},
        {"period": "2027", "value": 432600, "confidence": "medium"},
        {"period": "2028", "value": 445578, "confidence": "low"},
        {"period": "2029", "value": 458945, "confidence": "low"},
        {"period": "2030", "value": 472714, "confidence": "low"}
      ]
    },
    "10_years_ahead": {
      "period_label": "FY2026-FY2035",
      "granularity": "yearly", 
      "data_points": 10,
      "revenue": [
        {"period": "2026", "value": 1500000, "confidence": "low"},
        {"period": "2027", "value": 1545000, "confidence": "low"},
        {"period": "2028", "value": 1591350, "confidence": "low"},
        {"period": "2029", "value": 1639091, "confidence": "very_low"},
        {"period": "2030", "value": 1688263, "confidence": "very_low"},
        {"period": "2031", "value": 1738911, "confidence": "very_low"},
        {"period": "2032", "value": 1791078, "confidence": "very_low"},
        {"period": "2033", "value": 1844810, "confidence": "very_low"},
        {"period": "2034", "value": 1900154, "confidence": "very_low"},
        {"period": "2035", "value": 1957159, "confidence": "very_low"}
      ],
      "expenses": [
        {"period": "2026", "value": 900000, "confidence": "low"},
        {"period": "2027", "value": 927000, "confidence": "low"},
        {"period": "2028", "value": 954810, "confidence": "low"},
        {"period": "2029", "value": 983454, "confidence": "very_low"},
        {"period": "2030", "value": 1012958, "confidence": "very_low"},
        {"period": "2031", "value": 1043346, "confidence": "very_low"},
        {"period": "2032", "value": 1074647, "confidence": "very_low"},
        {"period": "2033", "value": 1106886, "confidence": "very_low"},
        {"period": "2034", "value": 1140092, "confidence": "very_low"},
        {"period": "2035", "value": 1174295, "confidence": "very_low"}
      ],
      "gross_profit": [
        {"period": "2026", "value": 600000, "confidence": "low"},
        {"period": "2027", "value": 618000, "confidence": "low"},
        {"period": "2028", "value": 636540, "confidence": "low"},
        {"period": "2029", "value": 655636, "confidence": "very_low"},
        {"period": "2030", "value": 675305, "confidence": "very_low"},
        {"period": "2031", "value": 695565, "confidence": "very_low"},
        {"period": "2032", "value": 716432, "confidence": "very_low"},
        {"period": "2033", "value": 737925, "confidence": "very_low"},
        {"period": "2034", "value": 760062, "confidence": "very_low"},
        {"period": "2035", "value": 782864, "confidence": "very_low"}
      ],
      "net_profit": [
        {"period": "2026", "value": 420000, "confidence": "low"},
        {"period": "2027", "value": 432600, "confidence": "low"},
        {"period": "2028", "value": 445578, "confidence": "low"},
        {"period": "2029", "value": 458945, "confidence": "very_low"},
        {"period": "2030", "value": 472714, "confidence": "very_low"},
        {"period": "2031", "value": 486895, "confidence": "very_low"},
        {"period": "2032", "value": 501502, "confidence": "very_low"},
        {"period": "2033", "value": 516547, "confidence": "very_low"},
        {"period": "2034", "value": 532043, "confidence": "very_low"},
        {"period": "2035", "value": 548005, "confidence": "very_low"}
      ]
    },
    "15_years_ahead": {
      "period_label": "FY2026-FY2040",
      "granularity": "yearly",
      "data_points": 15, 
      "revenue": [
        {"period": "2026", "value": 1500000, "confidence": "very_low"},
        {"period": "2027", "value": 1545000, "confidence": "very_low"},
        {"period": "2028", "value": 1591350, "confidence": "very_low"},
        {"period": "2029", "value": 1639091, "confidence": "very_low"},
        {"period": "2030", "value": 1688263, "confidence": "very_low"},
        {"period": "2031", "value": 1738911, "confidence": "very_low"},
        {"period": "2032", "value": 1791078, "confidence": "very_low"},
        {"period": "2033", "value": 1844810, "confidence": "very_low"},
        {"period": "2034", "value": 1900154, "confidence": "very_low"},
        {"period": "2035", "value": 1957159, "confidence": "very_low"},
        {"period": "2036", "value": 2015874, "confidence": "very_low"},
        {"period": "2037", "value": 2076350, "confidence": "very_low"},
        {"period": "2038", "value": 2138641, "confidence": "very_low"},
        {"period": "2039", "value": 2202800, "confidence": "very_low"},
        {"period": "2040", "value": 2268884, "confidence": "very_low"}
      ],
      "expenses": [
        {"period": "2026", "value": 900000, "confidence": "very_low"},
        {"period": "2027", "value": 927000, "confidence": "very_low"},
        {"period": "2028", "value": 954810, "confidence": "very_low"},
        {"period": "2029", "value": 983454, "confidence": "very_low"},
        {"period": "2030", "value": 1012958, "confidence": "very_low"},
        {"period": "2031", "value": 1043346, "confidence": "very_low"},
        {"period": "2032", "value": 1074647, "confidence": "very_low"},
        {"period": "2033", "value": 1106886, "confidence": "very_low"},
        {"period": "2034", "value": 1140092, "confidence": "very_low"},
        {"period": "2035", "value": 1174295, "confidence": "very_low"},
        {"period": "2036", "value": 1209524, "confidence": "very_low"},
        {"period": "2037", "value": 1245810, "confidence": "very_low"},
        {"period": "2038", "value": 1283184, "confidence": "very_low"},
        {"period": "2039", "value": 1321679, "confidence": "very_low"},
        {"period": "2040", "value": 1361329, "confidence": "very_low"}
      ],
      "gross_profit": [
        {"period": "2026", "value": 600000, "confidence": "very_low"},
        {"period": "2027", "value": 618000, "confidence": "very_low"},
        {"period": "2028", "value": 636540, "confidence": "very_low"},
        {"period": "2029", "value": 655636, "confidence": "very_low"},
        {"period": "2030", "value": 675305, "confidence": "very_low"},
        {"period": "2031", "value": 695565, "confidence": "very_low"},
        {"period": "2032", "value": 716432, "confidence": "very_low"},
        {"period": "2033", "value": 737925, "confidence": "very_low"},
        {"period": "2034", "value": 760062, "confidence": "very_low"},
        {"period": "2035", "value": 782864, "confidence": "very_low"},
        {"period": "2036", "value": 806350, "confidence": "very_low"},
        {"period": "2037", "value": 830541, "confidence": "very_low"},
        {"period": "2038", "value": 855457, "confidence": "very_low"},
        {"period": "2039", "value": 881121, "confidence": "very_low"},
        {"period": "2040", "value": 907555, "confidence": "very_low"}
      ],
      "net_profit": [
        {"period": "2026", "value": 420000, "confidence": "very_low"},
        {"period": "2027", "value": 432600, "confidence": "very_low"},
        {"period": "2028", "value": 445578, "confidence": "very_low"},
        {"period": "2029", "value": 458945, "confidence": "very_low"},
        {"period": "2030", "value": 472714, "confidence": "very_low"},
        {"period": "2031", "value": 486895, "confidence": "very_low"},
        {"period": "2032", "value": 501502, "confidence": "very_low"},
        {"period": "2033", "value": 516547, "confidence": "very_low"},
        {"period": "2034", "value": 532043, "confidence": "very_low"},
        {"period": "2035", "value": 548005, "confidence": "very_low"},
        {"period": "2036", "value": 564445, "confidence": "very_low"},
        {"period": "2037", "value": 581378, "confidence": "very_low"},
        {"period": "2038", "value": 598820, "confidence": "very_low"},
        {"period": "2039", "value": 616785, "confidence": "very_low"},
        {"period": "2040", "value": 635289, "confidence": "very_low"}
      ]
    }
  },
  "scenario_projections": {
    "optimistic": {
      "description": "Best case scenario with enhanced growth",
      "key_drivers": ["improved working capital management", "market expansion"],
      "growth_multipliers": {
        "1_year": 1.2,
        "3_years": 1.3,
        "5_years": 1.4,
        "10_years": 1.5,
        "15_years": 1.6
      }
    },
    "conservative": {
      "description": "Conservative scenario with reduced growth",
      "key_drivers": ["market uncertainty", "operational constraints"],
      "growth_multipliers": {
        "1_year": 0.8,
        "3_years": 0.7,
        "5_years": 0.6,
        "10_years": 0.5,
        "15_years": 0.4
      }
    }
  },
  "assumption_documentation": {
    "critical_assumptions": [
      {
        "assumption": "Revenue stabilizes at $1.5M baseline with 3% annual growth",
        "rationale": "Based on Stage 3 business restructuring analysis",
        "sensitivity": "high",
        "override_capability": true
      }
    ]
  },
  "executive_summary": "Comprehensive financial projections based on Stage 3 analysis showing projected revenue, expenses, gross profit, and net profit across all required time horizons."
}

CRITICAL INSTRUCTIONS:
1. Generate COMPLETE data for all 4 metrics (Revenue, Expenses, Gross Profit, Net Profit)
2. Include ALL 5 time horizons (1, 3, 5, 10, 15 years)
3. Use ACTUAL data points as specified (12 monthly, 12 quarterly, 5/10/15 yearly)
4. Ensure mathematical consistency (Revenue - Expenses = Gross Profit, etc.)
5. Apply appropriate confidence levels (high/medium/low/very_low by horizon)

DO NOT generate only assumptions - you MUST generate the complete base_case_projections structure with all financial data.

""" + ENHANCED_JSON_OUTPUT_INSTRUCTIONS