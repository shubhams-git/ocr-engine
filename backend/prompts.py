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
- **Quoted Currency Values**: Strip quotes and dollar signs from values like "$1,234.56" → 1234.56
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
Instead of using flat rates like $850/month, apply INTELLIGENT DEPRECIATION ESTIMATION:

1. **PRIMARY METHOD - Asset Roll-Forward Analysis**:
   - Analyze Fixed Assets Net movements period-to-period
   - Calculate: Depreciation = Beginning FA + Capex - Ending FA - Disposals
   - Validate against accumulated depreciation changes (if available)

2. **SECONDARY METHOD - Progressive Asset-Based Rates**:
   - Small Equipment (<$100k): 15% annual rate (high depreciation)
   - Medium Equipment ($100k-$300k): 10% annual rate (moderate depreciation)  
   - Large Equipment ($300k-$600k): 7% annual rate (standard depreciation)
   - Infrastructure (>$600k): 4% annual rate (conservative depreciation)

3. **VALIDATION CHECKS**:
   - Ensure annual depreciation rate is between 2%-25%
   - Cross-check against typical industry depreciation patterns
   - Flag unrealistic depreciation amounts for review

DETAILED CALCULATION FRAMEWORK:

1. **OPERATING ACTIVITIES RECONSTRUCTION**:
   - Start with Net Income from P&L
   - Add back ENHANCED depreciation estimate (not flat $850)
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
   - Base tolerance: $1,000 AUD or 2% of |ΔCash|, whichever is greater
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
- **Primary tolerance**: $1,000 AUD absolute or 2% of |ΔCash|, whichever is greater
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
✅ Apply DEPRECIATION ESTIMATION (not flat $850)
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
- ❌ Using flat $850 depreciation
- ❌ Default RECLASS_DRAWINGS classification

REMEMBER: Output ONLY the enhanced JSON - no other text whatsoever.
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
- If Net Profit = $$100,000 for the quarter
- Dividend Payment = $$100,000 * 0.40 = $$40,000
- Cash Flow from Financing = -$$40,000 (cash outflow)
- Retained Earnings reduction = -$$40,000
- Remaining in Retained Earnings = $$60,000

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