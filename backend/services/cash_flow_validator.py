"""
Enhanced Cash Flow Validator - Provides improved validation logic with depreciation quality awareness
Replaces the simplistic RECLASS_DRAWINGS default with intelligent classification
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
# Import concrete type for type checking
from services.enhanced_depreciation import DepreciationEstimate

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Structured validation result for a single period"""
    status: str  # PASS, WARN, FAIL
    variance: float
    tolerance_used: float
    flags: List[str]
    reasons: List[Dict[str, Any]]
    quality_score: float
    recommendations: List[str]

class EnhancedCashFlowValidator:
    """
    Enhanced validation logic that considers depreciation estimation quality
    Provides intelligent variance classification instead of defaulting to RECLASS_DRAWINGS
    """
    
    def __init__(self, base_tolerance_aud: float = 1000, base_tolerance_pct: float = 0.02):
        self.base_tolerance_aud = base_tolerance_aud
        self.base_tolerance_pct = base_tolerance_pct
        
        logger.debug(f"Enhanced cash flow validator initialized | "
                    f"Base tolerance: ${base_tolerance_aud} or {base_tolerance_pct:.1%}")
    
    def validate_period(self,
                       period_data: Dict,
                       dep_estimate: DepreciationEstimate) -> ValidationResult:
        """
        Enhanced validation for a single period with depreciation quality consideration
        
        Args:
            period_data: Period cash flow data
            dep_estimate: Depreciation estimation metadata
            
        Returns:
            ValidationResult with enhanced classification
        """
        
        try:
            # Extract cash flow components
            ocf = period_data.get('ocf', 0)
            icf = period_data.get('icf', 0)
            fcf = period_data.get('fcf', 0)
            delta_cash = period_data.get('delta_cash', 0)
            period_name = period_data.get('period', 'Unknown')
            
            # Calculate variance (fundamental cash flow equation)
            calculated_cash_change = ocf + icf + fcf
            variance = abs(calculated_cash_change - delta_cash)
            
            logger.debug(f"Validating {period_name}: OCF={ocf}, ICF={icf}, FCF={fcf}, "
                        f"ΔCash={delta_cash}, Variance={variance}")
            
            # Calculate dynamic tolerance based on depreciation confidence
            base_tolerance = max(self.base_tolerance_aud, abs(delta_cash) * self.base_tolerance_pct)
            
            # Apply depreciation confidence multiplier (KEY ENHANCEMENT)
            if dep_estimate.confidence < 0.5:
                tolerance = base_tolerance * 3.0  # Very lenient for poor depreciation
                tolerance_description = "relaxed (poor depreciation data)"
            elif dep_estimate.confidence < 0.75:
                tolerance = base_tolerance * 2.0  # Moderately lenient
                tolerance_description = "moderate (fair depreciation data)"
            else:
                tolerance = base_tolerance  # Standard tolerance for good depreciation
                tolerance_description = "standard (good depreciation data)"
            
            logger.debug(f"Tolerance for {period_name}: ${tolerance:.0f} ({tolerance_description})")
            
            # Enhanced status determination with intelligent classification
            flags = []
            reasons = []
            recommendations = []
            
            # Depreciation quality flags
            if dep_estimate.confidence < 0.75:
                flags.append("DEPR_ESTIMATED")
                reasons.append({
                    "code": "DEPR_ESTIMATED",
                    "message": f"Depreciation estimated using {dep_estimate.method_used} "
                              f"(confidence: {dep_estimate.confidence:.1%})",
                    "impact": dep_estimate.monthly_amount
                })
            
            # Enhanced variance classification (REPLACES SIMPLISTIC RECLASS_DRAWINGS)
            if variance <= tolerance:
                status = "PASS"
                quality_score = min(1.0, 1.0 - (variance / tolerance) * 0.3)  # Cap penalty at 30%
                
                if variance > tolerance * 0.5:
                    flags.append("MINOR_VARIANCE")
                    reasons.append({
                        "code": "MINOR_VARIANCE",
                        "message": f"Small variance ${variance:,.0f} within acceptable tolerance",
                        "impact": variance
                    })
                
            elif variance <= tolerance * 1.5:
                status = "WARN"
                flags.append("WARN")
                quality_score = max(0.3, 0.7 - (variance / (tolerance * 2)))
                
                # INTELLIGENT VARIANCE CLASSIFICATION (replaces flat RECLASS_DRAWINGS)
                if self._is_likely_owner_drawings(period_data, variance):
                    flags.append("RECLASS_DRAWINGS")
                    reasons.append({
                        "code": "RECLASS_DRAWINGS",
                        "message": f"Financing adjustment ${fcf:,.0f} suggests owner drawings pattern",
                        "impact": abs(fcf)
                    })
                elif self._is_likely_data_quality_issue(period_data, dep_estimate, variance):
                    flags.append("DATA_QUALITY_ISSUE")
                    reasons.append({
                        "code": "DATA_QUALITY_ISSUE",
                        "message": f"Variance ${variance:,.0f} likely due to data estimation issues",
                        "impact": variance
                    })
                    recommendations.append("Improve source data quality for better accuracy")
                elif self._is_likely_working_capital_anomaly(period_data, variance):
                    flags.append("WC_ANOMALY")
                    reasons.append({
                        "code": "WC_ANOMALY",
                        "message": f"Working capital movements appear irregular",
                        "impact": variance
                    })
                    recommendations.append("Review working capital assumptions and seasonality")
                else:
                    # Default to calculation error for moderate variances
                    flags.append("CALC_ERROR")
                    reasons.append({
                        "code": "CALC_ERROR",
                        "message": f"Moderate variance ${variance:,.0f} requires investigation",
                        "impact": variance
                    })
                    recommendations.append("Review cash flow calculation methodology")
                
            else:  # variance > tolerance * 1.5
                status = "FAIL"
                flags.append("FAIL")
                quality_score = 0.0
                
                if variance > 10000:  # Large variance
                    flags.append("INVESTIGATION_REQUIRED")
                    reasons.append({
                        "code": "INVESTIGATION_REQUIRED",
                        "message": f"Excessive variance ${variance:,.0f} requires immediate investigation",
                        "impact": variance
                    })
                    recommendations.append("URGENT: Investigate source data and calculation methodology")
                elif dep_estimate.confidence < 0.5:
                    flags.append("SEVERE_DATA_ISSUES")
                    reasons.append({
                        "code": "SEVERE_DATA_ISSUES",
                        "message": f"Poor data quality combined with large variance ${variance:,.0f}",
                        "impact": variance
                    })
                    recommendations.append("CRITICAL: Improve data collection and validation processes")
                else:
                    flags.append("CALC_ERROR")
                    reasons.append({
                        "code": "CALC_ERROR",
                        "message": f"Large calculation error - variance ${variance:,.0f} exceeds tolerance",
                        "impact": variance
                    })
                    recommendations.append("Review and validate cash flow reconstruction methodology")
            
            return ValidationResult(
                status=status,
                variance=variance,
                tolerance_used=tolerance,
                flags=flags,
                reasons=reasons,
                quality_score=max(0, quality_score),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error validating period {period_data.get('period', 'unknown')}: {str(e)}")
            return ValidationResult(
                status="FAIL",
                variance=float('inf'),
                tolerance_used=self.base_tolerance_aud,
                flags=["VALIDATION_ERROR"],
                reasons=[{
                    "code": "VALIDATION_ERROR",
                    "message": f"Validation failed: {str(e)}",
                    "impact": 0
                }],
                quality_score=0.0,
                recommendations=["Fix validation error and retry"]
            )
    
    def _is_likely_owner_drawings(self, period_data: Dict, variance: float) -> bool:
        """Determine if variance pattern suggests owner drawings"""
        try:
            fcf = period_data.get('fcf', 0)
            ni = period_data.get('ni', 0)
            
            # Strong negative FCF with positive NI often indicates owner drawings
            if fcf < -5000 and ni > 0:
                # FCF magnitude is significant portion of NI
                if abs(fcf) > ni * 0.5:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _is_likely_data_quality_issue(self, period_data: Dict,
                                     dep_estimate: DepreciationEstimate,
                                     variance: float) -> bool:
        """Determine if variance likely due to data quality issues"""
        try:
            # Low depreciation confidence combined with moderate variance
            if dep_estimate.confidence < 0.6 and 1000 < variance < 5000:
                return True
            
            # Depreciation method indicates estimation
            if dep_estimate.method_used in ["revenue_percentage_fallback", "conservative_fallback"]:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _is_likely_working_capital_anomaly(self, period_data: Dict, variance: float) -> bool:
        """Determine if variance suggests working capital anomalies"""
        try:
            # Check for unusual working capital movements
            delta_ar = period_data.get('delta_ar', 0)
            delta_inventory = period_data.get('delta_inventory', 0)
            delta_ap = period_data.get('delta_ap', 0)
            
            total_wc_movement = abs(delta_ar) + abs(delta_inventory) + abs(delta_ap)
            
            # Large working capital movements might explain variance
            if total_wc_movement > variance * 0.8:
                return True
            
            return False
            
        except Exception:
            return False
    
    def validate_full_cash_flow_result(self,
                                     result: Dict,
                                     dep_estimate: DepreciationEstimate) -> Dict[str, Any]:
        """
        Validate complete cash flow result with enhanced metrics
        
        Returns:
            Enhanced quality assessment dictionary
        """
        
        try:
            periods = result.get('periods', [])
            total_periods = len(periods)
            
            if total_periods == 0:
                return {
                    "global_score": 0.0,
                    "status": "NO_DATA",
                    "recommendation": "No periods available for validation",
                    "period_counts": {"pass": 0, "warn": 0, "fail": 0},
                    "reconciliation_pass_rate": 0.0
                }
            
            logger.info(f"Validating complete cash flow result with {total_periods} periods")
            
            # Validate each period
            validation_results = []
            for period in periods:
                period_validation = self.validate_period(period, dep_estimate)
                validation_results.append(period_validation)
            
            # Aggregate results
            pass_count = sum(1 for v in validation_results if v.status == "PASS")
            warn_count = sum(1 for v in validation_results if v.status == "WARN") 
            fail_count = sum(1 for v in validation_results if v.status == "FAIL")
            
            # Calculate aggregate quality score
            if validation_results:
                avg_quality_score = np.mean([v.quality_score for v in validation_results])
            else:
                avg_quality_score = 0.0
            
            # Apply global penalties based on systematic issues
            depreciation_penalty = 0.0
            if dep_estimate.confidence < 0.7:
                depreciation_penalty = 0.2  # 20% penalty for poor depreciation
            elif dep_estimate.confidence < 0.5:
                depreciation_penalty = 0.3  # 30% penalty for very poor depreciation
            
            excessive_failures_penalty = 0.0
            if fail_count > total_periods * 0.2:  # More than 20% failures
                excessive_failures_penalty = 0.2
            
            # Calculate global score with penalties
            global_score = max(0, avg_quality_score - depreciation_penalty - excessive_failures_penalty)
            
            # Determine overall status
            if global_score >= 0.8:
                overall_status = "EXCELLENT"
            elif global_score >= 0.6:
                overall_status = "GOOD"
            elif global_score >= 0.4:
                overall_status = "ACCEPTABLE"
            elif global_score >= 0.2:
                overall_status = "POOR"
            else:
                overall_status = "FAILED"
            
            logger.info(f"Global validation result: Score={global_score:.2f}, Status={overall_status}")
            logger.info(f"Period breakdown: Pass={pass_count}, Warn={warn_count}, Fail={fail_count}")
            
            # Aggregate recommendations from period results
            aggregated_recos: List[str] = []
            for v in validation_results:
                # Common suggestions based on flags
                if "DATA_QUALITY_ISSUE" in v.flags:
                    aggregated_recos.append("Improve source data quality for better accuracy")
                if "WC_ANOMALY" in v.flags:
                    aggregated_recos.append("Review working capital assumptions and seasonality")
                if "INVESTIGATION_REQUIRED" in v.flags:
                    aggregated_recos.append("URGENT: Investigate source data and calculation methodology")
                if "CALC_ERROR" in v.flags:
                    aggregated_recos.append("Review cash flow calculation methodology")
                # Include any explicit recommendations attached
                if hasattr(v, "recommendations") and isinstance(v.recommendations, list):
                    aggregated_recos.extend([str(r) for r in v.recommendations])
            # Deduplicate while preserving order
            seen = set()
            aggregated_recos = [r for r in aggregated_recos if not (r in seen or seen.add(r))]
            
            return {
                "global_score": round(float(global_score), 3),
                "status": overall_status,
                "summary": {
                    "period_counts": {
                        "pass": pass_count,
                        "warn": warn_count,
                        "fail": fail_count
                    },
                    "reconciliation_pass_rate": (pass_count / total_periods) if total_periods > 0 else 0.0,
                    "avg_recon_delta_abs": float(np.mean([v.variance for v in validation_results])) if validation_results else 0.0
                },
                "depreciation_analysis": {
                    "method": dep_estimate.method_used,
                    "monthly_amount": float(dep_estimate.monthly_amount),
                    "confidence": float(dep_estimate.confidence),
                    "annual_rate": float(dep_estimate.annual_rate)
                },
                "recommendations": aggregated_recos,
                "period_results": [
                    {
                        "status": v.status,
                        "variance": float(v.variance),
                        "tolerance_used": float(v.tolerance_used),
                        "quality_score": float(v.quality_score),
                        "flags": v.flags,
                        "reasons": v.reasons
                    } for v in validation_results
                ]
            }
        except Exception as e:
            logger.error(f"Error validating full cash flow result: {str(e)}")
            return {
                "global_score": 0.0,
                "status": "ERROR",
                "summary": {
                    "period_counts": {"pass": 0, "warn": 0, "fail": 0},
                    "reconciliation_pass_rate": 0.0,
                    "avg_recon_delta_abs": 0.0
                },
                "error": f"Validation failed: {str(e)}"
            }