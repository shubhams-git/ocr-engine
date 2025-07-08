"""
Multi-PDF analysis service using Google Gemini AI
Handles multiple PDFs, extracts data, normalizes, and makes projections

PROJECTION ACCURACY IMPROVEMENT SUGGESTIONS:

1. **Data Quality Enhancements**
   - Request standardized financial statements (GAAP/IFRS format)
   - Validate data against industry benchmarks
   - Implement cross-validation between balance sheet and income statement
   - Add data completeness scoring and minimum thresholds

2. **Historical Analysis Improvements**
   - Require minimum 3-5 years of historical data for trend analysis
   - Implement seasonal decomposition for quarterly/monthly data
   - Detect and handle structural breaks in financial time series
   - Calculate rolling averages to smooth out volatility

3. **Advanced Forecasting Techniques**
   - Implement multiple forecasting models (ARIMA, exponential smoothing, regression)
   - Use ensemble methods to combine different projection approaches
   - Apply Monte Carlo simulation for scenario analysis
   - Incorporate economic indicators as external variables

4. **Industry Context Integration**
   - Add industry-specific growth rates and benchmark ratios
   - Include economic cycle considerations (recession/expansion periods)
   - Factor in regulatory changes and compliance costs
   - Consider competitive landscape and market saturation

5. **Risk Assessment Framework**
   - Implement sensitivity analysis for key assumptions
   - Add confidence intervals around projections
   - Create stress testing scenarios (worst/best case)
   - Include probability distributions for key metrics

6. **Model Validation & Calibration**
   - Implement backtesting on historical data
   - Add performance tracking against actual results
   - Regularly recalibrate model parameters
   - Include model uncertainty in final projections

7. **Business Context Factors**
   - Consider management guidance and strategic plans
   - Factor in known future events (contracts, expansions, etc.)
   - Include working capital seasonality patterns
   - Account for capital expenditure cycles

8. **Technical Improvements**
   - Add outlier detection and robust estimation methods
   - Implement automated ratio sanity checks
   - Use time-series cross-validation for model selection
   - Add feature importance analysis for key drivers

9. **External Data Integration**
   - Include macroeconomic forecasts (GDP, inflation, interest rates)
   - Add industry growth projections from reliable sources
   - Consider commodity price forecasts if relevant
   - Include demographic and market size projections

10. **Output Enhancement**
    - Provide prediction intervals, not just point estimates
    - Include assumption sensitivity analysis
    - Add graphical trend visualizations
    - Create executive summary with key insights and risks

IMPLEMENTATION PRIORITY:
High: Items 1, 2, 5, 10 (foundational data quality and risk assessment)
Medium: Items 3, 4, 6 (advanced modeling and industry context)
Low: Items 7, 8, 9 (business context and external data integration)
"""
import logging
import io
from typing import List
from fastapi import HTTPException

from google import genai
from config import get_next_key, API_KEYS
from models import MultiPDFAnalysisResponse

logger = logging.getLogger(__name__)

class MultiPDFService:
    """Service for handling multiple PDF analysis with projections"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB per file
        self.max_files = 10  # Maximum number of files to process
    
    def validate_files(self, files_data: List[tuple]) -> None:
        """Validate uploaded files (filename, content pairs)"""
        if not files_data:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files_data) > self.max_files:
            raise HTTPException(status_code=400, detail=f"Too many files. Maximum is {self.max_files}")
        
        for filename, content in files_data:
            if not filename:
                raise HTTPException(status_code=400, detail="Missing filename")
            
            if len(content) > self.max_file_size:
                raise HTTPException(status_code=413, detail=f"File {filename} too large. Maximum size is 50MB")
            
            if not filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {filename} is not a PDF")
            
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"File {filename} is empty")
            
            if not content.startswith(b'%PDF'):
                raise HTTPException(status_code=400, detail=f"File {filename} is not a valid PDF")
    
    def extract_response_text(self, response) -> str:
        """Extract text from Gemini response"""
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        elif response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    text_part = candidate.content.parts[0].text
                    if text_part:
                        return text_part.strip()
        
        raise Exception("No data could be extracted from response")
    
    async def analyze_multiple_pdfs(self, files_data: List[tuple], model: str = "gemini-2.5-flash") -> MultiPDFAnalysisResponse:
        """
        Analyze multiple PDFs with data extraction, normalization, and projections
        files_data: List of (filename, content) tuples
        """
        try:
            # Validate files
            self.validate_files(files_data)
            
            # Create comprehensive prompt for analysis
            prompt = """
            You are a senior financial analyst with expertise in trend analysis and forecasting.

            Your task: Analyze ALL attached financial PDFs and return a comprehensive JSON object with this structure:

            {
                "extracted_data": [
                    {
                        "source_document": "filename.pdf",
                        "period": "YYYY or YYYY-MM to YYYY-MM",
                        "financial_statements": {
                            "income_statement": { ... },
                            "balance_sheet": { ... },
                            "cash_flow": { ... }
                        },
                        "key_metrics": { ... }
                    }
                ],
                "normalized_data": {
                    "time_series": {
                        "revenue": [{"period": "2023", "value": 1000000}, ...],
                        "expenses": [{"period": "2023", "value": 800000}, ...],
                        "net_profit": [{"period": "2023", "value": 200000}, ...],
                        "assets": [{"period": "2023", "value": 2000000}, ...],
                        "liabilities": [{"period": "2023", "value": 1200000}, ...],
                        "equity": [{"period": "2023", "value": 800000}, ...]
                    },
                    "growth_rates": {
                        "revenue_cagr": 0.15,
                        "expense_growth": 0.12,
                        "profit_growth": 0.25
                    },
                    "financial_ratios": {
                        "profit_margin": [{"period": "2023", "value": 0.20}, ...],
                        "roa": [{"period": "2023", "value": 0.10}, ...],
                        "current_ratio": [{"period": "2023", "value": 1.5}, ...]
                    }
                },
                "projections": {
                    "methodology": "Describe the forecasting approach used",
                    "base_year": "YYYY",
                    "forecast_horizon": "2-3 years",
                    "yearly_projections": {
                        "2025": {
                            "revenue": {"value": 1200000, "growth_rate": 0.15, "confidence": "high"},
                            "expenses": {"value": 950000, "growth_rate": 0.12, "confidence": "medium"},
                            "net_profit": {"value": 250000, "growth_rate": 0.25, "confidence": "medium"},
                            "assets": {"value": 2400000, "growth_rate": 0.20, "confidence": "medium"},
                            "key_ratios": {
                                "profit_margin": 0.208,
                                "roa": 0.104,
                                "debt_to_equity": 0.65
                            }
                        },
                        "2026": { ... },
                        "2027": { ... }
                    },
                    "assumptions": [
                        "Market growth continues at historical 10-15% annually",
                        "Operating costs increase with inflation at 8% per year",
                        "No major capital expenditures beyond normal replacement"
                    ],
                    "scenarios": {
                        "optimistic": {
                            "description": "Strong market growth, cost efficiencies",
                            "revenue_multiplier": 1.3,
                            "key_drivers": ["market expansion", "operational efficiency"]
                        },
                        "conservative": {
                            "description": "Slower growth, higher costs",
                            "revenue_multiplier": 0.8,
                            "key_drivers": ["market saturation", "increased competition"]
                        }
                    },
                    "trend_analysis": {
                        "revenue_trend": "Consistent upward trend with seasonal variations",
                        "cost_trend": "Rising costs due to inflation and expansion",
                        "profitability_trend": "Improving margins through efficiency gains",
                        "seasonality": "Q4 typically strongest, Q1 weakest"
                    }
                },
                "data_quality_assessment": {
                    "completeness_score": 0.95,
                    "consistency_issues": [
                        "Missing cash flow data for 2022",
                        "Inconsistent expense categorization between periods"
                    ],
                    "outliers_detected": [
                        {"item": "Marketing expenses Q3 2023", "deviation": "300% above average", "impact": "high"}
                    ],
                    "data_gaps": [
                        "Detailed segment breakdown not available for all periods",
                        "Working capital components missing for 2021"
                    ],
                    "reliability_flags": [
                        {"flag": "unaudited_financials", "periods": ["2023"], "impact": "medium"},
                        {"flag": "estimation_used", "items": ["depreciation", "provisions"], "impact": "low"}
                    ]
                },
                "accuracy_considerations": {
                    "forecast_confidence": {
                        "year_1": "high",
                        "year_2": "medium", 
                        "year_3": "low"
                    },
                    "risk_factors": [
                        "Economic downturn could impact revenue by 20-30%",
                        "Interest rate changes affecting financing costs",
                        "Supply chain disruptions impacting cost structure"
                    ],
                    "improvement_recommendations": [
                        "Obtain monthly data for better seasonality analysis",
                        "Include industry benchmarks for validation",
                        "Incorporate leading economic indicators"
                    ],
                    "model_limitations": [
                        "Limited historical data (only 2-3 years available)",
                        "No consideration of competitive dynamics",
                        "Assumes current business model remains unchanged"
                    ]
                },
                "qa_checks": {
                    "math_consistency": [],
                    "classification_warnings": [],
                    "sign_anomalies": [],
                    "trend_validation": []
                },
                "executive_summary": "Brief narrative explaining key findings, trends, and projection rationale"
            }

            **DETAILED INSTRUCTIONS:**

            **1. Data Extraction & Validation**
            • Extract every financial figure exactly as shown, maintaining original signs and formatting
            • Identify the time periods covered by each document
            • Store GST/VAT gross balances separately (gst_paid_total, gst_collected_total)
            • Flag and correct classification issues (e.g., debit balances in liability accounts)

            **2. Trend Analysis Requirements**
            • Calculate year-over-year growth rates for all major financial metrics
            • Identify seasonal patterns if monthly/quarterly data is available
            • Detect anomalies and outliers that could skew projections
            • Analyze ratio trends (margins, liquidity, efficiency, leverage)

            **3. Projection Methodology**
            • Use trend analysis as primary driver for projections
            • Apply compound annual growth rates (CAGR) where appropriate
            • Consider mean reversion for ratios that appear unsustainable
            • Factor in business lifecycle stage (startup, growth, mature, decline)

            **4. Yearly Projections (MANDATORY)**
            • Provide specific projections for each of the next 2-3 years
            • Include confidence levels: high (>80%), medium (60-80%), low (<60%)
            • Calculate projected financial ratios for each year
            • Show growth rates year-over-year

            **5. Assumptions Documentation**
            • List ALL assumptions used in projections
            • Specify economic assumptions (inflation, interest rates, market growth)
            • Note operational assumptions (capacity, efficiency, market share)
            • Include regulatory or industry-specific factors

            **6. Risk Assessment**
            • Identify key risk factors that could impact projections
            • Provide optimistic and conservative scenarios (±20-30% variance)
            • Flag data quality issues that affect forecast reliability
            • Note model limitations and recommend improvements

            **7. Data Quality Control**
            • Assign completeness score (0-1) based on available data
            • Flag inconsistencies between periods or documents
            • Identify missing data that affects forecast quality
            • Note any estimates or approximations used

            **8. Mathematical Validation**
            • Verify: Gross Profit = Revenue - COGS (±$1 tolerance)
            • Verify: Operating Profit = Gross Profit - Operating Expenses (±$1)
            • Verify: Assets = Liabilities + Equity (±$1)
            • Validate that projected ratios remain within reasonable ranges

            **9. Output Quality**
            • Use 2 decimal places for monetary values
            • Express growth rates and ratios as decimals (e.g., 0.15 for 15%)
            • Ensure all projected values are mathematically consistent
            • Provide clear narrative explanations for major changes or assumptions

            **10. Special Considerations**
            • For partial-year data, clearly state annualization method
            • If insufficient historical data, note limitations and reduce confidence
            • Consider industry benchmarks if apparent from data patterns
            • Flag any regulatory or compliance issues that might affect projections

            Return ONLY the JSON object. Ensure all financial calculations are accurate and all assumptions are explicitly stated.
            """
            
            # Try with each API key until one works
            last_error = None
            
            for attempt in range(len(API_KEYS)):
                try:
                    # Get next API key
                    api_key = get_next_key()
                    current_client = genai.Client(api_key=api_key)
                    
                    logger.info(f"Processing multi-PDF analysis with model {model} (attempt {attempt + 1})")
                    
                    # Upload files using File API
                    uploaded_files = []
                    contents = []
                    
                    for filename, content in files_data:
                        logger.info(f"Uploading file: {filename}")
                        
                        # Upload file using File API with filename for mime type detection
                        import tempfile
                        import os
                        
                        # Create a temporary file with PDF extension
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                            temp_file.write(content)
                            temp_file_path = temp_file.name
                        
                        try:
                            uploaded_file = current_client.files.upload(file=temp_file_path)
                        finally:
                            # Clean up temporary file
                            os.unlink(temp_file_path)
                        uploaded_files.append(uploaded_file)
                        contents.append(uploaded_file)
                    
                    # Add prompt at the end
                    contents.append(prompt)
                    
                    # Send to Gemini with uploaded files
                    response = current_client.models.generate_content(
                        model=model,
                        contents=contents
                    )
                    
                    # Extract response text
                    extracted_text = self.extract_response_text(response)
                    logger.info("Multi-PDF analysis completed successfully")
                    
                    # Try to parse the JSON response
                    try:
                        import json
                        import re
                        
                        logger.info(f"Raw response length: {len(extracted_text)} characters")
                        
                        # First, try to extract JSON from markdown code blocks
                        json_text = extracted_text
                        
                        # Multiple extraction strategies
                        extraction_successful = False
                        
                        # Strategy 1: Look for ```json code blocks (most common)
                        if '```json' in extracted_text:
                            logger.info("Found ```json markdown block, attempting extraction...")
                            # Use a more robust pattern that handles nested braces
                            json_matches = re.finditer(r'```json\s*\n(.*?)(?=\n```|\n$)', extracted_text, re.DOTALL)
                            for match in json_matches:
                                candidate_json = match.group(1).strip()
                                try:
                                    # Try to parse this candidate
                                    result_data = json.loads(candidate_json)
                                    json_text = candidate_json
                                    extraction_successful = True
                                    logger.info("Successfully extracted JSON from ```json block")
                                    break
                                except json.JSONDecodeError:
                                    continue
                        
                        # Strategy 2: Look for any code blocks if ```json didn't work
                        if not extraction_successful and '```' in extracted_text:
                            logger.info("Looking for generic code blocks...")
                            json_matches = re.finditer(r'```[a-zA-Z]*\s*\n(.*?)(?=\n```|\n$)', extracted_text, re.DOTALL)
                            for match in json_matches:
                                candidate_json = match.group(1).strip()
                                try:
                                    result_data = json.loads(candidate_json)
                                    json_text = candidate_json
                                    extraction_successful = True
                                    logger.info("Successfully extracted JSON from generic code block")
                                    break
                                except json.JSONDecodeError:
                                    continue
                        
                        # Strategy 3: Look for the largest JSON object in the text
                        if not extraction_successful:
                            logger.info("Looking for largest JSON object in text...")
                            # Find all potential JSON objects (starting with { and ending with })
                            brace_count = 0
                            start_pos = -1
                            longest_json = ""
                            
                            for i, char in enumerate(extracted_text):
                                if char == '{':
                                    if brace_count == 0:
                                        start_pos = i
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0 and start_pos != -1:
                                        # Found a complete JSON object
                                        candidate_json = extracted_text[start_pos:i+1]
                                        if len(candidate_json) > len(longest_json):
                                            try:
                                                # Validate it's valid JSON
                                                json.loads(candidate_json)
                                                longest_json = candidate_json
                                            except json.JSONDecodeError:
                                                pass
                            
                            if longest_json:
                                try:
                                    result_data = json.loads(longest_json)
                                    json_text = longest_json
                                    extraction_successful = True
                                    logger.info(f"Successfully extracted JSON object of {len(longest_json)} characters")
                                except json.JSONDecodeError:
                                    pass
                        
                        # Strategy 4: Try parsing the entire response as JSON
                        if not extraction_successful:
                            logger.info("Attempting to parse entire response as JSON...")
                            try:
                                result_data = json.loads(extracted_text)
                                extraction_successful = True
                                logger.info("Successfully parsed entire response as JSON")
                            except json.JSONDecodeError:
                                pass
                        
                        # If we successfully extracted JSON, return the structured response
                        if extraction_successful:
                            # Extract enhanced fields for better analysis
                            data_quality = result_data.get("data_quality_assessment", {})
                            accuracy_considerations = result_data.get("accuracy_considerations", {})
                            projections_data = result_data.get("projections", {})
                            
                            return MultiPDFAnalysisResponse(
                                success=True,
                                extracted_data=result_data.get("extracted_data", []),
                                normalized_data=result_data.get("normalized_data", {}),
                                projections=projections_data,
                                explanation=result_data.get("executive_summary", result_data.get("explanation", "Analysis completed successfully")),
                                error=None,
                                
                                # Enhanced fields
                                data_quality_score=data_quality.get("completeness_score"),
                                confidence_levels=accuracy_considerations.get("forecast_confidence", {}),
                                assumptions=projections_data.get("assumptions", []),
                                risk_factors=accuracy_considerations.get("risk_factors", []),
                                methodology=projections_data.get("methodology"),
                                scenarios=projections_data.get("scenarios", {})
                            )
                        else:
                            logger.warning("All JSON extraction strategies failed")
                            raise json.JSONDecodeError("No valid JSON found", extracted_text, 0)
                            
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.warning(f"Failed to parse JSON response: {str(e)}")
                        logger.info("Returning raw text as explanation...")
                        
                        # If all JSON parsing fails, return the raw text as explanation
                        return MultiPDFAnalysisResponse(
                            success=True,
                            extracted_data=[],
                            normalized_data={},
                            projections={},
                            explanation=extracted_text,
                            error=None,
                            data_quality_score=None,
                            confidence_levels=None,
                            assumptions=None,
                            risk_factors=None,
                            methodology=None,
                            scenarios=None
                        )
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"API key {attempt + 1} failed: {str(e)}")
            
            # All API keys failed
            logger.error(f"All {len(API_KEYS)} API keys failed. Last error: {str(last_error)}")
            return MultiPDFAnalysisResponse(
                success=False,
                extracted_data=[],
                normalized_data={},
                projections={},
                explanation="",
                error=f"All API keys failed: {str(last_error)}",
                data_quality_score=None,
                confidence_levels=None,
                assumptions=None,
                risk_factors=None,
                methodology=None,
                scenarios=None
            )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing multi-PDF analysis: {str(e)}")
            return MultiPDFAnalysisResponse(
                success=False,
                extracted_data=[],
                normalized_data={},
                projections={},
                explanation="",
                error=str(e),
                data_quality_score=None,
                confidence_levels=None,
                assumptions=None,
                risk_factors=None,
                methodology=None,
                scenarios=None
            )

# Create a single instance to use across the app
multi_pdf_service = MultiPDFService() 