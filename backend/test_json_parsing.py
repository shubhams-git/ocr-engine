#!/usr/bin/env python3
"""
Test script to validate JSON parsing functionality for data.data structures
Run this script to test the robust JSON parsing implementation
"""
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import DataStructureParser, JSONValidator
from logging_config import get_logger

logger = get_logger(__name__)

def test_stage1_data_parsing():
    """Test the Stage 1 data parsing with various data structures"""
    
    print("🧪 Testing Stage 1 Data Parsing...")
    
    # Test Case 1: data.data structure (from admin.py test results)
    test_case_1 = {
        "filename": "test-file.csv",
        "success": True,
        "data": {
            "success": True,
            "data": '{"version": "1.0", "company_id": "Test Company", "document_type": "Profit and Loss", "periods": [{"period": "2024-01", "revenue": 100000, "net_income": 25000}]}',
            "error": None
        },
        "raw_text": None
    }
    
    # Test Case 2: Direct data structure
    test_case_2 = {
        "filename": "test-file-2.csv", 
        "success": True,
        "data": {
            "version": "1.0",
            "company_id": "Test Company 2",
            "document_type": "Balance Sheet",
            "periods": [{"period": "2024-01", "cash": 50000, "total_assets": 150000}]
        },
        "raw_text": None
    }
    
    # Test Case 3: Malformed JSON string
    test_case_3 = {
        "filename": "test-file-3.csv",
        "success": True,
        "data": {
            "success": True,
            "data": '{"version": "1.0", "company_id": "Test Company 3", "document_type": "Profit and Loss"',  # Missing closing brace
            "error": None
        },
        "raw_text": None
    }
    
    test_cases = [
        ("data.data JSON string", test_case_1),
        ("Direct data object", test_case_2),
        ("Malformed JSON", test_case_3)
    ]
    
    results = []
    
    for test_name, test_data in test_cases:
        print(f"\n📋 Testing: {test_name}")
        try:
            # Parse the data
            parsed_data = DataStructureParser.parse_stage1_data(test_data)
            
            if parsed_data:
                print(f"✅ Parsing successful!")
                print(f"   Company: {parsed_data.get('company_id', 'N/A')}")
                print(f"   Document Type: {parsed_data.get('document_type', 'N/A')}")
                print(f"   Periods: {len(parsed_data.get('periods', []))}")
                
                # Validate financial structure
                is_valid = JSONValidator.validate_financial_data(parsed_data)
                print(f"   Financial validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
                
                # Test normalization
                normalized = DataStructureParser.normalize_stage1_result(test_data)
                print(f"   Normalization: {'✅ SUCCESS' if normalized['success'] else '❌ FAILED'}")
                
                results.append((test_name, True, is_valid))
            else:
                print(f"❌ Parsing failed!")
                results.append((test_name, False, False))
                
        except Exception as e:
            print(f"❌ Exception during parsing: {str(e)}")
            results.append((test_name, False, False))
    
    return results

def test_actual_stage1_results():
    """Test with actual Stage 1 results from the JSON file"""
    
    print("\n🧪 Testing with Actual Stage 1 Results...")
    
    try:
        # Try to load the actual stage 1 results
        stage1_file = os.path.join(os.path.dirname(__file__), "stage 1 - approach 2.json")
        
        if not os.path.exists(stage1_file):
            print(f"❌ Stage 1 results file not found: {stage1_file}")
            return False
            
        with open(stage1_file, 'r') as f:
            actual_results = json.load(f)
            
        # Check for different possible structures
        documents = []
        if 'chain_ready' in actual_results:
            documents = actual_results['chain_ready']
            print(f"📄 Found chain_ready structure with {len(documents)} documents")
        elif 'result' in actual_results:
            documents = actual_results['result'] 
            print(f"📄 Found result structure with {len(documents)} documents")
        else:
            print(f"❌ Unknown structure, keys: {list(actual_results.keys())}")
            return False
        
        # Test parsing each result
        parsed_count = 0
        valid_count = 0
        
        for i, result in enumerate(documents):
            try:
                print(f"\n📋 Processing document {i+1}: {result.get('filename', 'unknown')}")
                
                # Parse using our robust parser
                parsed_data = DataStructureParser.parse_stage1_data(result)
                
                if parsed_data:
                    parsed_count += 1
                    print(f"   ✅ Parsing successful")
                    print(f"   Company: {parsed_data.get('company_id', 'N/A')}")
                    print(f"   Document Type: {parsed_data.get('document_type', 'N/A')}")
                    
                    # Validate financial data
                    is_valid = JSONValidator.validate_financial_data(parsed_data)
                    if is_valid:
                        valid_count += 1
                        print(f"   ✅ Financial validation passed")
                    else:
                        print(f"   ❌ Financial validation failed")
                else:
                    print(f"   ❌ Parsing failed")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
        
        print(f"\n📊 Summary:")
        print(f"   Total documents: {len(documents)}")
        print(f"   Successfully parsed: {parsed_count}")
        print(f"   Validation passed: {valid_count}")
        print(f"   Success rate: {(valid_count / len(documents)) * 100:.1f}%" if len(documents) > 0 else "   Success rate: 0.0%")
        
        return valid_count > 0
        
    except Exception as e:
        print(f"❌ Error testing actual results: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 JSON Parsing Robustness Test")
    print("=" * 50)
    
    # Test basic parsing scenarios
    basic_results = test_stage1_data_parsing()
    
    # Test with actual data
    actual_success = test_actual_stage1_results()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    print("\n🔧 Basic Parsing Tests:")
    for test_name, parsed, validated in basic_results:
        status = "✅ PASS" if parsed and validated else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n📄 Actual Data Test: {'✅ PASS' if actual_success else '❌ FAIL'}")
    
    # Overall assessment (actual data success is most important)
    basic_success_count = sum(1 for _, parsed, validated in basic_results if parsed and validated)
    # We expect malformed JSON to fail, so count only valid test cases
    valid_basic_tests = sum(1 for test_name, _, _ in basic_results if "Malformed" not in test_name)
    valid_basic_success = sum(1 for test_name, parsed, validated in basic_results if "Malformed" not in test_name and parsed and validated)
    
    overall_success = (valid_basic_success == valid_basic_tests) and actual_success
    
    print(f"\n🎯 Overall Assessment: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("✅ The robust JSON parsing implementation is working correctly!")
        print("✅ Ready to handle data.data structures from both tests and application code!")
    else:
        print("❌ Some tests failed. Review the parsing logic.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
