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

# Comprehensive Multi-PDF analysis prompt with methodology transparency
MULTI_PDF_PROMPT = """
ROLE
You are a senior financial analyst and data scientist with expertise in trend analysis, forecasting, and model transparency.

TASK
1. Parse **all attached PDFs** (financial statements).  
2. Detect the optimal time-period granularity and latest period found.  
3. Produce an **auditable forecast JSON** with complete methodology documentation.

CRITICAL CONSTRAINTS
• **Automatic base-period detection** – never assume today's date.  
• Use Australian FY (July 1 – June 30) when generating FY labels.  
• Pick forecasting granularity using this hierarchy:
  – ≥12 monthly points → monthly  
  – ≥6 quarterly points → quarterly  
  – else yearly  
• Document ALL methodology decisions transparently.
• **METHODOLOGY MUST BE AN OBJECT** – Never return methodology as a string. Always use the structured object format with model_chosen, model_justification, preprocessing_steps, etc.
• Output *only* valid JSON. Do not wrap in markdown.

MANDATORY FINANCIAL METRICS SCHEMA ENFORCEMENT
**ALL PROJECTION PERIODS MUST INCLUDE THESE FOUR FINANCIAL METRICS:**
1. **revenue** - MANDATORY in every projection period
2. **gross_profit** - MANDATORY in every projection period  
3. **expenses** - MANDATORY in every projection period
4. **net_profit** - MANDATORY in every projection period

**INCOMPLETE PROJECTIONS ARE INVALID** - Missing any of these four metrics will result in frontend display errors.
**VALIDATION CHECK** - Before outputting, verify that every projection period (1_year_ahead, 3_years_ahead, 5_years_ahead, 10_years_ahead, 15_years_ahead) contains all four metrics with complete data points.

OUTPUT FORMAT
{{
  "summary": "<150-word plain-English overview of findings, methodology, and key insights>",
  "data_analysis_summary": {{
    "period_granularity_detected": "monthly|quarterly|yearly|mixed",
    "total_data_points": 24,
    "time_span": "January 2022 to December 2023",
    "data_completeness": "complete|partial|sparse",
    "optimal_forecast_horizon": "2-3 years",
    "seasonality_detected": true,
    "rationale": "Monthly data provides 24 data points enabling robust seasonality analysis and trend detection"
  }},
  "extracted_data": [
    {{
      "source_document": "filename.pdf",
      "period_range": "2023-01 to 2023-12 (monthly) | 2023 (annual) | 2023-Q1 to 2023-Q4 (quarterly)",
      "granularity": "monthly|quarterly|yearly",
      "financial_statements": {{
        "income_statement": {{ 
          "revenue": [
            {{"period": "2023-01", "value": 150000}},
            {{"period": "2023-02", "value": 145000}}
          ],
          "expenses": [
            {{"period": "2023-01", "value": 120000}},
            {{"period": "2023-02", "value": 118000}}
          ],
          "net_income": [
            {{"period": "2023-01", "value": 30000}},
            {{"period": "2023-02", "value": 27000}}
          ]
        }},
        "balance_sheet": {{ 
          "assets": [{{"period": "2023-01", "value": 2000000}}],
          "liabilities": [{{"period": "2023-01", "value": 1200000}}],
          "equity": [{{"period": "2023-01", "value": 800000}}]
        }},
        "cash_flow": {{}}
      }},
      "key_metrics": {{}}
    }}
  ],
  "normalized_data": {{
    "period_metadata": {{
      "granularity_used": "monthly",
      "period_format": "YYYY-MM",
      "total_periods": 24,
      "date_range": {{
        "start": "2022-01",
        "end": "2023-12"
      }},
      "data_gaps": ["2022-06", "2022-07"],
      "interpolation_used": false
    }},
    "time_series": {{
      "revenue": [
        {{"period": "2022-01", "value": 140000, "data_source": "extracted"}},
        {{"period": "2022-02", "value": 135000, "data_source": "extracted"}},
        {{"period": "2022-06", "value": null, "data_source": "missing"}}
      ],
      "expenses": [
        {{"period": "2022-01", "value": 115000, "data_source": "extracted"}},
        {{"period": "2022-02", "value": 112000, "data_source": "extracted"}}
      ],
      "net_profit": [
        {{"period": "2022-01", "value": 25000, "data_source": "calculated"}},
        {{"period": "2022-02", "value": 23000, "data_source": "calculated"}}
      ],
      "assets": [
        {{"period": "2022-01", "value": 1950000, "data_source": "extracted"}},
        {{"period": "2022-02", "value": 1965000, "data_source": "extracted"}}
      ],
      "liabilities": [
        {{"period": "2022-01", "value": 1180000, "data_source": "extracted"}}
      ],
      "equity": [
        {{"period": "2022-01", "value": 770000, "data_source": "calculated"}}
      ]
    }},
    "seasonality_analysis": {{
      "seasonal_patterns_detected": true,
      "peak_months": ["November", "December"],
      "trough_months": ["January", "February"],
      "seasonal_amplitude": 0.15,
      "deseasonalized_trend": "positive_growth"
    }},
    "growth_rates": {{
      "revenue_monthly_avg": 0.025,
      "revenue_cagr": 0.18,
      "expense_growth_monthly": 0.020,
      "profit_growth_monthly": 0.035,
      "volatility_metrics": {{
        "revenue_std": 8500,
        "profit_std": 3200
      }}
    }},
    "financial_ratios": {{
      "profit_margin": [
        {{"period": "2022-01", "value": 0.179, "data_source": "calculated"}},
        {{"period": "2022-02", "value": 0.170, "data_source": "calculated"}}
      ],
      "roa": [
        {{"period": "2022-01", "value": 0.013, "data_source": "calculated"}}
      ],
      "current_ratio": [
        {{"period": "2022-01", "value": 1.48, "data_source": "calculated"}}
      ]
    }}
  }},
  "projections": {{
    "methodology": "Time series analysis with seasonal decomposition using available data points",
    "base_period_detection": "CRITICAL: Automatically detect the latest/most recent period in the actual data",
    "australian_fy_note": "Australian Financial Year runs from July 1 to June 30. FY2025 = July 1, 2024 to June 30, 2025",
    "projection_intervals": "Fixed intervals: 1, 3, 5, 10, and 15 years ahead from the DETECTED latest data period",
    "base_period": "DETECT FROM DATA: Find the latest period in your extracted data and use that as the current period",
    "projection_logic": "If latest data is June 2025 (end of FY2025), then 1 year ahead = FY2026, 3 years = FY2028, etc.",
    
    "_SCHEMA_VALIDATION": "BEFORE OUTPUTTING: Verify that EVERY projection period below contains all four metrics: revenue, gross_profit, expenses, net_profit",
    
    "specific_projections": {{
      "1_year_ahead": {{
        "period": "CALCULATE: Latest data period + 1 Australian FY",
        "granularity": "monthly",
        "data_points": 12,
        "_REQUIRED_METRICS": "ALL FOUR MUST BE PRESENT: revenue, gross_profit, expenses, net_profit",
        "revenue": [
          {{"period": "Month 1", "value": 175000, "confidence": "high"}},
          {{"period": "Month 2", "value": 180000, "confidence": "high"}},
          {{"period": "Month 3", "value": 178000, "confidence": "high"}},
          {{"period": "Month 4", "value": 182000, "confidence": "high"}},
          {{"period": "Month 5", "value": 185000, "confidence": "high"}},
          {{"period": "Month 6", "value": 190000, "confidence": "high"}},
          {{"period": "Month 7", "value": 188000, "confidence": "high"}},
          {{"period": "Month 8", "value": 192000, "confidence": "high"}},
          {{"period": "Month 9", "value": 195000, "confidence": "high"}},
          {{"period": "Month 10", "value": 200000, "confidence": "high"}},
          {{"period": "Month 11", "value": 198000, "confidence": "high"}},
          {{"period": "Month 12", "value": 202000, "confidence": "high"}}
        ],
        "gross_profit": [
          {{"period": "Month 1", "value": 70000, "confidence": "high"}},
          {{"period": "Month 2", "value": 72000, "confidence": "high"}},
          {{"period": "Month 3", "value": 71200, "confidence": "high"}},
          {{"period": "Month 4", "value": 72800, "confidence": "high"}},
          {{"period": "Month 5", "value": 74000, "confidence": "high"}},
          {{"period": "Month 6", "value": 76000, "confidence": "high"}},
          {{"period": "Month 7", "value": 75200, "confidence": "high"}},
          {{"period": "Month 8", "value": 76800, "confidence": "high"}},
          {{"period": "Month 9", "value": 78000, "confidence": "high"}},
          {{"period": "Month 10", "value": 80000, "confidence": "high"}},
          {{"period": "Month 11", "value": 79200, "confidence": "high"}},
          {{"period": "Month 12", "value": 80800, "confidence": "high"}}
        ],
        "expenses": [
          {{"period": "Month 1", "value": 135000, "confidence": "high"}},
          {{"period": "Month 2", "value": 138000, "confidence": "high"}},
          {{"period": "Month 3", "value": 136500, "confidence": "high"}},
          {{"period": "Month 4", "value": 139500, "confidence": "high"}},
          {{"period": "Month 5", "value": 142000, "confidence": "high"}},
          {{"period": "Month 6", "value": 145000, "confidence": "high"}},
          {{"period": "Month 7", "value": 143500, "confidence": "high"}},
          {{"period": "Month 8", "value": 146500, "confidence": "high"}},
          {{"period": "Month 9", "value": 149000, "confidence": "high"}},
          {{"period": "Month 10", "value": 152000, "confidence": "high"}},
          {{"period": "Month 11", "value": 150500, "confidence": "high"}},
          {{"period": "Month 12", "value": 153500, "confidence": "high"}}
        ],
        "net_profit": [
          {{"period": "Month 1", "value": 40000, "confidence": "high"}},
          {{"period": "Month 2", "value": 42000, "confidence": "high"}},
          {{"period": "Month 3", "value": 41500, "confidence": "high"}},
          {{"period": "Month 4", "value": 42500, "confidence": "high"}},
          {{"period": "Month 5", "value": 43000, "confidence": "high"}},
          {{"period": "Month 6", "value": 45000, "confidence": "high"}},
          {{"period": "Month 7", "value": 44500, "confidence": "high"}},
          {{"period": "Month 8", "value": 45500, "confidence": "high"}},
          {{"period": "Month 9", "value": 46000, "confidence": "high"}},
          {{"period": "Month 10", "value": 48000, "confidence": "high"}},
          {{"period": "Month 11", "value": 47500, "confidence": "high"}},
          {{"period": "Month 12", "value": 48500, "confidence": "high"}}
        ]
      }},
      "3_years_ahead": {{
        "period": "CALCULATE: Latest data period + 3 Australian FY",
        "granularity": "quarterly",
        "data_points": 12,
        "_REQUIRED_METRICS": "ALL FOUR MUST BE PRESENT: revenue, gross_profit, expenses, net_profit",
        "revenue": [
          {{"period": "Quarter 1", "value": 650000, "confidence": "medium"}},
          {{"period": "Quarter 2", "value": 670000, "confidence": "medium"}},
          {{"period": "Quarter 3", "value": 685000, "confidence": "medium"}},
          {{"period": "Quarter 4", "value": 700000, "confidence": "medium"}},
          {{"period": "Quarter 5", "value": 720000, "confidence": "medium"}},
          {{"period": "Quarter 6", "value": 735000, "confidence": "medium"}},
          {{"period": "Quarter 7", "value": 750000, "confidence": "medium"}},
          {{"period": "Quarter 8", "value": 770000, "confidence": "medium"}},
          {{"period": "Quarter 9", "value": 790000, "confidence": "medium"}},
          {{"period": "Quarter 10", "value": 810000, "confidence": "medium"}},
          {{"period": "Quarter 11", "value": 830000, "confidence": "medium"}},
          {{"period": "Quarter 12", "value": 850000, "confidence": "medium"}}
        ],
        "gross_profit": [
          {{"period": "Quarter 1", "value": 260000, "confidence": "medium"}},
          {{"period": "Quarter 2", "value": 268000, "confidence": "medium"}},
          {{"period": "Quarter 3", "value": 274000, "confidence": "medium"}},
          {{"period": "Quarter 4", "value": 280000, "confidence": "medium"}},
          {{"period": "Quarter 5", "value": 288000, "confidence": "medium"}},
          {{"period": "Quarter 6", "value": 294000, "confidence": "medium"}},
          {{"period": "Quarter 7", "value": 300000, "confidence": "medium"}},
          {{"period": "Quarter 8", "value": 308000, "confidence": "medium"}},
          {{"period": "Quarter 9", "value": 316000, "confidence": "medium"}},
          {{"period": "Quarter 10", "value": 324000, "confidence": "medium"}},
          {{"period": "Quarter 11", "value": 332000, "confidence": "medium"}},
          {{"period": "Quarter 12", "value": 340000, "confidence": "medium"}}
        ],
        "expenses": [
          {{"period": "Quarter 1", "value": 490000, "confidence": "medium"}},
          {{"period": "Quarter 2", "value": 502000, "confidence": "medium"}},
          {{"period": "Quarter 3", "value": 511000, "confidence": "medium"}},
          {{"period": "Quarter 4", "value": 520000, "confidence": "medium"}},
          {{"period": "Quarter 5", "value": 532000, "confidence": "medium"}},
          {{"period": "Quarter 6", "value": 541000, "confidence": "medium"}},
          {{"period": "Quarter 7", "value": 550000, "confidence": "medium"}},
          {{"period": "Quarter 8", "value": 562000, "confidence": "medium"}},
          {{"period": "Quarter 9", "value": 574000, "confidence": "medium"}},
          {{"period": "Quarter 10", "value": 586000, "confidence": "medium"}},
          {{"period": "Quarter 11", "value": 598000, "confidence": "medium"}},
          {{"period": "Quarter 12", "value": 610000, "confidence": "medium"}}
        ],
        "net_profit": [
          {{"period": "Quarter 1", "value": 160000, "confidence": "medium"}},
          {{"period": "Quarter 2", "value": 168000, "confidence": "medium"}},
          {{"period": "Quarter 3", "value": 174000, "confidence": "medium"}},
          {{"period": "Quarter 4", "value": 180000, "confidence": "medium"}},
          {{"period": "Quarter 5", "value": 188000, "confidence": "medium"}},
          {{"period": "Quarter 6", "value": 194000, "confidence": "medium"}},
          {{"period": "Quarter 7", "value": 200000, "confidence": "medium"}},
          {{"period": "Quarter 8", "value": 208000, "confidence": "medium"}},
          {{"period": "Quarter 9", "value": 216000, "confidence": "medium"}},
          {{"period": "Quarter 10", "value": 224000, "confidence": "medium"}},
          {{"period": "Quarter 11", "value": 232000, "confidence": "medium"}},
          {{"period": "Quarter 12", "value": 240000, "confidence": "medium"}}
        ]
      }},
      "5_years_ahead": {{
        "period": "CALCULATE: Latest data period + 5 Australian FY",
        "granularity": "yearly",
        "data_points": 5,
        "_REQUIRED_METRICS": "ALL FOUR MUST BE PRESENT: revenue, gross_profit, expenses, net_profit",
        "revenue": [
          {{"period": "Year 1", "value": 3500000, "confidence": "medium"}},
          {{"period": "Year 2", "value": 3700000, "confidence": "medium"}},
          {{"period": "Year 3", "value": 3920000, "confidence": "medium"}},
          {{"period": "Year 4", "value": 4150000, "confidence": "medium"}},
          {{"period": "Year 5", "value": 4400000, "confidence": "medium"}}
        ],
        "gross_profit": [
          {{"period": "Year 1", "value": 1400000, "confidence": "medium"}},
          {{"period": "Year 2", "value": 1480000, "confidence": "medium"}},
          {{"period": "Year 3", "value": 1568000, "confidence": "medium"}},
          {{"period": "Year 4", "value": 1660000, "confidence": "medium"}},
          {{"period": "Year 5", "value": 1760000, "confidence": "medium"}}
        ],
        "expenses": [
          {{"period": "Year 1", "value": 2650000, "confidence": "medium"}},
          {{"period": "Year 2", "value": 2780000, "confidence": "medium"}},
          {{"period": "Year 3", "value": 2920000, "confidence": "medium"}},
          {{"period": "Year 4", "value": 3070000, "confidence": "medium"}},
          {{"period": "Year 5", "value": 3230000, "confidence": "medium"}}
        ],
        "net_profit": [
          {{"period": "Year 1", "value": 850000, "confidence": "medium"}},
          {{"period": "Year 2", "value": 920000, "confidence": "medium"}},
          {{"period": "Year 3", "value": 1000000, "confidence": "medium"}},
          {{"period": "Year 4", "value": 1080000, "confidence": "medium"}},
          {{"period": "Year 5", "value": 1170000, "confidence": "medium"}}
        ]
      }},
      "10_years_ahead": {{
        "period": "CALCULATE: Latest data period + 10 Australian FY",
        "granularity": "yearly",
        "data_points": 10,
        "_REQUIRED_METRICS": "ALL FOUR MUST BE PRESENT: revenue, gross_profit, expenses, net_profit",
        "revenue": [
          {{"period": "Year 1", "value": 6000000, "confidence": "low"}},
          {{"period": "Year 2", "value": 6300000, "confidence": "low"}},
          {{"period": "Year 3", "value": 6620000, "confidence": "low"}},
          {{"period": "Year 4", "value": 6950000, "confidence": "low"}},
          {{"period": "Year 5", "value": 7300000, "confidence": "low"}},
          {{"period": "Year 6", "value": 7670000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 8050000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 8450000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 8870000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 9310000, "confidence": "very_low"}}
        ],
        "gross_profit": [
          {{"period": "Year 1", "value": 2400000, "confidence": "low"}},
          {{"period": "Year 2", "value": 2520000, "confidence": "low"}},
          {{"period": "Year 3", "value": 2648000, "confidence": "low"}},
          {{"period": "Year 4", "value": 2780000, "confidence": "low"}},
          {{"period": "Year 5", "value": 2920000, "confidence": "low"}},
          {{"period": "Year 6", "value": 3068000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 3220000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 3380000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 3548000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 3724000, "confidence": "very_low"}}
        ],
        "expenses": [
          {{"period": "Year 1", "value": 4200000, "confidence": "low"}},
          {{"period": "Year 2", "value": 4410000, "confidence": "low"}},
          {{"period": "Year 3", "value": 4630000, "confidence": "low"}},
          {{"period": "Year 4", "value": 4860000, "confidence": "low"}},
          {{"period": "Year 5", "value": 5100000, "confidence": "low"}},
          {{"period": "Year 6", "value": 5360000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 5630000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 5910000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 6210000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 6520000, "confidence": "very_low"}}
        ],
        "net_profit": [
          {{"period": "Year 1", "value": 1800000, "confidence": "low"}},
          {{"period": "Year 2", "value": 1890000, "confidence": "low"}},
          {{"period": "Year 3", "value": 1990000, "confidence": "low"}},
          {{"period": "Year 4", "value": 2090000, "confidence": "low"}},
          {{"period": "Year 5", "value": 2200000, "confidence": "low"}},
          {{"period": "Year 6", "value": 2310000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 2420000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 2540000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 2660000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 2790000, "confidence": "very_low"}}
        ]
      }},
      "15_years_ahead": {{
        "period": "CALCULATE: Latest data period + 15 Australian FY",
        "granularity": "yearly",
        "data_points": 15,
        "_REQUIRED_METRICS": "ALL FOUR MUST BE PRESENT: revenue, gross_profit, expenses, net_profit",
        "revenue": [
          {{"period": "Year 1", "value": 9500000, "confidence": "very_low"}},
          {{"period": "Year 2", "value": 9950000, "confidence": "very_low"}},
          {{"period": "Year 3", "value": 10420000, "confidence": "very_low"}},
          {{"period": "Year 4", "value": 10910000, "confidence": "very_low"}},
          {{"period": "Year 5", "value": 11420000, "confidence": "very_low"}},
          {{"period": "Year 6", "value": 11950000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 12500000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 13080000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 13680000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 14310000, "confidence": "very_low"}},
          {{"period": "Year 11", "value": 14970000, "confidence": "very_low"}},
          {{"period": "Year 12", "value": 15660000, "confidence": "very_low"}},
          {{"period": "Year 13", "value": 16380000, "confidence": "very_low"}},
          {{"period": "Year 14", "value": 17130000, "confidence": "very_low"}},
          {{"period": "Year 15", "value": 17920000, "confidence": "very_low"}}
        ],
        "gross_profit": [
          {{"period": "Year 1", "value": 3800000, "confidence": "very_low"}},
          {{"period": "Year 2", "value": 3980000, "confidence": "very_low"}},
          {{"period": "Year 3", "value": 4168000, "confidence": "very_low"}},
          {{"period": "Year 4", "value": 4364000, "confidence": "very_low"}},
          {{"period": "Year 5", "value": 4568000, "confidence": "very_low"}},
          {{"period": "Year 6", "value": 4780000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 5000000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 5232000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 5472000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 5724000, "confidence": "very_low"}},
          {{"period": "Year 11", "value": 5988000, "confidence": "very_low"}},
          {{"period": "Year 12", "value": 6264000, "confidence": "very_low"}},
          {{"period": "Year 13", "value": 6552000, "confidence": "very_low"}},
          {{"period": "Year 14", "value": 6852000, "confidence": "very_low"}},
          {{"period": "Year 15", "value": 7168000, "confidence": "very_low"}}
        ],
        "expenses": [
          {{"period": "Year 1", "value": 6650000, "confidence": "very_low"}},
          {{"period": "Year 2", "value": 6980000, "confidence": "very_low"}},
          {{"period": "Year 3", "value": 7320000, "confidence": "very_low"}},
          {{"period": "Year 4", "value": 7680000, "confidence": "very_low"}},
          {{"period": "Year 5", "value": 8060000, "confidence": "very_low"}},
          {{"period": "Year 6", "value": 8460000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 8880000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 9320000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 9780000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 10260000, "confidence": "very_low"}},
          {{"period": "Year 11", "value": 10770000, "confidence": "very_low"}},
          {{"period": "Year 12", "value": 11310000, "confidence": "very_low"}},
          {{"period": "Year 13", "value": 11880000, "confidence": "very_low"}},
          {{"period": "Year 14", "value": 12470000, "confidence": "very_low"}},
          {{"period": "Year 15", "value": 13090000, "confidence": "very_low"}}
        ],
        "net_profit": [
          {{"period": "Year 1", "value": 2850000, "confidence": "very_low"}},
          {{"period": "Year 2", "value": 2970000, "confidence": "very_low"}},
          {{"period": "Year 3", "value": 3100000, "confidence": "very_low"}},
          {{"period": "Year 4", "value": 3230000, "confidence": "very_low"}},
          {{"period": "Year 5", "value": 3360000, "confidence": "very_low"}},
          {{"period": "Year 6", "value": 3490000, "confidence": "very_low"}},
          {{"period": "Year 7", "value": 3620000, "confidence": "very_low"}},
          {{"period": "Year 8", "value": 3760000, "confidence": "very_low"}},
          {{"period": "Year 9", "value": 3900000, "confidence": "very_low"}},
          {{"period": "Year 10", "value": 4050000, "confidence": "very_low"}},
          {{"period": "Year 11", "value": 4200000, "confidence": "very_low"}},
          {{"period": "Year 12", "value": 4350000, "confidence": "very_low"}},
          {{"period": "Year 13", "value": 4500000, "confidence": "very_low"}},
          {{"period": "Year 14", "value": 4650000, "confidence": "very_low"}},
          {{"period": "Year 15", "value": 4800000, "confidence": "very_low"}}
        ]
      }}
    }},
    "assumptions": [
      "Australian economic conditions remain relatively stable across projection periods",
      "Business operates within Australian Financial Year (July 1 - June 30) framework",
      "Growth rates naturally decelerate over longer time horizons (1yr: high confidence → 15yr: very low confidence)",
      "No major disruptions to established business cycle or Australian market conditions",
      "Regulatory environment in Australia remains supportive of business operations"
    ],
    "scenarios": {{
      "optimistic": {{
        "description": "Accelerated growth with strong Australian market performance",
        "growth_multiplier_1_3yr": 1.3,
        "growth_multiplier_5_10yr": 1.2,
        "growth_multiplier_15yr": 1.1,
        "key_drivers": ["Australian market expansion", "operational efficiency", "favorable AUD exchange rates"]
      }},
      "conservative": {{
        "description": "Slower growth due to Australian market challenges",
        "growth_multiplier_1_3yr": 0.8,
        "growth_multiplier_5_10yr": 0.7,
        "growth_multiplier_15yr": 0.6,
        "key_drivers": ["Australian market saturation", "increased competition", "economic uncertainty", "unfavorable AUD conditions"]
      }}
    }},
    "trend_analysis": {{
      "overall_trend": "Strong positive growth with Australian seasonal patterns",
      "seasonality_impact": "Revenue peaks in Q2 FY (Oct-Dec), troughs in Q4 FY (Apr-Jun) due to Australian business cycles",
      "growth_trajectory": "Decelerating growth rates over time: 1yr (high growth) → 15yr (mature/stable growth)",
      "volatility_assessment": "Increasing uncertainty over longer projection periods",
      "australian_factors": "Considerations for Australian market dynamics, FY reporting cycles, and economic patterns"
    }}
  }},
  "methodology": {{
    "model_chosen": "SARIMA|ARIMA|Prophet|LinearRegression|ExponentialSmoothing|Combined",
    "model_justification": "MUST PROVIDE: Clear explanation of why this specific model was selected for the data characteristics and business context. Example: Selected SARIMA due to strong seasonal patterns and trend components in revenue data",
    "preprocessing_steps": [
      "outlier removal using IQR method",
      "linear interpolation for missing data points", 
      "log transformation applied to stabilize variance",
      "seasonal decomposition for pattern analysis"
    ],
    "data_quality_score": 0.92,
    "train_test_split": "80/20 chronological split with validation period",
    "validation_metrics": {{
      "mape": 0.082,
      "rmse": 14500,
      "mae": 11200,
      "r_squared": 0.89,
      "cross_validation_score": 0.85
    }},
    "feature_engineering": [
      "Australian seasonal indicators (Q2 FY peak, Q4 FY trough)",
      "economic cycle indicators", 
      "trend and seasonality decomposition"
    ],
    "sensitivity_analysis": "±10% revenue growth scenario analysis shows net profit impact range",
    "confidence_intervals": "95% confidence intervals calculated using bootstrap resampling",
    "key_assumptions": [
      "Australian inflation rate remains within normal range",
      "No major regulatory changes affecting the industry", 
      "Business continues current operational model",
      "No major economic disruptions"
    ]
  }},
  "data_quality_assessment": {{
    "completeness_score": 0.92,
    "period_coverage": "24 months with 2 missing data points",
    "consistency_issues": [
      "Missing data for specific periods",
      "Categorization changes in certain quarters"
    ],
    "outliers_detected": [
      {{"item": "Revenue spike December 2023", "deviation": "45% above trend", "impact": "medium", "likely_cause": "holiday_season"}},
      {{"item": "Expenses drop January 2023", "deviation": "20% below trend", "impact": "low", "likely_cause": "post_holiday_reduction"}}
    ],
    "data_gaps": [
      "Specific missing periods identified in analysis"
    ],
    "reliability_flags": [
      {{"flag": "seasonal_validation", "status": "passed", "impact": "low"}},
      {{"flag": "trend_consistency", "status": "passed", "impact": "low"}},
      {{"flag": "ratio_reasonableness", "status": "warning", "items": ["specific_ratio_warnings"], "impact": "medium"}}
    ]
  }},
  "accuracy_considerations": {{
    "projection_confidence": {{
      "1_year_ahead": "high",
      "3_years_ahead": "medium",
      "5_years_ahead": "medium",
      "10_years_ahead": "low",
      "15_years_ahead": "very_low"
    }},
    "australian_fy_confidence": "high",
    "trend_confidence": "high", 
    "risk_factors": [
      "Australian economic downturns could disrupt growth patterns",
      "Changes in Australian tax policy or FY regulations",
      "Competition could impact long-term growth trajectory",
      "Currency fluctuations (AUD) affecting international business",
      "Regulatory changes specific to Australian market"
    ],
    "improvement_recommendations": [
      "Include Australian economic indicators in future analysis",
      "Consider Australian seasonal business patterns within FY framework",
      "Add industry-specific Australian market analysis",
      "Include sensitivity analysis for AUD exchange rate impacts"
    ],
    "model_limitations": [
      "Long-term projections (10-15 years) have inherently high uncertainty",
      "No consideration of major economic disruptions or policy changes",
      "Assumes Australian business environment remains relatively stable",
      "Limited consideration of technological disruption over long horizons"
    ]
  }},
  "qa_checks": {{
    "period_consistency": [],
    "seasonal_validation": [],
    "math_consistency": [],
    "trend_validation": [],
    "outlier_assessment": [],
    "_SCHEMA_COMPLETENESS_CHECK": "VERIFY: All 5 projection periods contain complete sets of 4 financial metrics (revenue, gross_profit, expenses, net_profit) before outputting this JSON"
  }},
  "executive_summary": "Comprehensive analysis based on available data points with Australian Financial Year alignment. Specific projections provided for 1, 3, 5, 10, and 15 years ahead, with confidence levels decreasing over longer horizons. Australian seasonal patterns and FY framework considered throughout analysis."
}}

REASONING STYLE
• Provide concise *chain-of-thought* reasoning inside the `methodology` fields only.  
• Use short bullet lists, not paragraphs.
• Explain model selection rationale clearly.
• Document preprocessing steps with specific details.
• Include validation metrics for transparency.

EXAMPLES
• Monthly format: "2023-01" ; Quarterly: "2023-Q3" ; FY: "FY2024".
• Model justification: "Selected SARIMA(2,1,1)(1,1,1)[12] due to clear trend and seasonal patterns in revenue data with monthly seasonality"
• Preprocessing: "Applied log transformation to revenue series to reduce variance heteroscedasticity"

CRITICAL METHODOLOGY FORMAT EXAMPLE
"methodology": {{
  "model_chosen": "SARIMA",
  "model_justification": "Selected SARIMA model due to strong seasonal patterns...",
  "data_quality_score": 0.92,
  "preprocessing_steps": ["outlier removal", "interpolation"],
  "key_assumptions": ["business continues current model"]
}}

FINAL VALIDATION REQUIREMENT
Before outputting the JSON, perform this check:
Does EVERY projection period (1_year_ahead, 3_years_ahead, 5_years_ahead, 10_years_ahead, 15_years_ahead) contain ALL FOUR financial metrics?
1. revenue: [array with data points]
2. gross_profit: [array with data points]  
3. expenses: [array with data points]
4. net_profit: [array with data points]

If ANY projection period is missing ANY of these four metrics, DO NOT output the JSON. Add the missing metrics first.

REMINDER
Return JSON only – no other text. Include complete methodology transparency.
NEVER return methodology as a string - always use the structured object format above.
MANDATORY: Every projection period MUST contain all four financial metrics: revenue, gross_profit, expenses, net_profit
""" 