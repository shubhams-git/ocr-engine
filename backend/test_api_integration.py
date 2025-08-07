#!/usr/bin/env python3
"""
Integration test to verify the API works with the P&L validation fix
This script creates test CSV files and calls the multi-PDF API endpoint
"""
import asyncio
import aiohttp
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_files():
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
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp()
    
    pnl_file = Path(temp_dir) / "Profit and Loss - Test Company.csv"
    bs_file = Path(temp_dir) / "Balance Sheet - Test Company.csv"
    
    pnl_file.write_text(pnl_content)
    bs_file.write_text(bs_content)
    
    return str(pnl_file), str(bs_file), temp_dir

async def test_multi_pdf_api():
    """Test the multi-PDF API endpoint"""
    logger.info("🧪 Testing multi-PDF API endpoint...")
    
    # Create test files
    pnl_file, bs_file, temp_dir = create_test_files()
    
    try:
        # Prepare multipart form data
        data = aiohttp.FormData()
        
        # Add P&L file
        with open(pnl_file, 'rb') as f:
            data.add_field('files', f, filename='Profit and Loss - Test Company.csv', content_type='text/csv')
        
        # Add Balance Sheet file  
        with open(bs_file, 'rb') as f:
            data.add_field('files', f, filename='Balance Sheet - Test Company.csv', content_type='text/csv')
        
        # Add model parameter
        data.add_field('model', 'gemini-2.5-pro')
        
        # Make API request
        base_url = "http://localhost:8000"
        
        timeout = aiohttp.ClientTimeout(total=1800)  # 30 minutes timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"📡 Making request to {base_url}/multi-pdf/analyze")
            
            async with session.post(f"{base_url}/multi-pdf/analyze", data=data) as response:
                status = response.status
                response_text = await response.text()
                
                logger.info(f"📡 Response status: {status}")
                
                if status == 200:
                    try:
                        response_json = json.loads(response_text)
                        success = response_json.get('success', False)
                        logger.info(f"✅ API call successful: {success}")
                        
                        if success:
                            extracted_count = len(response_json.get('extracted_data', []))
                            projections_present = bool(response_json.get('projections'))
                            logger.info(f"📋 Extracted data files: {extracted_count}")
                            logger.info(f"📋 Projections generated: {projections_present}")
                            
                            return True
                        else:
                            error = response_json.get('error', 'Unknown error')
                            logger.error(f"❌ API returned success=false: {error}")
                            return False
                            
                    except json.JSONDecodeError:
                        logger.error(f"❌ Invalid JSON response: {response_text[:500]}...")
                        return False
                else:
                    logger.error(f"❌ API call failed with status {status}")
                    logger.error(f"Response: {response_text[:500]}...")
                    return False
    
    except aiohttp.ClientConnectorError:
        logger.error("❌ Could not connect to API server. Is the server running on localhost:8000?")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return False
    
    finally:
        # Cleanup temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
            logger.info("🧹 Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"⚠️ Could not clean up temp dir: {str(e)}")

async def main():
    """Main test function"""
    logger.info("🚀 Starting API integration test...")
    logger.info("📋 This test requires the OCR engine server to be running on localhost:8000")
    
    success = await test_multi_pdf_api()
    
    if success:
        logger.info("🎉 API integration test PASSED! The P&L validation fix is working correctly.")
        return True
    else:
        logger.error("❌ API integration test FAILED. Check the logs above for details.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {str(e)}")
        sys.exit(1)
