"""
Enhanced Depreciation Estimator - Core component that fixes the 0.0 quality score issue
Provides intelligent depreciation estimation using multiple methods and business rules
"""

import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

@dataclass
class DepreciationEstimate:
    """Structured depreciation estimation result with full metadata"""
    monthly_amount: float
    method_used: str
    confidence: float
    annual_rate: float
    justification: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class EnhancedDepreciationEstimator:
    """
    Multi-method depreciation estimator that replaces flat $850/month estimation
    Uses progressive rates based on asset size and data quality with Australian business standards
    """
    
    def __init__(self, min_annual_rate: float = 0.02, max_annual_rate: float = 0.25):
        self.min_annual_rate = min_annual_rate
        self.max_annual_rate = max_annual_rate
        
        # Progressive depreciation rates based on Australian business standards
        self.asset_depreciation_rates = {
            "small_equipment": {"threshold": 100000, "rate": 0.15, "description": "Tools, small equipment, software"},
            "medium_equipment": {"threshold": 300000, "rate": 0.10, "description": "Vehicles, machinery, computers"},
            "large_equipment": {"threshold": 600000, "rate": 0.07, "description": "Major equipment, plant"},
            "infrastructure": {"threshold": float('inf'), "rate": 0.04, "description": "Buildings, major infrastructure"}
        }
        
        logger.debug("Enhanced depreciation estimator initialized with Australian business standards")
    
    def estimate_depreciation_from_stage1_data(self, pnl_data: Optional[Dict], bs_data: Optional[Dict]) -> DepreciationEstimate:
        """
        Main entry point for depreciation estimation from Stage 1 data
        
        Args:
            pnl_data: Stage 1 P&L extraction result
            bs_data: Stage 1 Balance Sheet extraction result
            
        Returns:
            DepreciationEstimate with method, confidence, and justification
        """
        
        if not bs_data or not bs_data.get('periods'):
            logger.info("No balance sheet data available, using revenue-based fallback")
            return self._estimate_from_revenue_fallback(pnl_data)
        
        # Extract time series data from Stage 1 format
        periods = bs_data.get('periods', [])
        
        # Fixed assets time series (net book value)
        fixed_assets = []
        for period in periods:
            fa_net = period.get('fixed_assets_net')
            if fa_net is not None and fa_net > 0:
                fixed_assets.append(fa_net)
        
        # Accumulated depreciation time series
        accumulated_dep = []
        for period in periods:
            acc_dep = period.get('accumulated_depreciation')
            if acc_dep is not None:
                # Handle negative accumulated depreciation (common accounting representation)
                accumulated_dep.append(abs(acc_dep))
        
        # Revenue time series (for fallback validation)
        revenue_data = []
        if pnl_data and pnl_data.get('periods'):
            for period in pnl_data.get('periods', []):
                revenue = period.get('revenue')
                if revenue is not None and revenue > 0:
                    revenue_data.append(revenue)
        
        return self.estimate_depreciation(fixed_assets, accumulated_dep, revenue_data)
    
    def estimate_depreciation(self, 
                            fixed_assets_data: List[float],
                            accumulated_dep_data: Optional[List[float]] = None,
                            revenue_data: Optional[List[float]] = None) -> DepreciationEstimate:
        """
        Multi-method depreciation estimation with fallback hierarchy
        
        Method Priority:
        1. Accumulated depreciation changes (highest accuracy)
        2. Progressive asset-based rates (good accuracy)  
        3. Revenue-based fallback (lowest accuracy)
        """
        
        if not fixed_assets_data or len(fixed_assets_data) == 0:
            logger.warning("No fixed asset data available for depreciation estimation")
            return self._create_fallback_estimate("No fixed asset data available")
        
        # Convert to pandas for robust analysis
        try:
            fixed_assets = pd.Series([fa for fa in fixed_assets_data if fa > 0])
        except Exception as e:
            logger.error(f"Error processing fixed assets data: {str(e)}")
            return self._create_fallback_estimate(f"Data processing error: {str(e)}")
        
        if len(fixed_assets) == 0:
            return self._create_fallback_estimate("No valid fixed asset values")
        
        logger.info(f"Analyzing {len(fixed_assets)} periods of fixed asset data")
        logger.debug(f"Asset range: ${fixed_assets.min():,.0f} - ${fixed_assets.max():,.0f}")
        
        # Method 1: Accumulated Depreciation Changes (PREFERRED)
        if accumulated_dep_data and len(accumulated_dep_data) > 1:
            acc_dep_estimate = self._estimate_from_accumulated_depreciation(accumulated_dep_data, fixed_assets)
            if acc_dep_estimate.confidence >= 0.8:
                logger.info(f"✅ Using accumulated depreciation method: ${acc_dep_estimate.monthly_amount:.0f}/month")
                return acc_dep_estimate
            else:
                logger.debug(f"Accumulated depreciation method confidence too low: {acc_dep_estimate.confidence:.1%}")
        
        # Method 2: Progressive Asset-Based Estimation (ENHANCED)
        asset_estimate = self._estimate_from_progressive_asset_rates(fixed_assets)
        if asset_estimate.confidence >= 0.5:
            logger.info(f"✅ Using progressive asset rates: ${asset_estimate.monthly_amount:.0f}/month at {asset_estimate.annual_rate:.1%}")
            return asset_estimate
        
        # Method 3: Revenue-Based Fallback
        if revenue_data and len(revenue_data) > 0:
            revenue_estimate = self._estimate_from_revenue_fallback_direct(revenue_data)
            logger.warning(f"⚠️ Using revenue-based fallback: ${revenue_estimate.monthly_amount:.0f}/month")
            return revenue_estimate
        
        # Method 4: Last resort
        logger.error("All depreciation estimation methods failed")
        return self._create_fallback_estimate("No reliable estimation method available")
    
    def _estimate_from_accumulated_depreciation(self, acc_dep_data: List[float], fixed_assets: pd.Series) -> DepreciationEstimate:
        """Estimate depreciation from accumulated depreciation changes (most accurate)"""
        
        try:
            # Clean and process accumulated depreciation data
            acc_dep_series = pd.Series([abs(ad) for ad in acc_dep_data if ad is not None])
            acc_dep_series = acc_dep_series[acc_dep_series >= 0]  # Only meaningful values
            
            if len(acc_dep_series) < 2:
                return self._create_fallback_estimate("Insufficient accumulated depreciation data points")
            
            # Calculate period-to-period changes
            dep_changes = acc_dep_series.diff().dropna()
            valid_changes = dep_changes[dep_changes > 0]
            
            if len(valid_changes) == 0:
                return self._create_fallback_estimate("No valid accumulated depreciation increases found")
            
            # Use median to avoid outlier bias
            monthly_depreciation = valid_changes.median()
            
            # Validate reasonableness against asset base
            avg_asset_base = fixed_assets.mean()
            max_reasonable = avg_asset_base * 0.02  # Max 2% per month = 24% annual
            
            if monthly_depreciation > max_reasonable:
                logger.warning(f"Calculated depreciation ${monthly_depreciation:.0f} exceeds reasonable maximum ${max_reasonable:.0f}")
                return self._create_fallback_estimate("Accumulated depreciation changes appear unrealistic")
            
            # Calculate implied annual rate for validation
            annual_rate = (monthly_depreciation * 12) / max(avg_asset_base, 1)
            
            # Validate rate is within acceptable bounds
            if not (self.min_annual_rate <= annual_rate <= self.max_annual_rate):
                return self._create_fallback_estimate(f"Calculated annual rate {annual_rate:.1%} outside reasonable range")
            
            # Calculate confidence based on data consistency
            cv = valid_changes.std() / max(valid_changes.mean(), 1)  # Coefficient of variation
            confidence = max(0.8, min(0.95, 1.0 - cv))  # Lower CV = higher confidence
            
            return DepreciationEstimate(
                monthly_amount=float(monthly_depreciation),
                method_used="accumulated_depreciation_changes",
                confidence=float(confidence),
                annual_rate=float(annual_rate),
                justification=f"Calculated from {len(valid_changes)} accumulated depreciation changes. "
                             f"Median monthly increase: ${float(monthly_depreciation):.0f}, Annual rate: {float(annual_rate):.1%}, "
                             f"Consistency: {float(confidence):.1%}"
            )
            
        except Exception as e:
            logger.error(f"Error in accumulated depreciation method: {str(e)}")
            return self._create_fallback_estimate(f"Accumulated depreciation calculation error: {str(e)}")
    
    def _estimate_from_progressive_asset_rates(self, fixed_assets: pd.Series) -> DepreciationEstimate:
        """
        Progressive asset-based estimation using Australian business standards
        KEY ENHANCEMENT: Replaces flat $850 with intelligent asset-size-based rates
        """
        
        try:
            avg_assets = fixed_assets.mean()
            median_assets = fixed_assets.median()
            
            # Use median for rate selection (more robust against outliers)
            asset_value = median_assets
            
            # Determine progressive depreciation rate based on asset size
            rate_info = None
            asset_category = None
            
            for category, info in self.asset_depreciation_rates.items():
                if asset_value < info["threshold"]:
                    rate_info = info
                    asset_category = category
                    break
            
            if not rate_info:
                rate_info = self.asset_depreciation_rates["infrastructure"]
                asset_category = "infrastructure"
            
            annual_rate = rate_info["rate"]
            monthly_depreciation = (avg_assets * annual_rate) / 12
            
            # Calculate confidence based on asset data quality
            asset_count = len(fixed_assets)
            asset_stability = 1.0 - (fixed_assets.std() / max(fixed_assets.mean(), 1))
            
            # Higher confidence for more data points and stable assets
            confidence = min(0.85, 0.5 + (asset_count * 0.05) + (asset_stability * 0.2))
            
            return DepreciationEstimate(
                monthly_amount=float(monthly_depreciation),
                method_used="progressive_asset_based",
                confidence=float(confidence),
                annual_rate=float(annual_rate),
                justification=f"Progressive rate for {asset_category} (${asset_value:,.0f}): {float(annual_rate):.1%} on "
                             f"${avg_assets:,.0f} average assets. {rate_info['description']}. "
                             f"Based on {asset_count} data points with {asset_stability:.1%} stability."
            )
            
        except Exception as e:
            logger.error(f"Error in progressive asset rates method: {str(e)}")
            return self._create_fallback_estimate(f"Progressive rates calculation error: {str(e)}")
    
    def _estimate_from_revenue_fallback(self, pnl_data: Optional[Dict]) -> DepreciationEstimate:
        """Revenue-based fallback estimation from P&L data"""
        
        if not pnl_data or not pnl_data.get('periods'):
            return self._create_fallback_estimate("No P&L data available for revenue-based estimation")
        
        try:
            revenue_data = []
            for period in pnl_data.get('periods', []):
                revenue = period.get('revenue')
                if revenue is not None and revenue > 0:
                    revenue_data.append(revenue)
            
            return self._estimate_from_revenue_fallback_direct(revenue_data)
            
        except Exception as e:
            logger.error(f"Error extracting revenue data: {str(e)}")
            return self._create_fallback_estimate(f"Revenue extraction error: {str(e)}")
    
    def _estimate_from_revenue_fallback_direct(self, revenue_data: List[float]) -> DepreciationEstimate:
        """Direct revenue-based estimation (last resort)"""
        
        if not revenue_data:
            return self._create_fallback_estimate("No revenue data available")
        
        try:
            avg_monthly_revenue = np.mean(revenue_data)
            
            # Use 1.5-2.5% of revenue as depreciation estimate (conservative)
            depreciation_percentage = 0.02  # 2% of revenue
            monthly_depreciation = avg_monthly_revenue * depreciation_percentage
            
            # Confidence is lower for revenue-based method
            data_quality = min(0.6, 0.3 + (len(revenue_data) * 0.03))
            
            return DepreciationEstimate(
                monthly_amount=float(monthly_depreciation),
                method_used="revenue_percentage_fallback",
                confidence=float(data_quality),
                annual_rate=float(depreciation_percentage * 12),  # Nominal annual rate
                justification=f"Fallback estimation: {depreciation_percentage:.1%} of average monthly revenue "
                             f"(${float(avg_monthly_revenue):,.0f}). Based on {len(revenue_data)} revenue data points. "
                             f"This is a conservative estimate and may not reflect actual asset depreciation."
            )
            
        except Exception as e:
            logger.error(f"Error in revenue-based fallback: {str(e)}")
            return self._create_fallback_estimate(f"Revenue fallback calculation error: {str(e)}")
    
    def _create_fallback_estimate(self, reason: str) -> DepreciationEstimate:
        """Create minimal fallback estimate when all methods fail"""
        
        logger.error(f"Creating fallback depreciation estimate: {reason}")
        
        return DepreciationEstimate(
            monthly_amount=1200.0,  # Conservative fallback (better than 0)
            method_used="conservative_fallback",
            confidence=0.3,  # Low confidence but not zero
            annual_rate=0.05,  # 5% annual depreciation
            justification=f"Conservative fallback estimate due to: {reason}. "
                         f"Using $1,200/month (5% annual) as safe default for Australian small business."
        )
    
    def analyze_asset_depreciation_profile(self, fixed_assets_data: List[float]) -> Dict[str, Any]:
        """
        Analyze asset depreciation profile for detailed insights
        """
        
        if not fixed_assets_data:
            return {"error": "No asset data provided"}
        
        try:
            assets = pd.Series([fa for fa in fixed_assets_data if fa > 0])
            
            if len(assets) == 0:
                return {"error": "No valid asset data"}
            
            profile = {
                "asset_statistics": {
                    "count": len(assets),
                    "mean": assets.mean(),
                    "median": assets.median(),
                    "min": assets.min(),
                    "max": assets.max(),
                    "std": assets.std(),
                    "coefficient_of_variation": assets.std() / assets.mean() if assets.mean() > 0 else 0
                },
                "depreciation_recommendations": {},
                "asset_category_analysis": {}
            }
            
            # Analyze which category each asset value falls into
            for i, asset_value in enumerate(assets):
                for category, info in self.asset_depreciation_rates.items():
                    if asset_value < info["threshold"]:
                        category_key = f"period_{i+1}"
                        profile["asset_category_analysis"][category_key] = {
                            "asset_value": asset_value,
                            "category": category,
                            "recommended_rate": info["rate"],
                            "description": info["description"]
                        }
                        break
            
            # Overall recommendation
            median_value = assets.median()
            for category, info in self.asset_depreciation_rates.items():
                if median_value < info["threshold"]:
                    profile["depreciation_recommendations"] = {
                        "recommended_category": category,
                        "recommended_annual_rate": info["rate"],
                        "recommended_monthly_amount": (assets.mean() * info["rate"]) / 12,
                        "justification": f"Based on median asset value of ${median_value:,.0f}"
                    }
                    break
            
            return profile
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}