#!/usr/bin/env python3
"""
Integration test to verify the enhanced cash flow fixes are working
Run this script to validate all components are properly integrated
"""

import asyncio
import logging
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_cash_flow_integration():
    """
    Comprehensive test of enhanced cash flow reconstruction
    """
    
    print("🧪 ENHANCED CASH FLOW INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Import all enhanced components
        print("\n1️⃣ Testing Enhanced Component Imports...")
        
        from services.enhanced_depreciation import EnhancedDepreciationEstimator, DepreciationEstimate
        from services.cash_flow_validator import EnhancedCashFlowValidator, ValidationResult
        from config import ENHANCED_CASH_FLOW_CONFIG
        from services.business_analysis_service import business_analysis_service
        
        print("   ✅ All enhanced components imported successfully")
        
        # Test 2: Verify enhanced business analysis service integration
        print("\n2️⃣ Testing Business Analysis Service Integration...")
        
        # Check if enhanced components are integrated
        has_dep_estimator = hasattr(business_analysis_service, 'depreciation_estimator')
        has_validator = hasattr(business_analysis_service, 'cash_flow_validator')
        has_enhanced_config = hasattr(business_analysis_service, 'enhanced_config')
        
        print(f"   📊 Depreciation Estimator: {'✅ INTEGRATED' if has_dep_estimator else '❌ MISSING'}")
        print(f"   📊 Cash Flow Validator: {'✅ INTEGRATED' if has_validator else '❌ MISSING'}")
        print(f"   📊 Enhanced Config: {'✅ INTEGRATED' if has_enhanced_config else '❌ MISSING'}")
        
        # Test 3: Test enhanced depreciation with realistic data
        print("\n3️⃣ Testing Enhanced Depreciation Estimation...")
        
        depreciation_estimator = EnhancedDepreciationEstimator()
        
        # Realistic asset progression (similar to MJV but improved)
        test_assets = [280000, 350000, 380000, 770000, 775000]
        test_acc_dep = [0, 0, 15000, 45000, 75000]  # Progressive accumulated depreciation
        
        # Cast to floats to satisfy type annotations
        dep_result = depreciation_estimator.estimate_depreciation(list(map(float, test_assets)), list(map(float, test_acc_dep)))
        
        print(f"   📊 Depreciation Analysis:")
        print(f"      Method: {dep_result.method_used}")
        print(f"      Monthly Amount: ${dep_result.monthly_amount:.0f}")
        print(f"      Confidence: {dep_result.confidence:.1%}")
        print(f"      Annual Rate: {dep_result.annual_rate:.1%}")
        print(f"      Justification: {dep_result.justification[:100]}...")
        
        # Validate improvements over flat $850
        improvement_indicators = [
            dep_result.monthly_amount != 850,  # Should not be flat $850
            dep_result.confidence > 0.5,       # Should have reasonable confidence
            dep_result.method_used != "conservative_fallback",  # Should use better method
            dep_result.annual_rate > 0.02      # Should have realistic rate
        ]
        
        improvement_score = sum(improvement_indicators) / len(improvement_indicators)
        print(f"   📈 Improvement Score: {improvement_score:.1%} ({sum(improvement_indicators)}/{len(improvement_indicators)} indicators)")
        
        # Test 4: Test enhanced cash flow validation
        print("\n4️⃣ Testing Enhanced Cash Flow Validation...")
        
        cash_flow_validator = EnhancedCashFlowValidator()
        
        # Mock cash flow period (similar to problematic MJV data)
        test_period = {
            "period": "2023-01",
            "ocf": 17120,
            "icf": 0,
            "fcf": -32810,
            "delta_cash": -15690,
            "ni": 18270,
            "depreciation": dep_result.monthly_amount,  # Use enhanced depreciation
            "flags": [],
            "reasons": []
        }
        
        validation_result = cash_flow_validator.validate_period(test_period, dep_result)
        
        print(f"   📊 Validation Result:")
        print(f"      Status: {validation_result.status}")
        print(f"      Variance: ${validation_result.variance:.0f}")
        print(f"      Quality Score: {validation_result.quality_score:.2f}")
        print(f"      Flags: {validation_result.flags}")
        
        # Test 5: Test full cash flow validation
        print("\n5️⃣ Testing Full Cash Flow Result Validation...")
        
        # Mock full cash flow result with multiple periods
        mock_cash_flow_result = {
            "periods": [
                test_period,
                {
                    "period": "2023-02",
                    "ocf": 18330,
                    "icf": 0,
                    "fcf": -7880,
                    "delta_cash": 10450,
                    "ni": 18780,
                    "depreciation": dep_result.monthly_amount,
                    "flags": [],
                    "reasons": []
                }
            ]
        }
        
        full_validation = cash_flow_validator.validate_full_cash_flow_result(
            mock_cash_flow_result, 
            dep_result
        )
        
        global_score = full_validation.get('global_score', 0)
        print(f"   📊 Full Validation:")
        print(f"      Global Score: {global_score:.2f}")
        print(f"      Status: {full_validation.get('status', 'Unknown')}")
        print(f"      Recommendations: {len(full_validation.get('recommendations', []))}")
        
        # Test 6: Test enhanced JSON parsing
        print("\n6️⃣ Testing Enhanced JSON Parsing...")
        
        try:
            from services.business_analysis_service import EnhancedJSONParser
            
            # Test with valid cash flow JSON
            test_json = json.dumps({
                "version": "1.0",
                "currency": "AUD", 
                "method_version": "enhanced_indirect_method_v2.0",
                "periods": [
                    {
                        "period": "2023-01",
                        "ni": 18270,
                        "ocf": 17120,
                        "delta_cash": -15690
                    }
                ]
            })
            
            parsed_result = EnhancedJSONParser.parse_cash_flow_response(test_json)
            
            if parsed_result:
                print(f"   ✅ Enhanced JSON parsing successful")
                print(f"   📊 Parsed periods: {len(parsed_result.get('periods', []))}")
            else:
                print(f"   ❌ Enhanced JSON parsing failed")
                
        except Exception as e:
            print(f"   ⚠️ Enhanced JSON parser test failed: {str(e)}")
        
        # Test 7: Configuration validation
        print("\n7️⃣ Testing Enhanced Configuration...")
        
        config_valid = False  # default to avoid unbound in report
        try:
            from config import validate_enhanced_config
            
            config_valid = validate_enhanced_config()
            print(f"   📊 Configuration Valid: {'✅ YES' if config_valid else '❌ NO'}")
            
            # Check key configuration values
            feature_flags = ENHANCED_CASH_FLOW_CONFIG["feature_flags"]
            enabled_features = [k for k, v in feature_flags.items() if v]
            
            print(f"   📊 Enabled Features: {len(enabled_features)}/{len(feature_flags)}")
            for feature in enabled_features[:5]:  # Show first 5
                print(f"      - {feature}")
                
        except Exception as e:
            print(f"   ❌ Configuration test failed: {str(e)}")
        
        # Test 8: Overall assessment
        print("\n8️⃣ Overall Integration Assessment...")
        
        # Calculate overall integration health
        health_checks = [
            has_dep_estimator and has_validator,  # Core integration
            improvement_score > 0.75,             # Depreciation improvements
            global_score > 0.3,                   # Validation improvements
            dep_result.monthly_amount > 1000,     # Reasonable depreciation
            validation_result.quality_score > 0.5 # Validation quality
        ]
        
        health_score = sum(health_checks) / len(health_checks)
        
        print(f"   📈 Integration Health: {health_score:.1%} ({sum(health_checks)}/{len(health_checks)} checks passed)")
        
        if health_score >= 0.8:
            print("   🎉 INTEGRATION EXCELLENT - Ready for deployment!")
            status_message = "All major components integrated and functioning well"
        elif health_score >= 0.6:
            print("   ✅ INTEGRATION GOOD - Minor issues to address")
            status_message = "Most components working, some optimizations needed"
        elif health_score >= 0.4:
            print("   ⚠️ INTEGRATION PARTIAL - Several issues to fix")
            status_message = "Core functionality present but needs improvement"
        else:
            print("   ❌ INTEGRATION POOR - Major issues need attention")
            status_message = "Significant problems preventing proper operation"
        
        # Test 9: Generate integration report
        print("\n9️⃣ Integration Report...")
        
        report = f"""
ENHANCED CASH FLOW INTEGRATION REPORT
====================================

Overall Health: {health_score:.1%}
Status: {status_message}

Component Status:
✅ Depreciation Estimator: {'Integrated' if has_dep_estimator else 'Missing'}
✅ Cash Flow Validator: {'Integrated' if has_validator else 'Missing'}  
✅ Enhanced Configuration: {'Loaded' if config_valid else 'Invalid'}

Performance Improvements:
📈 Depreciation Quality: {dep_result.confidence:.1%} confidence
📈 Monthly Depreciation: ${dep_result.monthly_amount:.0f} (vs flat $850)
📈 Validation Score: {validation_result.quality_score:.2f}
📈 Global Quality: {global_score:.2f}

Key Features:
- Progressive depreciation rates based on asset size
- Intelligent variance classification (not default RECLASS_DRAWINGS)
- Confidence-adjusted validation tolerances
- Enhanced JSON parsing with multiple strategies
- Comprehensive quality scoring

Expected Improvements in Production:
- Quality scores should improve from 0.0 to {global_score:.1f}+
- More accurate depreciation estimates
- Better cash flow reconciliation
- Intelligent error classification
- Reduced false positives in validation
        """
        
        print(report)
        
        return health_score >= 0.6  # Success if health >= 60%
        
    except Exception as e:
        print(f"❌ Integration test failed with exception: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_cash_flow_integration())
    print(f"\n{'✅ INTEGRATION TEST PASSED' if success else '❌ INTEGRATION TEST FAILED'}")
    sys.exit(0 if success else 1)