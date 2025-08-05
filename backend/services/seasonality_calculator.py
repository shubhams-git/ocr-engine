"""
Enhanced Seasonality Calculator for Australian Plumbing/HVAC Business
Implements realistic month-to-month variations with industry-specific patterns
"""
import math
from typing import Dict, List, Tuple, Optional, Any
from logging_config import get_logger

logger = get_logger(__name__)

class AustralianPlumbingHVACSeasonality:
    """
    Australian plumbing/HVAC business seasonality calculator with realistic patterns
    Incorporates climate, holiday periods, and working capital timing effects
    """
    
    def __init__(self):
        # Australian seasonal patterns for plumbing/HVAC
        # Index 0 = January, 11 = December
        self.base_seasonal_factors = {
            'revenue': [
                0.75,  # Jan: Holiday period, emergency only (-25%)
                0.95,  # Feb: Gradual recovery, short month (-5%)
                1.10,  # Mar: Full capacity, pre-winter prep (+10%)
                1.05,  # Apr: Moderate activity (+5%)
                1.00,  # May: Baseline (0%)
                1.15,  # Jun: Winter peak, heating issues (+15%)
                1.20,  # Jul: Peak winter demand (+20%)
                1.10,  # Aug: Continued winter activity (+10%)
                1.05,  # Sep: Transition to spring (+5%)
                1.00,  # Oct: Baseline (0%)
                1.05,  # Nov: Pre-summer maintenance (+5%)
                0.85   # Dec: Holiday slowdown (-15%)
            ],
            'direct_costs': [
                0.80,  # Jan: Reduced material usage
                0.95,  # Feb: Gradual increase
                1.08,  # Mar: Material costs rise with activity
                1.03,  # Apr: Slight increase
                1.00,  # May: Baseline
                1.12,  # Jun: Higher material costs (winter demand)
                1.18,  # Jul: Peak material usage
                1.08,  # Aug: Continued high usage
                1.03,  # Sep: Normalizing
                1.00,  # Oct: Baseline
                1.02,  # Nov: Slight increase
                0.88   # Dec: Reduced activity
            ],
            'overhead': [
                1.05,  # Jan: Higher per-job costs (holiday rates)
                1.00,  # Feb: Normalizing
                0.98,  # Mar: Efficiency gains with volume
                1.00,  # Apr: Baseline
                1.00,  # May: Baseline
                1.02,  # Jun: Slight increase (emergency call-outs)
                1.03,  # Jul: Higher emergency rates
                1.01,  # Aug: Moderate increase
                1.00,  # Sep: Baseline
                1.00,  # Oct: Baseline
                1.00,  # Nov: Baseline
                1.05   # Dec: Holiday premium costs
            ]
        }
        
        # Holiday period adjustments (additional impact)
        self.holiday_adjustments = {
            'january': {
                'description': 'New Year holiday period + summer holidays',
                'revenue_impact': -0.10,  # Additional -10% beyond base seasonality
                'expense_timing_delay': 5,  # Days delay in expense recognition
                'working_capital_impact': 0.15  # 15% increase in DSO
            },
            'december': {
                'description': 'Christmas/holiday period impact',
                'revenue_impact': -0.05,  # Additional -5% beyond base seasonality
                'expense_timing_delay': 3,  # Days delay
                'working_capital_impact': 0.10  # 10% increase in DSO
            }
        }
        
        # Working capital timing patterns
        self.working_capital_patterns = {
            'dso_seasonal_variation': [15, 12, 8, 10, 10, 12, 14, 12, 10, 10, 11, 18],  # Days by month
            'dpo_seasonal_variation': [25, 22, 20, 22, 22, 24, 25, 23, 22, 22, 23, 30]   # Days by month
        }
        
        logger.info("🌡️ Australian Plumbing/HVAC Seasonality Calculator initialized")
        logger.debug(f"Base seasonal factors loaded for {len(self.base_seasonal_factors)} metrics")
    
    def get_monthly_factors(self, business_type: str = "plumbing_hvac") -> Dict[str, List[float]]:
        """
        Get monthly seasonality factors for different business metrics
        
        Args:
            business_type: Type of business ("plumbing_hvac", "general_service", etc.)
            
        Returns:
            Dictionary with seasonality factors for each metric
        """
        if business_type == "plumbing_hvac":
            return self.base_seasonal_factors.copy()
        else:
            # Fallback to generic service business patterns
            logger.warning(f"Business type '{business_type}' not specifically supported, using generic patterns")
            return self._get_generic_service_factors()
    
    def _get_generic_service_factors(self) -> Dict[str, List[float]]:
        """Fallback generic service business seasonality"""
        return {
            'revenue': [0.90, 0.95, 1.05, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.95],
            'direct_costs': [0.92, 0.96, 1.03, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.97],
            'overhead': [1.02, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.02]
        }
    
    def apply_q1_realism(self, base_values: List[float], metric_type: str = "revenue") -> List[float]:
        """
        Apply realistic Q1 variations to remove uniform patterns
        
        Args:
            base_values: List of 3 values for Jan, Feb, Mar
            metric_type: Type of metric ("revenue", "direct_costs", "overhead")
            
        Returns:
            Adjusted Q1 values with realistic variation
        """
        if len(base_values) != 3:
            logger.error(f"Expected 3 Q1 values, got {len(base_values)}")
            return base_values
        
        # Get seasonality factors for Q1 (Jan, Feb, Mar)
        seasonal_factors = self.base_seasonal_factors.get(metric_type, [1.0, 1.0, 1.0])[:3]
        
        # Apply seasonality
        adjusted_values = []
        for i, (base_val, seasonal_factor) in enumerate(zip(base_values, seasonal_factors)):
            adjusted_val = base_val * seasonal_factor
            
            # Apply holiday adjustments for January and March (if December rollover effects)
            if i == 0:  # January
                holiday_impact = self.holiday_adjustments['january']['revenue_impact']
                if metric_type == 'revenue':
                    adjusted_val *= (1 + holiday_impact)
            
            adjusted_values.append(adjusted_val)
        
        # Validation: Ensure minimum variance between months
        self._validate_q1_variance(adjusted_values, metric_type)
        
        logger.debug(f"Q1 {metric_type} seasonality applied: {[f'{v:,.0f}' for v in adjusted_values]}")
        return adjusted_values
    
    def _validate_q1_variance(self, values: List[float], metric_type: str) -> None:
        """Validate that Q1 has sufficient month-to-month variance"""
        if len(values) < 2:
            return
            
        # Calculate month-over-month variance
        variances = []
        for i in range(1, len(values)):
            variance = abs(values[i] - values[i-1]) / values[i-1]
            variances.append(variance)
        
        min_variance = min(variances)
        avg_variance = sum(variances) / len(variances)
        
        # Import from config for validation threshold
        try:
            from config import MINIMUM_MONTHLY_VARIANCE
            threshold = MINIMUM_MONTHLY_VARIANCE
        except ImportError:
            threshold = 0.05  # 5% fallback threshold
        
        if min_variance < threshold:
            logger.warning(f"⚠️ Q1 {metric_type} variance ({min_variance:.1%}) below threshold ({threshold:.1%})")
        else:
            logger.debug(f"✅ Q1 {metric_type} variance validation passed: min={min_variance:.1%}, avg={avg_variance:.1%}")
    
    def get_working_capital_timing_adjustment(self, month: int, metric_type: str) -> float:
        """
        Get working capital timing adjustment for specific month
        
        Args:
            month: Month number (1-12)
            metric_type: Type of adjustment needed
            
        Returns:
            Timing adjustment factor
        """
        month_idx = month - 1  # Convert to 0-based index
        
        if metric_type == "dso_adjustment":
            base_dso = 15  # Base DSO in days
            seasonal_dso = self.working_capital_patterns['dso_seasonal_variation'][month_idx]
            return seasonal_dso / base_dso
        
        elif metric_type == "dpo_adjustment":
            base_dpo = 22  # Base DPO in days
            seasonal_dpo = self.working_capital_patterns['dpo_seasonal_variation'][month_idx]
            return seasonal_dpo / base_dpo
        
        return 1.0  # No adjustment
    
    def get_calibration_report(self, historical_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate calibration report showing seasonality adjustments and rationale
        
        Args:
            historical_data: Optional historical monthly data for comparison
            
        Returns:
            Detailed calibration report
        """
        report = {
            "seasonality_methodology": {
                "approach": "Australian Plumbing/HVAC Industry-Specific Patterns",
                "data_sources": [
                    "Australian climate patterns",
                    "HVAC demand seasonality",
                    "Holiday period impacts",
                    "Working capital timing variations"
                ],
                "validation_approach": "Month-over-month variance thresholds with business logic validation"
            },
            "monthly_factor_summary": {},
            "q1_specific_adjustments": {
                "january": {
                    "revenue_factor": self.base_seasonal_factors['revenue'][0],
                    "rationale": "Holiday period + emergency-only services",
                    "additional_adjustments": self.holiday_adjustments['january']
                },
                "february": {
                    "revenue_factor": self.base_seasonal_factors['revenue'][1],
                    "rationale": "Short month + gradual recovery from holidays"
                },
                "march": {
                    "revenue_factor": self.base_seasonal_factors['revenue'][2],
                    "rationale": "Full capacity return + pre-winter preparation work"
                }
            },
            "working_capital_impacts": {
                "dso_seasonal_pattern": "Higher in holiday periods (Jan: +20%, Dec: +10%)",
                "dpo_seasonal_pattern": "Extended during holiday periods for supplier relationships",
                "cash_flow_timing": "Expense recognition delays during holiday periods"
            }
        }
        
        # Add monthly factor summary
        for metric, factors in self.base_seasonal_factors.items():
            report["monthly_factor_summary"][metric] = {
                "min_factor": min(factors),
                "max_factor": max(factors),
                "peak_months": [i+1 for i, f in enumerate(factors) if f == max(factors)],
                "trough_months": [i+1 for i, f in enumerate(factors) if f == min(factors)],
                "seasonal_amplitude": max(factors) - min(factors)
            }
        
        logger.info("📊 Seasonality calibration report generated")
        return report


class SeasonalityValidator:
    """Validates seasonality patterns and projection consistency"""
    
    @staticmethod
    def validate_period_completeness(projections: Dict, start_year: int) -> Dict[str, bool]:
        """Validate that projections start from correct calendar year"""
        results = {"period_completeness": True, "errors": []}
        
        try:
            monthly_data = projections.get("base_case_projections", {}).get("1_year_ahead", {})
            first_period = monthly_data.get("revenue", [{}])[0].get("period", "")
            
            expected_start = f"{start_year}-01"
            if not first_period.startswith(expected_start):
                results["period_completeness"] = False
                results["errors"].append(f"Expected start period {expected_start}, got {first_period}")
                
        except Exception as e:
            results["period_completeness"] = False
            results["errors"].append(f"Period validation error: {str(e)}")
        
        return results
    
    @staticmethod
    def validate_q1_variance(q1_values: List[float], metric_name: str, threshold: float = 0.05) -> Dict[str, Any]:
        """Validate Q1 has sufficient month-to-month variance"""
        if len(q1_values) != 3:
            return {"valid": False, "error": f"Expected 3 Q1 values, got {len(q1_values)}"}
        
        variances = []
        for i in range(1, len(q1_values)):
            variance = abs(q1_values[i] - q1_values[i-1]) / q1_values[i-1]
            variances.append(variance)
        
        min_variance = min(variances)
        avg_variance = sum(variances) / len(variances)
        
        return {
            "valid": min_variance >= threshold,
            "min_variance": min_variance,
            "avg_variance": avg_variance,
            "threshold": threshold,
            "metric": metric_name,
            "values": q1_values
        }
    
    @staticmethod
    def validate_aggregation_consistency(monthly_values: List[float], quarterly_total: float, tolerance: float = 0.01) -> Dict[str, Any]:
        """Validate monthly values aggregate correctly to quarterly totals"""
        calculated_total = sum(monthly_values)
        variance = abs(calculated_total - quarterly_total) / quarterly_total
        
        return {
            "consistent": variance <= tolerance,
            "calculated_total": calculated_total,
            "expected_total": quarterly_total,
            "variance": variance,
            "tolerance": tolerance
        }


# Factory function for easy integration
def create_seasonality_calculator(business_type: str = "plumbing_hvac") -> AustralianPlumbingHVACSeasonality:
    """Factory function to create appropriate seasonality calculator"""
    return AustralianPlumbingHVACSeasonality()