"""
Projection Service - Stage 3: Projection Engine with Scenario Planning
Separated from multi_pdf_service to create modular stage-based services
"""
import asyncio
import time
import json
import re
import string
from typing import Dict, Any
from fastapi import HTTPException

from google import genai
from config import get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from prompts import STAGE3_PROJECTION_PROMPT
from logging_config import (get_logger, log_api_call, log_stage_progress)

# Set up logger
logger = get_logger(__name__)

class ProjectionService:
    """Service for Stage 3: Projection Engine with Scenario Planning"""
    
    def __init__(self):
        # API configuration from config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # API key pool management
        self.api_key_pool = API_KEYS.copy()
        self.api_key_index = 0
        
        # Debug flag for detailed response logging
        self.debug_responses = False
        
        # Only log during main server process, not during uvicorn reloads
        import os
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Projection Service (Stage 3) initialized")
        logger.debug(f"API configuration | Timeout: {self.api_timeout}s | Max retries: {self.max_retries} | Retry delay: {self.retry_delay}s")
        logger.debug(f"API key pool initialized | Count: {len(self.api_key_pool)}")
        logger.debug(f"Debug response logging: {'ENABLED' if self.debug_responses else 'DISABLED'}")
    
    def get_next_api_key(self) -> str:
        """Get next API key from pool with rotation"""
        key = self.api_key_pool[self.api_key_index % len(self.api_key_pool)]
        self.api_key_index += 1
        key_preview = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key[:8] + "..."
        logger.debug(f"API key rotation | Using key: {key_preview} | Position: {self.api_key_index}/{len(self.api_key_pool)}")
        return key
    
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
        
        raise Exception("No data extracted from Gemini response")
    
    async def process_with_gemini(self, prompt: str, content: str, model: str, api_key: str, operation_name: str = "Projection Engine") -> str:
        """Process single request with Gemini using asyncio with timeout and retry logic"""
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
                if attempt == 0:
                    log_api_call(logger, operation_name, model, key_suffix, success=True)
                else:
                    logger.info(f"API call RETRY {attempt}/{self.max_retries}: {operation_name} | Model: {model} | Key: ...{key_suffix}")
                
                # Use new SDK client
                client = genai.Client(api_key=api_key)
                
                # Create text-based content (Stage 3 works with text analysis)
                if content:
                    contents = f"{content}\n\n{prompt}"
                    logger.debug(f"Request type: text + prompt | Content: {len(content)} chars | Prompt: {len(prompt)} chars")
                else:
                    contents = prompt
                    logger.debug(f"Request type: text-only | Prompt length: {len(prompt)} chars")
                
                # Apply timeout to the API call using new SDK
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model,
                        contents=contents
                    ),
                    timeout=self.api_timeout
                )
                
                elapsed_time = time.time() - start_time
                response_text = self.extract_response_text(response)
                
                # Log the full raw response for debugging (controlled by debug flag)
                if self.debug_responses:
                    logger.info(f"🔍 RAW RESPONSE from {operation_name}")
                    logger.info(f"📝 Response length: {len(response_text)} characters")
                    logger.info(f"📋 First 200 chars: {response_text[:200]}...")
                    logger.info(f"📋 Last 200 chars: ...{response_text[-200:]}")
                    logger.info(f"📋 FULL RESPONSE:\n{response_text}")
                
                log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=True)
                return response_text
                
            except asyncio.TimeoutError as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                logger.warning(f"API call TIMEOUT: {operation_name} | Attempt {attempt + 1}/{self.max_retries + 1} | Duration: {elapsed_time:.2f}s")
                
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(self.retry_delay)
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                error_str = str(e)
                
                # Check if this is a retryable error
                retryable_errors = [
                    "503 Service Temporarily Unavailable",
                    "502 Bad Gateway", 
                    "504 Gateway Timeout",
                    "429 Too Many Requests",
                    "500 Internal Server Error",
                    "500 An internal error has occurred"
                ]
                
                is_retryable = any(error in error_str for error in retryable_errors)
                
                if is_retryable and attempt < self.max_retries:
                    logger.warning(f"API call RETRYABLE ERROR: {operation_name} | Attempt {attempt + 1}/{self.max_retries + 1} | Error: {error_str}")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"API call NON-RETRYABLE ERROR: {operation_name} | Error: {error_str}")
                    break
        
        # If we reach here, all attempts failed
        elapsed_time = time.time() - start_time
        key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
        final_error = str(last_exception) if last_exception else "Unknown error"
        log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=False, error=final_error)
        raise last_exception or Exception("All retry attempts failed")
    
    def _extract_methodology_string(self, stage3_result: Dict) -> str:
        """Extract methodology information from stage3 result and return as string"""
        try:
            projection_methodology = stage3_result.get('projection_methodology', {})
            
            if not projection_methodology:
                return "ARIMA (fallback methodology due to limited analysis)"
            
            # Extract key components from projection methodology
            primary_method = projection_methodology.get('primary_method_applied', 'Unknown')
            integration_approach = projection_methodology.get('integration_approach', 'Standard approach')
            
            # Create meaningful string representation
            methodology_str = f"{primary_method}"
            if integration_approach and integration_approach != 'Standard approach':
                methodology_str += f" with {integration_approach}"
            
            logger.debug(f"Extracted methodology string: {methodology_str}")
            return methodology_str
            
        except Exception as e:
            logger.warning(f"Error extracting methodology string: {str(e)}")
            return "Mixed forecasting methodology (analysis incomplete)"

    def _extract_confidence_levels(self, stage3_result: Dict) -> Dict[str, str]:
        """Extract confidence levels from stage3 result and return as dictionary"""
        try:
            confidence_levels = {}
            base_projections = stage3_result.get('base_case_projections', {})
            
            # Extract confidence levels for each projection period
            for period_key, period_data in base_projections.items():
                if isinstance(period_data, dict):
                    # Try to get confidence from revenue data (first available)
                    revenue_data = period_data.get('revenue', [])
                    if revenue_data and isinstance(revenue_data, list) and len(revenue_data) > 0:
                        first_revenue = revenue_data[0]
                        if isinstance(first_revenue, dict):
                            confidence = first_revenue.get('confidence', 'medium')
                            confidence_levels[period_key] = confidence
                        else:
                            confidence_levels[period_key] = 'medium'
                    else:
                        confidence_levels[period_key] = 'medium'
                else:
                    confidence_levels[period_key] = 'medium'
            
            # If no confidence levels found, provide default structure
            if not confidence_levels:
                confidence_levels = {
                    '1_year_ahead': 'medium',
                    '3_years_ahead': 'medium',
                    '5_years_ahead': 'low',
                    '10_years_ahead': 'low',
                    '15_years_ahead': 'very_low'
                }
            
            logger.debug(f"Extracted confidence levels: {confidence_levels}")
            return confidence_levels
            
        except Exception as e:
            logger.warning(f"Error extracting confidence levels: {str(e)}")
            return {
                '1_year_ahead': 'medium',
                '3_years_ahead': 'medium',
                '5_years_ahead': 'low',
                '10_years_ahead': 'low',
                '15_years_ahead': 'very_low'
            }

    async def _semantic_validation_with_ai(self, projections: Dict, validation_results: Dict) -> None:
        """
        Enhanced semantic validation using Gemini 2.5 Flash for business logic checks
        This is a lightweight, cost-effective validation for catching unrealistic projections
        """
        try:
            logger.info("🤖 SEMANTIC VALIDATION: AI-powered business logic checks")
            
            # Extract key metrics for validation
            base_projections = projections.get('base_case_projections', {})
            if not base_projections:
                logger.debug("⚠️ No base projections found for semantic validation")
                return
            
            # Prepare lightweight context for AI validation
            validation_context = {
                "periods": list(base_projections.keys()),
                "metrics_summary": {}
            }
            
            # Extract key trends for validation (revenue, growth rates, margins)
            for period, data in base_projections.items():
                if isinstance(data, dict):
                    revenue_values = [item.get('value', 0) for item in data.get('revenue', [])]
                    expenses_values = [item.get('value', 0) for item in data.get('expenses', [])]
                    net_profit_values = [item.get('value', 0) for item in data.get('net_profit', [])]
                    
                    if revenue_values and expenses_values:
                        validation_context["metrics_summary"][period] = {
                            "revenue": revenue_values[0],
                            "expenses": expenses_values[0],
                            "net_profit": net_profit_values[0] if net_profit_values else 0,
                            "margin": (revenue_values[0] - expenses_values[0]) / max(revenue_values[0], 1) if revenue_values[0] > 0 else 0
                        }
            
            # Calculate growth rates for validation
            periods = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
            growth_rates = []
            
            for i in range(len(periods) - 1):
                current_period = periods[i]
                next_period = periods[i + 1]
                
                if current_period in validation_context["metrics_summary"] and next_period in validation_context["metrics_summary"]:
                    current_revenue = validation_context["metrics_summary"][current_period]["revenue"]
                    next_revenue = validation_context["metrics_summary"][next_period]["revenue"]
                    
                    if current_revenue > 0:
                        growth_rate = (next_revenue - current_revenue) / current_revenue
                        growth_rates.append({
                            "from": current_period,
                            "to": next_period,
                            "growth_rate": growth_rate
                        })
            
            # Lightweight prompt for semantic validation
            validation_prompt = f"""
TASK: Quick semantic validation of financial projections for business logic issues.

PROJECTIONS SUMMARY:
{json.dumps(validation_context["metrics_summary"], indent=2)}

GROWTH RATES:
{json.dumps(growth_rates, indent=2)}

VALIDATION CHECKS:
1. Are growth rates realistic for a typical business? (>500% annual growth is suspicious)
2. Are margin trends logical? (margins jumping from 10% to 80% without explanation is unrealistic)
3. Are there any obvious mathematical inconsistencies?
4. Do the numbers scale appropriately across time periods?

RESPOND WITH ONLY:
- "VALID" if projections seem reasonable
- "FLAG: [brief description]" if there's a significant business logic issue

Keep response under 100 words. Focus on major red flags only.
"""

            # Make lightweight API call to Gemini 2.5 Flash
            api_key = self.get_next_api_key()
            
            # Use Flash model for cost-effective validation
            response = await self.process_with_gemini(
                validation_prompt,
                "",
                "gemini-2.5-flash",  # Use Flash for cost efficiency
                api_key,
                "Semantic Validation"
            )
            
            # Parse AI response
            response_text = response.strip()
            
            if response_text.startswith("FLAG:"):
                flag_description = response_text[5:].strip()
                validation_results['warnings'].append(f"AI Semantic Check: {flag_description}")
                logger.warning(f"🚨 AI Semantic Flag: {flag_description}")
                
                # Log to console for visibility
                logger.info(f"🤖 SEMANTIC VALIDATION RESULT: FLAGGED")
                logger.info(f"📋 Issue: {flag_description}")
                
            elif response_text.startswith("VALID"):
                logger.info(f"✅ AI Semantic Validation: Projections appear reasonable")
                
            else:
                logger.debug(f"⚠️ Unexpected AI validation response: {response_text}")
            
        except Exception as e:
            # Non-blocking: if AI validation fails, we just skip it
            logger.debug(f"⚠️ AI semantic validation failed (non-blocking): {str(e)}")
            # Don't add to validation_results errors - this is optional enhancement

    def _validate_pnl_reconciliation(self, pnl_data: Dict, period: str, validation_results: Dict) -> None:
        """Validate P&L statement internal reconciliation"""
        try:
            # Check if calculation chains are present
            if 'revenue' in pnl_data and 'calculation_chain' not in pnl_data['revenue']:
                validation_results['warnings'].append(f"Missing calculation chain for revenue in {period}")
            
            # Basic P&L reconciliation checks
            if all(key in pnl_data for key in ['revenue', 'cost_of_goods_sold', 'gross_profit']):
                revenue = pnl_data['revenue'].get('value', 0)
                cogs = pnl_data['cost_of_goods_sold'].get('value', 0)
                gross_profit = pnl_data['gross_profit'].get('value', 0)
                
                expected_gross_profit = revenue - cogs
                variance = abs(gross_profit - expected_gross_profit) / max(abs(expected_gross_profit), 1)
                
                if variance > 0.05:  # 5% tolerance
                    validation_results['warnings'].append(f"Gross profit reconciliation variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ Gross profit reconciliation variance in {period}: {variance:.2%}")
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'gross_profit_reconciliation',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.05 else 'warning'
                })
            
            # Enhanced Net Profit Reconciliation - Full P&L Waterfall
            self._validate_full_pnl_waterfall(pnl_data, period, validation_results)
                
        except Exception as e:
            validation_results['warnings'].append(f"P&L validation error in {period}: {str(e)}")
            logger.debug(f"⚠️ P&L validation error in {period}: {str(e)}")
    
    def _validate_full_pnl_waterfall(self, pnl_data: Dict, period: str, validation_results: Dict) -> None:
        """Validate the complete P&L waterfall following proper accounting structure"""
        try:
            # P&L Waterfall Structure:
            # 1. Revenue - COGS = Gross Profit
            # 2. Gross Profit - Operating Expenses = EBITDA
            # 3. EBITDA - Depreciation = EBIT
            # 4. EBIT - Interest = PBT (Pre-tax)
            # 5. PBT - Tax = Net Profit
            
            # Extract values
            revenue = pnl_data.get('revenue', {}).get('value', 0)
            cogs = pnl_data.get('cost_of_goods_sold', {}).get('value', 0)
            gross_profit = pnl_data.get('gross_profit', {}).get('value', 0)
            ebitda = pnl_data.get('ebitda', {}).get('value', 0)
            depreciation = pnl_data.get('depreciation', {}).get('value', 0)
            ebit = pnl_data.get('ebit', {}).get('value', 0)
            interest_expense = pnl_data.get('interest_expense', {}).get('value', 0)
            net_profit_before_tax = pnl_data.get('net_profit_before_tax', {}).get('value', 0)
            tax_expense = pnl_data.get('tax_expense', {}).get('value', 0)
            net_profit = pnl_data.get('net_profit', {}).get('value', 0)
            
            # Get operating expenses
            opex = 0
            if 'operating_expenses' in pnl_data:
                opex_data = pnl_data['operating_expenses']
                if isinstance(opex_data, dict) and 'total_opex' in opex_data:
                    opex = opex_data['total_opex'].get('value', 0)
            
            # Validate Step 2: Gross Profit - OpEx = EBITDA
            if gross_profit != 0 and opex != 0 and ebitda != 0:
                expected_ebitda = gross_profit - opex
                variance = abs(ebitda - expected_ebitda) / max(abs(expected_ebitda), 1)
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'ebitda_reconciliation',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.05 else 'warning'
                })
                
                if variance > 0.05:
                    validation_results['warnings'].append(f"EBITDA reconciliation variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ EBITDA reconciliation variance in {period}: {variance:.2%}")
            
            # Validate Step 3: EBITDA - Depreciation = EBIT
            if ebitda != 0 and depreciation != 0 and ebit != 0:
                expected_ebit = ebitda - depreciation
                variance = abs(ebit - expected_ebit) / max(abs(expected_ebit), 1)
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'ebit_reconciliation',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.05 else 'warning'
                })
                
                if variance > 0.05:
                    validation_results['warnings'].append(f"EBIT reconciliation variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ EBIT reconciliation variance in {period}: {variance:.2%}")
            
            # Validate Step 4: EBIT - Interest = PBT
            if ebit != 0 and net_profit_before_tax != 0:
                expected_pbt = ebit - interest_expense
                variance = abs(net_profit_before_tax - expected_pbt) / max(abs(expected_pbt), 1)
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'pbt_reconciliation',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.05 else 'warning'
                })
                
                if variance > 0.05:
                    validation_results['warnings'].append(f"PBT reconciliation variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ PBT reconciliation variance in {period}: {variance:.2%}")
            
            # Validate Step 5: PBT - Tax = Net Profit (Final Check)
            if net_profit_before_tax != 0 and tax_expense != 0 and net_profit != 0:
                expected_net_profit = net_profit_before_tax - tax_expense
                variance = abs(net_profit - expected_net_profit) / max(abs(expected_net_profit), 1)
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'net_profit_reconciliation',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.05 else 'warning'
                })
                
                if variance > 0.05:
                    validation_results['warnings'].append(f"Net profit reconciliation variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ Net profit reconciliation variance in {period}: {variance:.2%}")
                else:
                    logger.debug(f"✅ Net profit reconciliation passed in {period}: {variance:.2%} variance")
            
            # Fallback: If detailed waterfall is not available, use simplified check
            elif gross_profit != 0 and net_profit != 0:
                # Simplified check: Account for all major deductions
                total_deductions = opex + depreciation + interest_expense + tax_expense
                expected_net_profit = gross_profit - total_deductions
                variance = abs(net_profit - expected_net_profit) / max(abs(expected_net_profit), 1)
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'net_profit_reconciliation_simplified',
                    'variance': variance,
                    'status': 'passed' if variance <= 0.10 else 'warning'  # Higher tolerance for simplified check
                })
                
                if variance > 0.10:
                    validation_results['warnings'].append(f"Net profit reconciliation (simplified) variance in {period}: {variance:.2%}")
                    logger.warning(f"⚠️ Net profit reconciliation (simplified) variance in {period}: {variance:.2%}")
                else:
                    logger.debug(f"✅ Net profit reconciliation (simplified) passed in {period}: {variance:.2%} variance")
            
        except Exception as e:
            validation_results['warnings'].append(f"P&L waterfall validation error in {period}: {str(e)}")
            logger.debug(f"⚠️ P&L waterfall validation error in {period}: {str(e)}")
    
    def _validate_cash_flow_reconciliation(self, cf_data: Dict, period: str, validation_results: Dict) -> None:
        """Validate cash flow statement internal reconciliation"""
        try:
            # Check if operating, investing, and financing activities sum to net change in cash
            if 'operating_activities' in cf_data and 'investing_activities' in cf_data and 'financing_activities' in cf_data:
                operating_cash = cf_data['operating_activities'].get('net_cash_from_operations', {}).get('value', 0)
                investing_cash = cf_data['investing_activities'].get('net_cash_from_investing', {}).get('value', 0)
                financing_cash = cf_data['financing_activities'].get('net_cash_from_financing', {}).get('value', 0)
                
                if 'net_change_in_cash' in cf_data:
                    reported_net_change = cf_data['net_change_in_cash'].get('value', 0)
                    calculated_net_change = operating_cash + investing_cash + financing_cash
                    
                    variance = abs(reported_net_change - calculated_net_change) / max(abs(calculated_net_change), 1)
                    
                    if variance > 0.05:  # 5% tolerance
                        validation_results['warnings'].append(f"Cash flow reconciliation variance in {period}: {variance:.2%}")
                        logger.warning(f"⚠️ Cash flow reconciliation variance in {period}: {variance:.2%}")
                    
                    validation_results['reconciliation_checks'].append({
                        'period': period,
                        'check': 'cash_flow_reconciliation',
                        'variance': variance,
                        'status': 'passed' if variance <= 0.05 else 'warning'
                    })
                    
        except Exception as e:
            validation_results['warnings'].append(f"Cash flow validation error in {period}: {str(e)}")
            logger.debug(f"⚠️ Cash flow validation error in {period}: {str(e)}")
    
    def _validate_balance_sheet_reconciliation(self, bs_data: Dict, period: str, validation_results: Dict) -> None:
        """Validate balance sheet balancing equation"""
        try:
            # Check if balance sheet balances (Assets = Liabilities + Equity)
            if 'balance_check' in bs_data:
                balance_status = bs_data['balance_check'].get('balance_status', 'UNBALANCED')
                variance = bs_data['balance_check'].get('variance', {}).get('value', 0)
                
                if balance_status == 'UNBALANCED' or abs(variance) > 0.01:
                    validation_results['errors'].append(f"Balance sheet does not balance in {period}: variance = {variance}")
                    validation_results['valid'] = False
                    logger.error(f"❌ Balance sheet does not balance in {period}: variance = {variance}")
                else:
                    logger.debug(f"✅ Balance sheet balances in {period}")
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'balance_sheet_balancing',
                    'variance': abs(variance),
                    'status': 'passed' if balance_status == 'BALANCED' and abs(variance) <= 0.01 else 'failed'
                })
            else:
                validation_results['warnings'].append(f"Missing balance check in {period}")
                
        except Exception as e:
            validation_results['warnings'].append(f"Balance sheet validation error in {period}: {str(e)}")
            logger.debug(f"⚠️ Balance sheet validation error in {period}: {str(e)}")
    
    def _validate_cross_statement_consistency(self, period_data: Dict, period: str, validation_results: Dict) -> None:
        """Validate consistency between the three financial statements"""
        try:
            pnl_data = period_data.get('profit_and_loss', [{}])[0]
            cf_data = period_data.get('cash_flow_statement', [{}])[0]
            bs_data = period_data.get('balance_sheet', [{}])[0]
            
            # Check if P&L net profit matches cash flow starting point
            if 'net_profit' in pnl_data and 'operating_activities' in cf_data:
                pnl_net_profit = pnl_data['net_profit'].get('value', 0)
                cf_net_income = cf_data['operating_activities'].get('net_income', {}).get('value', 0)
                
                if abs(pnl_net_profit - cf_net_income) > 0.01:
                    validation_results['warnings'].append(f"P&L net profit doesn't match cash flow net income in {period}")
                    logger.warning(f"⚠️ P&L net profit doesn't match cash flow net income in {period}")
                
                validation_results['reconciliation_checks'].append({
                    'period': period,
                    'check': 'pnl_to_cashflow_consistency',
                    'variance': abs(pnl_net_profit - cf_net_income),
                    'status': 'passed' if abs(pnl_net_profit - cf_net_income) <= 0.01 else 'warning'
                })
            
            # Additional cross-statement checks can be added here
            logger.debug(f"✅ Cross-statement consistency checks completed for {period}")
            
        except Exception as e:
            validation_results['warnings'].append(f"Cross-statement validation error in {period}: {str(e)}")
            logger.debug(f"⚠️ Cross-statement validation error in {period}: {str(e)}")

    async def local_validation(self, projections: Dict) -> Dict:
        """Enhanced validation and reconciliation with AI semantic checks"""
        logger.info(f"🔍 LOCAL VALIDATION: Financial Reconciliation & Consistency Checks")
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'reconciliation_checks': [],
            'consistency_scores': {}
        }
        
        try:
            # Check for required projection periods
            required_periods = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
            base_projections = projections.get('base_case_projections', {})
            
            logger.debug(f"🔍 Validating {len(base_projections)} projection periods against {len(required_periods)} required")
            
            for period in required_periods:
                if period not in base_projections:
                    validation_results['warnings'].append(f"Missing projection period: {period}")
                    logger.warning(f"⚠️ Missing projection period: {period}")
                else:
                    period_data = base_projections[period]
                    required_statements = ['profit_and_loss', 'cash_flow_statement', 'balance_sheet']
                    
                    for statement in required_statements:
                        if statement not in period_data:
                            validation_results['errors'].append(f"Missing {statement} in {period}")
                            validation_results['valid'] = False
                            logger.error(f"❌ Missing {statement} in {period}")
                        else:
                            statement_data = period_data[statement]
                            if isinstance(statement_data, list) and len(statement_data) > 0:
                                # Three-way forecast reconciliation checks
                                if statement == 'profit_and_loss':
                                    self._validate_pnl_reconciliation(statement_data[0], period, validation_results)
                                elif statement == 'cash_flow_statement':
                                    self._validate_cash_flow_reconciliation(statement_data[0], period, validation_results)
                                elif statement == 'balance_sheet':
                                    self._validate_balance_sheet_reconciliation(statement_data[0], period, validation_results)
                                
                                logger.debug(f"✅ Found {statement} in {period} with {len(statement_data)} data points")
                            else:
                                validation_results['errors'].append(f"Empty {statement} data in {period}")
                                validation_results['valid'] = False
                                logger.error(f"❌ Empty {statement} data in {period}")
                    
                    # Cross-statement validation
                    if all(stmt in period_data for stmt in required_statements):
                        self._validate_cross_statement_consistency(period_data, period, validation_results)
            
            # Cross-statement consistency checks
            if base_projections:
                validation_results['consistency_scores']['projection_completeness'] = len(base_projections) / len(required_periods)
                
                # Check for logical consistency across metrics
                total_checks = 0
                passed_checks = 0
                
                for period, data in base_projections.items():
                    if all(metric in data for metric in ['revenue', 'gross_profit', 'expenses']):
                        total_checks += 1
                        # Check if gross profit <= revenue
                        revenue_values = [item.get('value', 0) for item in data.get('revenue', [])]
                        gross_profit_values = [item.get('value', 0) for item in data.get('gross_profit', [])]
                        
                        if revenue_values and gross_profit_values:
                            if all(gp <= rev for gp, rev in zip(gross_profit_values, revenue_values)):
                                passed_checks += 1
                            else:
                                validation_results['warnings'].append(f"Gross profit > Revenue in {period}")
                
                if total_checks > 0:
                    validation_results['consistency_scores']['logical_consistency'] = passed_checks / total_checks
            
            # Basic validation score (before AI validation)
            error_weight = len(validation_results['errors']) * 0.5
            warning_weight = len(validation_results['warnings']) * 0.1
            basic_score = max(0, 1.0 - error_weight - warning_weight)
            
            logger.info(f"✅ Basic Validation Complete: Valid={validation_results['valid']}, Score={basic_score:.2f}, Warnings={len(validation_results['warnings'])}, Errors={len(validation_results['errors'])}")
            
            # AI Semantic Validation (non-blocking enhancement)
            await self._semantic_validation_with_ai(projections, validation_results)
            
            # Recalculate overall score after AI validation
            error_weight = len(validation_results['errors']) * 0.5
            warning_weight = len(validation_results['warnings']) * 0.1
            validation_results['overall_score'] = max(0, 1.0 - error_weight - warning_weight)
            
            logger.info(f"✅ Enhanced Validation Complete: Valid={validation_results['valid']}, Final Score={validation_results['overall_score']:.2f}, Total Warnings={len(validation_results['warnings'])}, Total Errors={len(validation_results['errors'])}")
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['valid'] = False
            logger.error(f"❌ Validation error: {str(e)}")
        
        return validation_results
    
    async def generate_projections(self, stage2_result: Dict, model: str = "gemini-2.5-pro") -> Dict[str, Any]:
        """
        Stage 3: Integrated projection engine with scenario planning
        
        Args:
            stage2_result: Result from Stage 2 business analysis
            model: Model to use for projections
            
        Returns:
            Dict containing financial projections and scenario planning
        """
        try:
            logger.info(f"🚀 STAGE 3: Projection Engine - Generating Financial Forecasts")
            
            api_key = self.get_next_api_key()
            
            template = string.Template(STAGE3_PROJECTION_PROMPT)
            context_prompt = template.substitute(
                stage2_analysis_output=json.dumps(stage2_result, indent=2)
            )
            
            logger.debug(f"📈 Projection context prepared: {len(context_prompt)} characters")
            
            response = await self.process_with_gemini(
                context_prompt,
                "",
                model,
                api_key,
                "Stage 3: Projection Engine"
            )
            
            # Parse response with multiple strategies
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 3 - Attempting JSON parsing for projections")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                # Strategy 1: Look for JSON in code blocks
                json_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
                if json_blocks:
                    if self.debug_responses:
                        logger.info(f"✅ Found JSON in code blocks: {len(json_blocks)} blocks")
                    result = json.loads(json_blocks[0])
                    projections_count = len(result.get('base_case_projections', {}))
                    logger.info(f"✅ Stage 3 Success: Generated {projections_count} projection horizons")
                    return result

                # Strategy 2: Look for the first JSON object in the text
                if self.debug_responses:
                    logger.info("⚠️ No JSON code blocks found, searching for raw JSON")
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    if self.debug_responses:
                        logger.info(f"✅ Found raw JSON match: {json_match.group(0)[:200]}...")
                    result = json.loads(json_match.group(0))
                    projections_count = len(result.get('base_case_projections', {}))
                    logger.info(f"✅ Stage 3 Success: Generated {projections_count} projection horizons")
                    return result

                # Strategy 3: Fallback structure
                logger.warning("⚠️ No JSON found in Stage 3 response, using fallback structure")
                return {
                    "projection_methodology": {
                        "primary_method_applied": stage2_result.get('methodology_evaluation', {}).get('selected_method', {}).get('primary_method', 'ARIMA'),
                        "integration_approach": "Fallback projections due to parsing issues"
                    },
                    "base_case_projections": {},
                    "scenario_projections": {"optimistic": {}, "conservative": {}},
                    "assumption_documentation": {"critical_assumptions": []},
                    "executive_summary": "Projection generation completed with fallback structure",
                    "raw_projections": response
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parsing failed in Stage 3: {str(e)}")
                return {
                    "projection_methodology": {"primary_method_applied": "fallback", "integration_approach": "Error recovery"},
                    "raw_projections": response,
                    "error": str(e)
                }

        except Exception as e:
            logger.error(f"❌ Stage 3 projection generation failed: {str(e)}")
            return {"error": str(e)}
    
    def get_methodology_string(self, stage3_result: Dict) -> str:
        """Get methodology string from Stage 3 result"""
        return self._extract_methodology_string(stage3_result)
    
    def get_confidence_levels(self, stage3_result: Dict) -> Dict[str, str]:
        """Get confidence levels from Stage 3 result"""
        return self._extract_confidence_levels(stage3_result)
    
    async def validate_projections(self, projections: Dict) -> Dict:
        """Validate projections for consistency and completeness"""
        return await self.local_validation(projections)

# Create projection service instance
projection_service = ProjectionService() 