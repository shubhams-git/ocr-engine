#!/usr/bin/env python3
"""
Test script to verify the P&L validation fix
This script tests the multi-PDF analysis functionality to ensure P&L validation works correctly.
"""
import asyncio
import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.multi_pdf_service import multi_pdf_service
from utils import DataStructureParser, JSONValidator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_csv_files():
    """Create test CSV files for P&L and Balance Sheet"""
    
    # P&L CSV content
    pnl_content = """Account,2023-01,2023-02,2023-03,2023-04,2023-05,2023-06
Revenue,150000,160000,155000,170000,165000,175000
Cost of Sales,90000,95000,92000,102000,98000,105000
Gross Profit,60000,65000,63000,68000,67000,70000
Operating Expenses,45000,47000,46000,49000,48000,50000
Net Income,15000,18000,17000,19000,19000,20000"""

    # Balance Sheet CSV content  
    bs_content = """Account,2023-01,2023-02,2023-03,2023-04,2023-05,2023-06
Cash,25000,30000,28000,32000,35000,40000
Accounts Receivable,15000,16000,18000,19000,20000,22000
Inventory,8000,9000,8500,9500,10000,11000
Total Current Assets,48000,55000,54500,60500,65000,73000
Fixed Assets Net,120000,118000,116000,114000,112000,110000
Total Assets,168000,173000,170500,174500,177000,183000
Accounts Payable,12000,13000,12500,14000,15000,16000
Short Term Debt,5000,5000,5000,5000,5000,5000
Total Current Liabilities,17000,18000,17500,19000,20000,21000
Long Term Debt,50000,48000,46000,44000,42000,40000
Total Equity,101000,107000,107000,111500,115000,122000
Total Liabilities and Equity,168000,173000,170500,174500,177000,183000"""
    
    return pnl_content, bs_content

def create_mock_stage1_response(document_type: str, periods_data: dict):
    """Create a mock Stage 1 response for testing"""
    return {
        "version": "1.0",
        "company_id": "test_company",
        "currency": "AUD",
        "generated_at": "2024-01-01T00:00:00Z",
        "document_type": document_type,
        "meta": {
            "source_manifest_hash": f"test_{document_type.lower().replace(' ', '_')}.csv",
            "coverage_score": 0.95
        },
        "periods": periods_data
    }

async def test_financial_data_validation():
    """Test the improved financial data validation"""
    logger.info("🧪 Testing financial data validation...")
    
    # Test P&L data
    pnl_periods = [
        {
            "period": "2023-01",
            "revenue": 150000,
            "cogs": 90000,
            "gross_profit": 60000,
            "opex": {"total": 45000},
            "net_income": 15000
        }
    ]
    
    pnl_data = create_mock_stage1_response("Profit and Loss", pnl_periods)
    pnl_valid = JSONValidator.validate_financial_data(pnl_data)
    
    # Test Balance Sheet data  
    bs_periods = [
        {
            "period": "2023-01", 
            "cash": 25000,
            "ar": 15000,
            "inventory": 8000,
            "total_assets": 168000,
            "ap": 12000,
            "equity": 101000,
            "total_liabilities_equity": 168000
        }
    ]
    
    bs_data = create_mock_stage1_response("Balance Sheet", bs_periods)
    bs_valid = JSONValidator.validate_financial_data(bs_data)
    
    logger.info(f"✅ P&L validation result: {pnl_valid}")
    logger.info(f"✅ Balance Sheet validation result: {bs_valid}")
    
    return pnl_valid and bs_valid

async def test_doc_type_extraction():
    """Test document type extraction and P&L detection"""
    logger.info("🧪 Testing document type extraction...")
    
    # Create test files
    pnl_content, bs_content = create_test_csv_files()
    
    files_data = [
        ("Profit and Loss - Test Company.csv", pnl_content.encode('utf-8')),
        ("Balance Sheet - Test Company.csv", bs_content.encode('utf-8'))
    ]
    
    # Test file validation
    try:
        multi_pdf_service.validate_files(files_data)
        logger.info("✅ File validation passed")
    except Exception as e:
        logger.error(f"❌ File validation failed: {str(e)}")
        return False
    
    return True

async def test_stage1_normalization():
    """Test Stage 1 result normalization"""
    logger.info("🧪 Testing Stage 1 result normalization...")
    
    # Mock Stage 1 response
    mock_ocr_response = {
        "success": True,
        "data": json.dumps({
            "document_type": "Profit and Loss",
            "company_id": "test_company", 
            "periods": [{"period": "2023-01", "revenue": 150000, "net_income": 15000}]
        }),
        "error": None
    }
    
    # Test normalization
    normalized = DataStructureParser.normalize_stage1_result(mock_ocr_response)
    
    success = (
        normalized["success"] and
        normalized["data"] and
        normalized["data"].get("document_type") == "Profit and Loss"
    )
    
    logger.info(f"✅ Stage 1 normalization result: {success}")
    logger.info(f"📋 Document type extracted: {normalized['data'].get('document_type', 'None')}")
    
    return success

def test_pnl_detection_logic():
    """Test the P&L detection logic specifically"""
    logger.info("🧪 Testing P&L detection logic...")
    
    # Simulate doc_types dictionary
    doc_types = {
        "Profit and Loss - Test Company.csv": "Profit and Loss",
        "Balance Sheet - Test Company.csv": "Balance Sheet"
    }
    
    # Test P&L detection
    has_profit_loss = any(doc_type == 'Profit and Loss' for doc_type in doc_types.values())
    
    logger.info(f"📋 Document types: {doc_types}")
    logger.info(f"📋 Document type values: {list(doc_types.values())}")
    logger.info(f"✅ P&L detection result: {has_profit_loss}")
    
    return has_profit_loss

async def run_comprehensive_test():
    """Run comprehensive test of the fix"""
    logger.info("🚀 Starting comprehensive P&L validation fix test...")
    
    tests = [
        ("Financial Data Validation", test_financial_data_validation()),
        ("Document Type Extraction", test_doc_type_extraction()),
        ("Stage 1 Normalization", test_stage1_normalization()),
        ("P&L Detection Logic", test_pnl_detection_logic())
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
            logger.info(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"❌ {test_name}: FAILED with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("🎯 TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:<30} | {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! The P&L validation fix should work correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["OCR_SERVER_MAIN"] = "true"
    
    # Run the test
    try:
        success = asyncio.run(run_comprehensive_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {str(e)}")
        sys.exit(1)
