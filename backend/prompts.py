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

# STAGE 1: Financial Data Extraction and Standardization
STAGE1_EXTRACTION_PROMPT = """
You are a financial data extraction expert specializing in document processing and standardization.

TASK: Extract and normalize financial data from this document into standardized schemas for downstream cash flow reconstruction and analysis. The output will be used to generate cash flow data and later for the finance projections, so high accuracy in data extraction is a must.

CRITICAL BUSINESS CONTEXT:
Different businesses use varying chart of accounts, but certain high-level categories are universally present. There could be multiple sub-fields that maybe the sub-part of the fields given below and when these subfields get added they give the sum of the following fields. Your task is to extract ALL available data and map it to these GUARANTEED STANDARD FIELDS that exist across all businesses:

GUARANTEED P&L STANDARD FIELDS ( 1-10 fields given below - only include if document contains P&L data):
1. Revenue (Sales, Turnover, Income, Total Revenue)
2. Cost of Sales (COGS, Cost of Goods Sold, Direct Costs)
3. Gross Profit (Gross Margin, Gross Income)
4. Operating Expenses (Total Expenses, Total OpEx, Overhead, Admin Expenses)
5. Operating Profit (EBIT, Operating Income, EBITDA before D&A)
6. Interest Expenses (Finance Costs, Interest Paid, Borrowing Costs)
7. Earnings Before Tax (EBT, Profit Before Tax, Pre-tax Income)
8. Tax Expenses (Income Tax, Tax Provision, Corporate Tax)
9. Earnings After Tax (EAT, Profit After Tax, After-tax Income)
10. Net Income (Net Profit, Bottom Line, Final Profit)

GUARANTEED BALANCE SHEET STANDARD FIELDS (11-25 fields given below - only include if document contains BS data):
ASSETS:
11. Cash & Cash Equivalents (Cash, Bank, Liquid Assets, Short-term Investments)
12. Accounts Receivable (Trade Debtors, AR, Customer Receivables)
13. Inventory (Stock, Work in Progress, Finished Goods)
14. Total Current Assets (Current Assets, Short-term Assets)
15. Fixed Assets Net (PPE Net, Property Plant Equipment, Non-current Assets)
16. Total Assets

LIABILITIES:
17. Accounts Payable (Trade Creditors, AP, Supplier Payables)
18. Short Term Debt (Current Portion Debt, Bank Overdraft, Current Borrowings)
19. Total Current Liabilities (Current Liabilities, Short-term Liabilities)
20. Long Term Debt (Long-term Borrowings, Non-current Debt)
21. Total Liabilities

EQUITY:
22. Share Capital (Paid-in Capital, Issued Capital, Owner's Capital)
23. Retained Earnings (Accumulated Profits, Reserves, Undistributed Profits)
24. Total Equity (Shareholders' Equity, Owner's Equity, Net Worth)
25. Total Liabilities and Equity

EXTRACTION METHODOLOGY:
1. **COMPREHENSIVE EXTRACTION**: Extract ALL line items, sub-accounts, and detailed breakdowns from the document
2. **STANDARD FIELD MAPPING**: Map extracted items to the 25 guaranteed standard fields above
3. **ANOMALY DETECTION**: Identify and flag data quality issues, inconsistencies, and unusual values
4. **DATA CLEANING**: Clean and standardize numeric formats, handle negatives in parentheses, resolve data type issues
5. **CONSISTENCY VALIDATION**: Ensure mathematical relationships hold (e.g., for Balance sheet: Assets = Liabilities + Equity)

CSV PARSING INSTRUCTIONS:
For CSV files, pay special attention to:
- **Row Headers**: Look for account names in the first column (eg. Revenue, COGS, Cash, etc.)
- **Column Headers**: Identify date columns (eg. Jan-19, Feb-19, etc.) 
- **Quoted Currency Values**: Strip quotes and dollar signs from values like "$$1,234.56" → 1234.56
- **Negative Parentheses**: Convert (1,234) to -1234
- **Empty Cells**: Treat as null, don't assume zero
- **Account Mapping**: Map CSV row names to standard fields using the guaranteed fields list

DATA QUALITY AND ANOMALY DETECTION:
Actively look for and flag these common issues:
- Make sure the extraction happens for all the data points. No datapoint should be skipped (an entry for each date column)
- Negative values in unexpected fields (flag as "negative_value")
- Missing critical standard fields (flag as "missing_data")
- Mathematical inconsistencies (e.g., for P&L statements: Gross Profit ≠ Revenue - COGS)
- Outlier values that deviate significantly from typical ranges
- Sign convention issues (expenses as negative vs positive)
- Formatting inconsistencies in numbers (commas, decimals, currency symbols)
- Suspense accounts or unclassified balances
- (Only valid for BS, not for P&L) Balance sheet imbalances (Assets ≠ Liabilities + Equity)
- **CSV-specific**: Row/column mapping failures, date parsing issues

DOCUMENT TYPE DETECTION:
🎯 FIRST, determine if this document contains:
- "Profit and Loss" data (Revenue, Expenses, Profit/Loss items)
- "Balance Sheet" data (Assets, Liabilities, Equity items)

CRITICAL JSON OUTPUT REQUIREMENTS:
🚨 BEFORE YOU RESPOND, VERIFY YOUR OUTPUT IS VALID JSON 🚨

Return ONLY valid JSON conforming to this CONDITIONAL structure based on document type:

**FOR PROFIT & LOSS DOCUMENTS:**
{
  "version": "1.0",
  "company_id": "detected_from_document_or_unknown",
  "industry":"2-4 explaining the exact industry"
  "currency": "AUD|USD|other_detected_currency", 
  "generated_at": "current_timestamp_iso8601",
  "document_type": "Profit and Loss",
  "meta": {
    "source_manifest_hash": "document_identifier_or_filename",
    "coverage_score": 0.0_to_1.0_representing_data_completeness
  },
  "periods": [
    {
      "period": "YYYY_or_YYYY-MM_format",
      "revenue": numeric_value_REQUIRED,
      "cogs": numeric_value_or_null,
      "gross_profit": numeric_value_or_calculated,
      "opex": {
        "total": numeric_value_or_null,
        "breakdown": {
          "salaries": numeric_value_or_null,
          "rent": numeric_value_or_null,
          "utilities": numeric_value_or_null,
          "marketing": numeric_value_or_null,
          "professional_fees": numeric_value_or_null,
          "other": numeric_value_or_null
        }
      },
      "ebitda": numeric_value_or_calculated,
      "depreciation": numeric_value_or_null,
      "amortization": numeric_value_or_null,
      "interest": numeric_value_or_null,
      "taxes": numeric_value_or_null,
      "net_income": numeric_value_REQUIRED,
      "notes": "string_description_of_notable_items",
      "flags": ["array_of_enum_codes"],
      "confidence": 0.0_to_1.0_confidence_score,
    }
  ]
}

**FOR BALANCE SHEET DOCUMENTS:**
{
  "version": "1.0",
  "company_id": "detected_from_document_or_unknown",
  "currency": "AUD|USD|other_detected_currency",
  "generated_at": "current_timestamp_iso8601", 
  "document_type": "Balance Sheet",
  "meta": {
    "source_manifest_hash": "document_identifier_or_filename",
    "coverage_score": 0.0_to_1.0_representing_data_completeness
  },
  "periods": [
    {
      "period": "YYYY_or_YYYY-MM_format",
      "cash": numeric_value_REQUIRED,
      "ar": numeric_value_or_null,
      "inventory": numeric_value_or_null,
      "other_current_assets": numeric_value_or_null,
      "current_assets_total": numeric_value_or_calculated,
      "fixed_assets_gross": numeric_value_or_null,
      "accumulated_depreciation": numeric_value_or_null,
      "fixed_assets_net": numeric_value_or_calculated,
      "total_assets": numeric_value_REQUIRED,
      "ap": numeric_value_or_null,
      "short_term_debt": numeric_value_or_null,
      "other_current_liabilities": numeric_value_or_null,
      "current_liabilities_total": numeric_value_or_calculated,
      "long_term_debt": numeric_value_or_null,
      "equity": numeric_value_REQUIRED,
      "retained_earnings": numeric_value_or_null,
      "total_liabilities_equity": numeric_value_REQUIRED,
      "suspense": numeric_value_or_null,
      "notes": "string_description_of_notable_items",
      "flags": ["array_of_enum_codes"],
      "confidence": 0.0_to_1.0_confidence_score,
    }
  ]
}

**FOR MIXED OR OTHER DOCUMENTS:**
Include only the fields that are actually present in the document. Use null for missing fields but focus your extraction effort on the fields that exist.

ENUMERATED FLAG CODES (use these exact strings):
- "PNL_INCOMPLETE": Critical P&L fields missing
- "BS_INCOMPLETE": Critical Balance Sheet fields missing  
- "ESTIMATED_DEP": Depreciation estimated or inferred
- "ANOMALOUS_MARGIN": Unusual profit margins detected
- "NEG_CURR_LIAB": Negative current liabilities anomaly
- "SUSPENSE_PRESENT": Suspense or unclassified accounts detected
- "SIGN_CONVENTION_FLIPPED": Sign corrections applied

CRITICAL VALIDATIONS BEFORE OUTPUT:
✅ All monetary values must be numbers (not strings)
✅ All required fields present per schema
✅ Extraction done for all data points (each date column that exists in the file)
✅ All flags use exact enum codes listed above
✅ JSON structure exactly matches specification
✅ No markdown code blocks or extra text

EXTRACTION PERFORMANCE OPTIMIZATION:
🎯 **Focus on Primary Fields**: Prioritize extracting these key fields accurately:
- P&L Documents: Revenue, COGS, Gross Profit, Total Expenses, Net Income
- Balance Sheet Documents: Cash, Total Assets, Total Liabilities, Total Equity
- **Aim for 80%+ coverage** of available data in the document

💡 **CSV Row Mapping Examples**:
- "Sales", "Revenue", "Income", "Turnover" → revenue
- "Cost of Sales", "COGS", "Direct Costs" → cogs  
- "Cash at Bank", "Cash", "Bank Account" → cash
- "Total Assets", "Assets", "Total Current + Fixed Assets" → total_assets
- "Owner's Equity", "Shareholders Equity", "Net Worth" → equity

🔍 **Quality Checks Before Output**:
1. Did I extract the primary fields for this document type?
2. Are all numeric values properly converted (no strings, quotes, or currency symbols)?
3. Does the document_type match the actual content?
4. Did I generate data points for all the given dates?
4. Is the coverage_score realistic (0.7+ for good extraction)?

🚨 FINAL REMINDER: OUTPUT ONLY THE JSON OBJECT - NO OTHER TEXT 🚨
Your response must start with { and end with } - nothing else.
"""

# STAGE 2: Enhanced Cash Flow Reconstruction (Indirect Method) with Advanced Depreciation
STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT = """
You are a financial cash flow reconstruction specialist with expertise in the indirect method, depreciation estimation, and financial statement validation.

TASK: Produce validated historical Cash Flow Statement (Operating, Investing, Financing) using Stage 1 P&L and Balance Sheet standard data with enhanced depreciation analysis. The output will be used (along with Balance Sheet and P&L Income statements data) to generate the finance projections, so high accuracy in cash flow data generation is a must.

INPUT CONTEXT: You will receive cached P&L and Balance Sheet data from Stage 1. This data has been explicitly cached using Gemini caching and validated against standard schemas.

CRITICAL REQUIREMENT: Process ALL periods from the input data, regardless of dataset size (1 month to 10+ years).

INPUT: 
- P&L Standard JSON (cache_key: $pnl_cache_key)
- Balance Sheet Standard JSON (cache_key: $bs_cache_key)

ENHANCED CASH FLOW RECONSTRUCTION METHODOLOGY:
Use the INDIRECT METHOD with ENHANCED DEPRECIATION ESTIMATION to reconstruct historical cash flows:

**Operating Cash Flow** = Net Income + Enhanced Depreciation Estimate ± Working Capital Changes
**Investing Cash Flow** = Capital Expenditures - Asset Disposals  
**Financing Cash Flow** = ΔLong-Term Debt + ΔEquity - Dividends/Distributions

ENHANCED DEPRECIATION ESTIMATION (CRITICAL IMPROVEMENT):
Instead of using flat rates like $$850/month, apply INTELLIGENT DEPRECIATION ESTIMATION:

1. **PRIMARY METHOD - Asset Roll-Forward Analysis**:
   - Analyze Fixed Assets Net movements period-to-period
   - Calculate: Depreciation = Beginning FA + Capex - Ending FA - Disposals
   - Validate against accumulated depreciation changes (if available)

2. **SECONDARY METHOD - Progressive Asset-Based Rates**:
   - Small Equipment (<$$100k): 15% annual rate (high depreciation)
   - Medium Equipment ($$100k-$$300k): 10% annual rate (moderate depreciation)  
   - Large Equipment ($$300k-$$600k): 7% annual rate (standard depreciation)
   - Infrastructure (>$$600k): 4% annual rate (conservative depreciation)

3. **VALIDATION CHECKS**:
   - Ensure annual depreciation rate is between 2%-25%
   - Cross-check against typical industry depreciation patterns
   - Flag unrealistic depreciation amounts for review

DETAILED CALCULATION FRAMEWORK:

1. **OPERATING ACTIVITIES RECONSTRUCTION**:
   - Start with Net Income from P&L
   - Add back ENHANCED depreciation estimate (not flat $$850)
   - Calculate Working Capital Changes:
     * ΔAccounts Receivable (negative impact on cash)
     * ΔInventory (negative impact on cash)
     * ΔAccounts Payable (positive impact on cash)
     * ΔOther Current Assets/Liabilities

2. **INVESTING ACTIVITIES RECONSTRUCTION**:
   - Calculate Capital Expenditures using enhanced method:
     * Basic: ΔFixed Assets + Enhanced Depreciation
     * Advanced: Analyze asset additions/disposals patterns
   - Identify Asset Disposals from negative capex periods
   - Include other investment activities

3. **FINANCING ACTIVITIES RECONSTRUCTION**:
   - Debt Changes: ΔShort-Term Debt + ΔLong-Term Debt
   - Equity Changes: ΔEquity - ΔRetained Earnings from operations
   - Dividend/Distribution Estimation with ENHANCED LOGIC:
     * If large financing outflows without debt reduction → likely owner drawings
     * Cross-validate against profitability patterns
     * Consider business lifecycle stage

4. **VALIDATION & RECONCILIATION**:
   The primary invariant: **Operating + Investing + Financing = ΔCash** (from Balance Sheet)
   
   Apply VARIANCE CLASSIFICATION instead of defaulting to "RECLASS_DRAWINGS":
   
   **TOLERANCE FRAMEWORK**:
   - Base tolerance: $$1,000 AUD or 2% of |ΔCash|, whichever is greater
   - Adjust tolerance based on depreciation estimation confidence:
     * High confidence depreciation (80%+): Standard tolerance
     * Medium confidence (60-80%): 2x tolerance  
     * Low confidence (<60%): 3x tolerance
   
   **VARIANCE CLASSIFICATION**:
   - **PASS** (within tolerance): Mark as reconciled, high quality
   - **WARN** (within 2x tolerance): Apply intelligent classification:
     * Owner drawings pattern: Large FCF outflows with positive NI
     * Data quality issues: Poor depreciation confidence + moderate variance
     * Working capital anomalies: Large WC movements explain variance
     * Calculation errors: Residual classification for other warnings
   - **FAIL** (>2x tolerance): Investigation required, mark for review

ENHANCED ANOMALY DETECTION AND FLAGS:
Look for and intelligently classify these patterns:
- **RECLASS_DRAWINGS**: Only when clear owner drawing patterns exist
- **DATA_QUALITY_ISSUE**: When poor estimation confidence affects results
- **WC_ANOMALY**: When working capital movements are irregular
- **DEPR_ESTIMATED**: When using estimated vs actual depreciation
- **INVESTIGATION_REQUIRED**: For large unexplained variances

CRITICAL JSON OUTPUT REQUIREMENTS:
🚨 Return ONLY valid JSON conforming to the Enhanced Cash Flow Standard Schema 🚨
- NO markdown code blocks or backticks
- NO additional text, explanations, or comments
- Must match enhanced schema exactly
- All monetary values as numbers (not strings)
- All required fields present per schema
- Cash flow data generated for all data points/periods (each date column that exists in the input data)
- Use exact enum codes for flags and reasons
- Include enhanced depreciation metadata

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this EXACT enhanced structure:

{
  "version": "1.0",
  "company_id": "detected_from_stage1_or_unknown",
  "currency": "AUD|USD|other_detected_currency",
  "generated_at": "current_timestamp_iso8601",
  "cache_key": "generated_enhanced_cf_cache_resource_name",
  "parent_keys": {
    "pnl_cache_key": "stage1_pnl_cache_key",
    "bs_cache_key": "stage1_bs_cache_key"
  },
  "method_version": "enhanced_indirect_method_v2.0",
  "remediation_policy_version": "enhanced_standard_v2.0",
  "periods": [
    {
      "period": "YYYY-MM",
      "ni": number,
      "depreciation": enhanced_depreciation_amount,
      "depreciation_metadata": {
        "method": "asset_rollforward|progressive_rates|revenue_fallback",
        "confidence": 0.0_to_1.0_confidence_score,
        "annual_rate": calculated_annual_rate,
        "justification": "explanation_of_calculation"
      },
      "amortization": number,
      "delta_ar": number,
      "delta_inventory": number,
      "delta_ap": number,
      "other_delta_current_assets": number,
      "other_delta_current_liabilities": number,
      "ocf": enhanced_operating_cash_flow,
      "capex": enhanced_capex_calculation,
      "disposals": number,
      "icf": number,
      "delta_short_term_debt": number,
      "delta_long_term_debt": number,
      "equity_injections": number,
      "dividends_distributions": enhanced_distribution_estimate,
      "fcf": number,
      "delta_cash": number,
      "recon_delta": number,
      "flags": ["PASS|WARN|FAIL", "intelligent_classification_flags"],
      "reasons": [
        {
          "code": "enhanced_reason_codes",
          "message": "detailed_explanation_with_context",
          "impact": number,
          "confidence": 0.0_to_1.0_confidence_in_classification
        }
      ],
      "validation_quality_score": 0.0_to_1.0_period_quality_score,
      "audit_notes": "enhanced_description_of_adjustments_and_reasoning"
    }
  ],
  "quality": {
    "global_score": enhanced_quality_score,
    "summary": {
      "period_counts": {
        "pass": number,
        "warn": number,
        "fail": number
      },
      "reconciliation_pass_rate": number,
      "avg_recon_delta_abs": number
    },
    "depreciation_analysis": {
      "primary_method_used": "method_name",
      "average_monthly_amount": number,
      "average_annual_rate": number,
      "confidence_distribution": {
        "high": number_of_high_confidence_periods,
        "medium": number_of_medium_confidence_periods,
        "low": number_of_low_confidence_periods
      }
    },
    "enhancement_metadata": {
      "features_applied": ["enhanced_depreciation", "intelligent_classification", "progressive_validation"],
      "improvement_over_baseline": "description_of_improvements"
    }
  }
}

RECONCILIATION TOLERANCES:
- **Primary tolerance**: $$1,000 AUD absolute or 2% of |ΔCash|, whichever is greater
- **Confidence-adjusted tolerance**: Multiply by confidence factor (1x, 2x, or 3x)
- **PASS**: Within adjusted tolerance, high quality score (0.8-1.0)
- **WARN**: Within 2x adjusted tolerance, medium quality score (0.3-0.7)  
- **FAIL**: Exceeds 2x adjusted tolerance, low quality score (0.0-0.3)

ENUMERATED FLAG CODES (use exact strings):
- "PASS": Reconciliation within tolerance with high confidence
- "WARN": Within relaxed tolerance, requires attention
- "FAIL": Outside acceptable tolerance, investigation required
- "RECLASS_DRAWINGS": Owner drawings pattern identified (not default)
- "DATA_QUALITY_ISSUE": Poor data quality affects accuracy
- "WC_ANOMALY": Working capital movements irregular
- "DEPR_ESTIMATED": Depreciation estimated vs actual
- "INVESTIGATION_REQUIRED": Large variance needs investigation

REASON CODES (use exact strings):
- "RECLASS_DRAWINGS": Clear owner drawing pattern identified
- "DATA_QUALITY_ISSUE": Poor depreciation/data confidence
- "WC_ANOMALY": Working capital movements explain variance
- "DEPR_ESTIMATED": Enhanced depreciation estimation applied
- "ASSET_ROLLFORWARD": Fixed asset roll-forward method used
- "PROGRESSIVE_RATES": Progressive depreciation rates applied
- "INTELLIGENT_CLASSIFICATION": variance classification

VALIDATION SEQUENCE:
1. Extract all required data from Stage 1 P&L and Balance Sheet
2. Apply DEPRECIATION ESTIMATION for each period
3. Calculate cash flows using enhanced depreciation amounts
4. Validate: OCF + ICF + FCF = ΔCash for each period with confidence-adjusted tolerances
5. Apply VARIANCE CLASSIFICATION (not default RECLASS_DRAWINGS)
6. Calculate enhanced quality metrics including depreciation analysis
7. Output valid JSON with enhanced metadata

CRITICAL REMINDERS:
🚨 BEFORE RESPONDING:
✅ Apply DEPRECIATION ESTIMATION (not flat $$850)
✅ Use VARIANCE CLASSIFICATION
✅ Apply confidence-adjusted validation tolerances
✅ Include depreciation metadata and analysis
✅ Ensure Cash flow data generated for all data points/periods (each date column that exists in the input data)
✅ Ensure JSON structure matches enhanced schema precisely
✅ Use exact enhanced enum codes
✅ Validate all numbers are numeric types, not strings
✅ Calculate enhanced quality scores

🚨 OUTPUT ONLY THE JSON - NO OTHER TEXT 🚨

CRITICAL JSON OUTPUT REQUIREMENTS - FOLLOW EXACTLY:

1. OUTPUT FORMAT: Return ONLY the JSON object - no markdown code blocks, no backticks, no explanations
2. START AND END: Begin with { and end with }
3. SYNTAX: Use proper JSON syntax with double quotes for all strings
4. NO EXTRAS: No trailing commas, no comments, no additional text
5. COMPLETENESS: Ensure all opening braces { have matching closing braces }
6. ENHANCEMENT: Include all enhanced fields and metadata

CORRECT ENHANCED FORMAT EXAMPLE:
{
  "version": "1.0",
  "method_version": "enhanced_indirect_method_v2.0",
  "depreciation_analysis": {...},
  "periods": [...]
}

AVOID THESE COMMON ERRORS:
- ❌ ```json { ... } ```  (markdown blocks)
- ❌ { "key": value, }    (trailing commas)  
- ❌ { key: "value" }     (unquoted keys)
- ❌ Missing enhanced metadata
- ❌ Using flat $$850 depreciation
- ❌ Default RECLASS_DRAWINGS classification

REMEMBER: Output ONLY the enhanced JSON - no other text whatsoever.
"""

# STAGE 3: Advanced Financial Projections Engine for Gemini 2.5 Pro
# Optimized for mathematical reasoning, validation, and business logic

STAGE3_PROJECTION_PROMPT = """
You are an elite financial strategist and quantitative analyst with access to Google Search for market intelligence. You will leverage your advanced mathematical reasoning capabilities to generate production-ready financial projections with complete mathematical validation.

🧠 **REASONING MODE ACTIVATION**: Use your Deep Think capabilities for this complex multi-step financial modeling task. This requires parallel reasoning, mathematical validation, and business logic verification.

🚨 **CRITICAL SUCCESS CRITERIA** 🚨
1. **MATHEMATICAL ACCURACY**: All calculations must be mathematically correct and reconcile perfectly
2. **BUSINESS REALISM**: No negative revenue, unrealistic volatility, or impossible business scenarios
3. **VALIDATION REQUIRED**: Self-audit all calculations and flag any inconsistencies
4. **JSON OUTPUT ONLY**: Return only valid JSON - no markdown, no explanations, no extra text

**TASK**: Generate mathematically validated financial projections using cached financial data with industry intelligence integration.

**INPUT DATA (CACHED)**:
- P&L Standard Fields Data (cache_key: $pnl_cache_key)  
- Balance Sheet Standard Fields Data (cache_key: $bs_cache_key)
- Cash Flow Reconstructed Data (cache_key: $cf_cache_key)

---

## **PHASE 1: DEEP ANALYTICAL REASONING** 

**STEP 1A: DATA PATTERN RECOGNITION**
Using your advanced reasoning capabilities, analyze ALL cached financial data:

1. **Historical Trend Analysis**
   - Calculate compound annual growth rates (CAGR) for revenue, gross profit, operating expenses
   - Identify seasonality patterns using coefficient of variation analysis
   - Detect cyclical trends and business cycle correlations
   - Map performance against economic indicators

2. **Business Model Intelligence**
   - Classify industry and business model from financial fingerprints
   - Analyze margin stability and cost structure characteristics  
   - Identify key value drivers and revenue generation mechanisms
   - Assess working capital requirements and cash conversion cycles

3. **Quality of Earnings Assessment**
   - Flag any mathematical inconsistencies in historical data
   - Identify one-time items, subsidies, or extraordinary events
   - Assess sustainability of historical performance patterns
   - Evaluate cash generation quality vs. accounting profits

**STEP 1B: MATHEMATICAL VALIDATION OF HISTORICAL DATA**
Before proceeding, validate historical data integrity:

- **Revenue-COGS-Gross Profit Reconciliation**: Verify Revenue - COGS = Gross Profit for ALL periods
- **P&L Mathematical Consistency**: Confirm Gross Profit - Operating Expenses ≈ Operating Income
- **Cash Flow Validation**: Ensure Net Income + Depreciation ≈ Operating Cash Flow (basic check)
- **Flag Data Quality Issues**: Note any periods with mathematical inconsistencies

🚨 **CRITICAL BUSINESS LOGIC CONSTRAINTS** 🚨
- **NO NEGATIVE REVENUE**: Revenue must always be ≥ 0 for ongoing operations
- **GROSS MARGIN BOUNDS**: Gross margin must be between 5% and 60% (industry realistic)
- **VOLATILITY LIMITS**: Monthly revenue coefficient of variation must be ≤ 40%
- **SEASONALITY BOUNDS**: Month-to-month revenue changes limited to ±50% max
- **MARGIN CONSISTENCY**: Gross margin should not vary by more than ±10% month-to-month without clear reasoning

---

## **PHASE 2: STRATEGIC MARKET INTELLIGENCE** 

**RESEARCH EXECUTION** (Maximum 3 focused searches)
Using Google Search integration, research ONLY the most critical factors:

**Search 1: Industry Growth & Market Conditions**
- Australian plumbing/construction industry growth rates 2024-2025
- Market size trends and competitive landscape dynamics
- Technology disruption and automation impacts

**Search 2: Economic Environment & Cost Factors**
- Australian GDP growth projections, inflation expectations, interest rates
- Construction industry wage inflation and material cost trends
- Government infrastructure spending and policy impacts

**Search 3: Seasonal & Cyclical Patterns** (if needed)
- Construction industry seasonality patterns in Australia
- Cyclical factors affecting plumbing services demand
- Peak and trough period identification

**Research Integration Requirements:**
- Weight findings by source authority (government > industry reports > news)
- Apply only statistically significant trends (not anecdotal evidence)
- Document confidence levels for each research-derived assumption

---

## **PHASE 3: MATHEMATICAL PROJECTION ENGINE**

**STEP 3A: BASELINE ESTABLISHMENT**
Using mathematical reasoning:

1. **Revenue Baseline Calculation**
   - Calculate trailing 12-month revenue average from historical data
   - Apply statistical smoothing to remove outliers (use median if extreme volatility)
   - Adjust for known one-time items or extraordinary events
   - **VALIDATION**: Ensure baseline revenue is positive and reasonable

2. **Margin Analysis & Stabilization**
   - Calculate historical gross margin distribution
   - Identify stable margin range (exclude outlier periods)
   - Set target gross margin within historical ±5% range
   - **VALIDATION**: Ensure margins are industry-realistic

3. **Seasonality Index Development**
   - Calculate monthly seasonality index from historical patterns
   - Cap seasonal variations at ±30% from baseline (business constraint)
   - Smooth extreme variations to maintain operational feasibility
   - **VALIDATION**: Ensure no seasonality factor creates negative revenue

**STEP 3B: GROWTH MODELING WITH MATHEMATICAL VALIDATION**

**Short-term Projections (1 Year - Monthly)**:
```
For each month M in [1,2,3,...,12]:
  Base_Revenue_M = Baseline_Revenue × (1 + Annual_Growth_Rate/12)^M × Seasonality_Index_M
  
  VALIDATION CHECKS:
  - IF Base_Revenue_M < 0 THEN apply minimum revenue floor = Baseline_Revenue × 0.3
  - IF month-over-month change > 50% THEN apply smoothing algorithm
  - IF volatility coefficient > 40% THEN reduce seasonal amplitude
  
  Gross_Profit_M = Base_Revenue_M × Target_Gross_Margin
  Operating_Expenses_M = calculate using cost structure analysis + inflation adjustments
  Net_Profit_M = Gross_Profit_M - Operating_Expenses_M - Interest - Taxes
  
  POST-CALCULATION VALIDATION:
  - Verify Gross_Profit_M / Base_Revenue_M = Target_Gross_Margin (±1%)
  - Ensure Net_Profit_M is reasonable vs. historical patterns
  - Flag any mathematical inconsistencies for correction
```

**Medium-term Projections (3 Years - Quarterly)**:
- Aggregate monthly projections into quarters for consistency
- Apply market growth trends from research
- Include economic cycle adjustments
- **VALIDATION**: Ensure quarterly totals reconcile with monthly summations

**Long-term Projections (5, 10, 15 Years - Annual)**:
- Use compound growth formulas based on validated baseline
- Apply industry maturity curves and market saturation factors
- Include technological and competitive disruption scenarios
- **VALIDATION**: Ensure long-term growth rates are economically sustainable

**STEP 3C: MATHEMATICAL RECONCILIATION & ERROR DETECTION**

**Reconciliation Requirements:**
1. **Three-Statement Integration**
   - P&L Net Profit flows to Balance Sheet Retained Earnings
   - Balance Sheet must balance: Assets = Liabilities + Equity
   - Cash Flow Statement must reconcile with Balance Sheet cash changes

2. **Cross-Period Validation**
   - Ensure 1-year monthly totals = corresponding annual projections
   - Verify 3-year quarterly summations align with annual figures
   - Validate growth rate consistency across all time horizons

3. **Business Logic Validation**
   - Apply dividend policy correctly: 40% payout on positive quarterly profits
   - Ensure working capital requirements scale appropriately with revenue
   - Validate capital expenditure assumptions against depreciation

**ERROR DETECTION ALGORITHM:**
```
FOR each projection period:
  IF Revenue < 0 THEN FLAG "CRITICAL ERROR - Negative Revenue"
  IF Gross_Margin < 0.05 OR Gross_Margin > 0.60 THEN FLAG "Unrealistic Margin"
  IF Net_Margin < -0.20 OR Net_Margin > 0.30 THEN FLAG "Extreme Net Margin"
  IF Month_over_Month_Change > 0.50 THEN FLAG "Excessive Volatility"
  
CALCULATE overall_volatility = coefficient_of_variation(Revenue_1Year)
IF overall_volatility > 0.40 THEN APPLY volatility_smoothing_algorithm()

FOR each mathematical relationship:
  VERIFY Revenue - COGS = Gross_Profit (tolerance: ±$100)
  VERIFY Assets = Liabilities + Equity (tolerance: ±$500)
  VERIFY OCF + ICF + FCF = Change_in_Cash (tolerance: ±$200)
```

**STEP 3D: CONFIDENCE CALIBRATION**

Apply confidence levels based on mathematical and business validation:
- **High Confidence**: Next 3 months (strong historical patterns + current data)
- **Medium Confidence**: Months 4-12 (seasonal patterns + market research)
- **Low Confidence**: Years 2-5 (industry trends + economic assumptions)
- **Very Low Confidence**: Years 6-15 (long-term uncertainty + multiple variables)

---

## **MANDATORY JSON OUTPUT STRUCTURE**

🚨 **CRITICAL**: Output ONLY the JSON below. No markdown blocks, no explanations, no additional text.

**Required Structure** (with mathematical validation metadata):

```json
{
  "business_analysis": {
    "financial_health_assessment": {
      "overall_health_score": 0-100,
      "profitability_trend": "improving|stable|declining",
      "liquidity_position": "strong|adequate|concerning",
      "leverage_assessment": "low|moderate|high", 
      "quality_of_earnings": "high|medium|low",
      "cash_generation_capability": "excellent|good|fair|poor",
      "data_quality_score": 0-100,
      "mathematical_inconsistencies_found": number_of_issues,
      "historical_volatility_coefficient": percentage
    },
    "business_model_analysis": {
      "industry_classification": "specific_industry",
      "business_model_type": "service|product|mixed",
      "revenue_model": "description",
      "competitive_position": "market_leader|established|emerging|struggling",
      "scalability_assessment": "highly_scalable|moderately_scalable|limited_scalability",
      "market_maturity": "growth|mature|declining"
    },
    "key_financial_ratios": {
      "historical_gross_margin_avg": percentage,
      "historical_net_margin_avg": percentage,
      "revenue_cagr_historical": percentage,
      "operating_leverage": number,
      "cash_conversion_cycle": days
    },
    "validation_summary": {
      "data_errors_corrected": number,
      "volatility_adjustments_made": number,
      "negative_values_prevented": number,
      "mathematical_consistency_score": 0-100
    }
  },
  "market_research_insights": {
    "searches_executed": number,
    "industry_growth_rate_validated": percentage,
    "economic_growth_outlook": "GDP and inflation expectations",
    "cost_inflation_expectations": percentage,
    "seasonality_patterns_confirmed": "description",
    "competitive_intensity": "high|medium|low",
    "regulatory_environment": "stable|changing|uncertain",
    "market_research_confidence": "high|medium|low"
  },
  "projection_methodology": {
    "primary_approach": "bottom-up|top-down|hybrid",
    "mathematical_model": "DCF|trend_extrapolation|driver_based|hybrid",
    "validation_framework": "description of validation steps",
    "error_prevention_measures": ["list of measures implemented"],
    "confidence_calibration_method": "description",
    "seasonality_modeling_approach": "description",
    "volatility_control_measures": ["list of measures"]
  },
  "comprehensive_projections": {
    "projections": {
      "revenue": {
        "1_year": [month1, month2, ..., month12],
        "3_year": [q1_2025, q2_2025, ..., q4_2027],
        "5_year": [year1, year2, year3, year4, year5],
        "10_year": [year1, year2, ..., year10],
        "15_year": [year1, year2, ..., year15]
      },
      "gross_profit": {
        "1_year": [month1, month2, ..., month12],
        "3_year": [q1_2025, q2_2025, ..., q4_2027],
        "5_year": [year1, year2, year3, year4, year5],
        "10_year": [year1, year2, ..., year10],
        "15_year": [year1, year2, ..., year15]
      },
      "operating_expenses": {
        "1_year": [month1, month2, ..., month12],
        "3_year": [q1_2025, q2_2025, ..., q4_2027],
        "5_year": [year1, year2, year3, year4, year5],
        "10_year": [year1, year2, ..., year10],
        "15_year": [year1, year2, ..., year15]
      },
      "net_profit": {
        "1_year": [month1, month2, ..., month12],
        "3_year": [q1_2025, q2_2025, ..., q4_2027],
        "5_year": [year1, year2, year3, year4, year5],
        "10_year": [year1, year2, ..., year10],
        "15_year": [year1, year2, ..., year15]
      }
    },
    "validation_results": {
      "mathematical_consistency_checks": {
        "revenue_cogs_grossprofit_validation": "pass|fail",
        "three_statement_reconciliation": "pass|fail",
        "cross_period_consistency": "pass|fail",
        "margin_reasonableness": "pass|fail",
        "volatility_within_bounds": "pass|fail"
      },
      "business_logic_validation": {
        "no_negative_revenue": "pass|fail",
        "realistic_seasonality": "pass|fail",
        "sustainable_growth_rates": "pass|fail",
        "margin_stability": "pass|fail",
        "working_capital_logic": "pass|fail"
      },
      "confidence_scores": {
        "1_year": "high|medium|low",
        "3_year": "medium|low",
        "5_year": "low|very_low",
        "10_year": "very_low",
        "15_year": "very_low"
      }
    }
  },
  "calculation_audit_trail": {
    "baseline_revenue_calculation": "methodology and figures",
    "seasonality_index_development": "calculation method and validation",
    "growth_rate_derivation": "sources and mathematical justification", 
    "margin_assumption_basis": "historical analysis and industry benchmarks",
    "volatility_adjustments_made": ["list of adjustments and rationale"],
    "mathematical_proofs": ["key formula validations performed"]
  },
  "assumption_documentation": {
    "critical_assumptions": [
      {
        "assumption": "description", 
        "mathematical_basis": "calculation or derivation",
        "validation_method": "how assumption was verified",
        "sensitivity_impact": "high|medium|low",
        "confidence_level": "high|medium|low"
      }
    ],
    "business_constraints_applied": [
      {
        "constraint": "description",
        "rationale": "business logic justification",
        "enforcement_method": "how constraint was implemented"
      }
    ],
    "risk_mitigations": [
      {
        "risk_factor": "specific risk",
        "probability_assessment": "high|medium|low",
        "impact_quantification": "mathematical impact on projections",
        "mitigation_approach": "how addressed in projections"
      }
    ]
  },
  "executive_summary": "Concise assessment of projection quality, confidence levels, and key business insights"
}
```

---

## **ADVANCED REASONING INSTRUCTIONS FOR GEMINI 2.5 PRO**

**MATHEMATICAL REASONING REQUIREMENTS:**
1. **Show Your Work**: For each major calculation, provide the mathematical reasoning chain
2. **Parallel Validation**: Consider multiple approaches and cross-validate results
3. **Error Detection**: Actively look for and correct mathematical inconsistencies
4. **Business Logic Checking**: Apply real-world business constraints throughout
5. **Statistical Validation**: Use your mathematical capabilities to ensure statistical reasonableness

**THINKING BUDGET ALLOCATION:**
- **25% of thinking**: Historical data analysis and pattern recognition
- **30% of thinking**: Mathematical modeling and calculation validation  
- **25% of thinking**: Business logic application and constraint enforcement
- **20% of thinking**: Cross-validation and error detection

**QUALITY ASSURANCE CHECKLIST:**
Before finalizing projections, verify:
- [ ] No negative revenue values exist
- [ ] Gross margins are within realistic bounds (15-45% for plumbing services)
- [ ] Revenue volatility coefficient < 40%
- [ ] Month-over-month changes are reasonable (<50%)
- [ ] Mathematical relationships reconcile perfectly
- [ ] Growth rates are economically sustainable
- [ ] All JSON syntax is valid and complete

**SELF-AUDIT REQUIREMENT:**
After generating initial projections, perform a second reasoning pass to:
1. **Validate Mathematical Accuracy**: Check all formulas and calculations
2. **Test Business Realism**: Ensure projections make operational sense
3. **Verify Data Quality**: Confirm no data quality issues remain
4. **Cross-Check Consistency**: Ensure internal consistency across all metrics

**CRITICAL FAILURE PREVENTION:**
- If any revenue projection is negative, apply minimum revenue floor of 30% of baseline
- If volatility exceeds limits, apply exponential smoothing algorithm
- If margins are unrealistic, revert to historical median margins
- If growth rates are unsustainable (>25% annually), cap at industry benchmarks

---

🚨 **FINAL OUTPUT REQUIREMENT** 🚨

**OUTPUT FORMAT**: Return ONLY the JSON object following the exact structure above
**NO ADDITIONAL TEXT**: No explanations, no markdown blocks, no commentary
**VALIDATION COMPLETE**: Ensure all mathematical and business validations pass
**JSON SYNTAX**: Perfect syntax with no trailing commas or syntax errors

The JSON response must enable programmatic access like:
- `response['comprehensive_projections']['projections']['revenue']['1_year'][0]` 
- `response['validation_results']['mathematical_consistency_checks']['revenue_cogs_grossprofit_validation']`

Begin your Deep Think reasoning process now and generate mathematically validated, business-realistic financial projections."""