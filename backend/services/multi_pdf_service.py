"""
Multi-PDF analysis service using Google Gemini AI
Handles multiple PDFs and CSV files, extracts data, normalizes, and makes projections

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
from typing import List, Tuple
from fastapi import HTTPException

from google import genai
from config import get_next_key, API_KEYS
from models import MultiPDFAnalysisResponse
from prompts import MULTI_PDF_PROMPT

logger = logging.getLogger(__name__)

class MultiPDFService:
    """Service for handling multiple PDF and CSV analysis with projections"""
    
    def __init__(self):
        # File size limits by type
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_files = 10  # Maximum number of files to process
    
    def get_file_type_and_mime(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Determine file type and MIME type from filename and content"""
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        filename_lower = filename.lower()
        
        # Check for CSV files
        if filename_lower.endswith('.csv'):
            return 'csv', 'text/csv'
        
        # Check for PDF files
        elif filename_lower.endswith('.pdf'):
            # Validate PDF header
            if not content.startswith(b'%PDF'):
                raise HTTPException(status_code=400, detail=f"File {filename} does not appear to be a valid PDF")
            return 'pdf', 'application/pdf'
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type for {filename}. Please upload PDF or CSV files only."
            )
    
    def process_csv_content(self, content: bytes, filename: str) -> str:
        """Convert CSV bytes to text with proper encoding detection"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                csv_text = content.decode(encoding)
                logger.info(f"Successfully decoded CSV {filename} with {encoding} encoding")
                return csv_text
            except UnicodeDecodeError:
                continue
        
        raise HTTPException(
            status_code=400, 
            detail=f"Unable to decode CSV file {filename}. Please ensure it's a valid text file with UTF-8, Latin-1, or Windows-1252 encoding."
        )
    
    def validate_files(self, files_data: List[tuple]) -> None:
        """Validate uploaded files (filename, content pairs) for both PDF and CSV"""
        if not files_data:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files_data) > self.max_files:
            raise HTTPException(status_code=400, detail=f"Too many files. Maximum is {self.max_files}")
        
        for filename, content in files_data:
            if not filename:
                raise HTTPException(status_code=400, detail="Missing filename")
            
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"File {filename} is empty")
            
            # Get file type and validate accordingly
            file_type, _ = self.get_file_type_and_mime(filename, content)
            
            if file_type == 'pdf' and len(content) > self.max_pdf_size:
                raise HTTPException(status_code=413, detail=f"PDF file {filename} too large. Maximum size is 50MB")
            elif file_type == 'csv' and len(content) > self.max_csv_size:
                raise HTTPException(status_code=413, detail=f"CSV file {filename} too large. Maximum size is 25MB")
    
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
    
    async def analyze_multiple_files(self, files_data: List[tuple], model: str = "gemini-2.5-flash") -> MultiPDFAnalysisResponse:
        """
        Analyze multiple PDF and CSV files with data extraction, normalization, and projections
        files_data: List of (filename, content) tuples
        """
        try:
            # Validate files
            self.validate_files(files_data)
            
            # Use prompt from configuration
            prompt = MULTI_PDF_PROMPT
            
            # Try with each API key until one works
            last_error = None
            
            for attempt in range(len(API_KEYS)):
                try:
                    # Get next API key
                    api_key = get_next_key()
                    current_client = genai.Client(api_key=api_key)
                    
                    logger.info(f"Processing multi-file analysis with model {model} (attempt {attempt + 1})")
                    
                    # Separate files by type and process accordingly
                    contents = []
                    
                    # Build comprehensive prompt with CSV data and PDF file references
                    comprehensive_prompt = prompt
                    csv_data_sections = []
                    
                    for filename, content in files_data:
                        file_type, mime_type = self.get_file_type_and_mime(filename, content)
                        
                        if file_type == 'csv':
                            logger.info(f"Processing CSV file: {filename}")
                            # Process CSV as text
                            csv_text = self.process_csv_content(content, filename)
                            csv_section = f"""
CSV FILE: {filename}
Content:
{csv_text}

---
"""
                            csv_data_sections.append(csv_section)
                        
                        elif file_type == 'pdf':
                            logger.info(f"Uploading PDF file: {filename}")
                            # Upload PDF using File API
                            import tempfile
                            import os
                            
                            # Create a temporary file with PDF extension
                            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                                temp_file.write(content)
                                temp_file_path = temp_file.name
                            
                            try:
                                uploaded_file = current_client.files.upload(file=temp_file_path)
                                contents.append(uploaded_file)
                            finally:
                                # Clean up temporary file
                                os.unlink(temp_file_path)
                    
                    # If we have CSV data, prepend it to the prompt
                    if csv_data_sections:
                        csv_intro = """
IMPORTANT: The following CSV files contain financial data that should be analyzed alongside any PDF documents:

"""
                        comprehensive_prompt = csv_intro + "".join(csv_data_sections) + "\n" + prompt
                    
                    # Add the comprehensive prompt
                    contents.append(comprehensive_prompt)
                    
                    # Send to Gemini with mixed content (uploaded PDFs + text prompt with CSV data)
                    response = current_client.models.generate_content(
                        model=model,
                        contents=contents
                    )
                    
                    # Extract response text
                    extracted_text = self.extract_response_text(response)
                    logger.info("Multi-file analysis completed successfully")
                    
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
                            data_analysis_summary = result_data.get("data_analysis_summary", {})
                            
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
                                scenarios=projections_data.get("scenarios", {}),
                                
                                # New dynamic period detection fields - map correctly
                                period_granularity=data_analysis_summary.get("period_granularity_detected"),
                                total_data_points=data_analysis_summary.get("total_data_points"),
                                time_span=data_analysis_summary.get("time_span"),
                                seasonality_detected=data_analysis_summary.get("seasonality_detected"),
                                data_analysis_summary=data_analysis_summary
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
                            scenarios=None,
                            period_granularity=None,
                            total_data_points=None,
                            time_span=None,
                            seasonality_detected=None,
                            data_analysis_summary=None
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
                scenarios=None,
                period_granularity=None,
                total_data_points=None,
                time_span=None,
                seasonality_detected=None,
                data_analysis_summary=None
            )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing multi-file analysis: {str(e)}")
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
                scenarios=None,
                period_granularity=None,
                total_data_points=None,
                time_span=None,
                seasonality_detected=None,
                data_analysis_summary=None
            )
    
    async def analyze_multiple_pdfs(self, files_data: List[tuple], model: str = "gemini-2.5-flash") -> MultiPDFAnalysisResponse:
        """
        Backward compatibility method - delegates to analyze_multiple_files
        """
        return await self.analyze_multiple_files(files_data, model)

# Create a single instance to use across the app
multi_pdf_service = MultiPDFService() 