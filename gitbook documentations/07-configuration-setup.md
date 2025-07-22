# Configuration & Setup Guide

## Overview

This guide covers the essential setup and configuration needed to run the OCR-based Financial Projection System effectively.

## System Requirements

### Hardware Needs
- **CPU**: 4+ cores (8+ recommended)
- **Memory**: 8GB RAM minimum (16GB+ recommended)
- **Storage**: 20GB available space
- **Network**: Stable internet connection for AI API calls

### Software Requirements
- **Python 3.8+**
- **FastAPI framework**
- **Google Gemini API access**
- **Standard Python libraries** (see requirements.txt)

## Essential Configuration

### 1. API Keys Setup
You need Google Gemini API keys for the system to work:

```bash
# Single API key
GOOGLE_API_KEY=your_gemini_api_key_here

# Multiple API keys (recommended for better performance)
GOOGLE_API_KEY_1=your_first_api_key
GOOGLE_API_KEY_2=your_second_api_key
GOOGLE_API_KEY_3=your_third_api_key
```

**Why multiple keys?**
- Better performance through load distribution
- Higher API quota limits
- Improved reliability

### 2. Basic Configuration (.env file)
```bash
# Server settings
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Processing limits
API_TIMEOUT=60
MAX_RETRIES=3
OVERALL_PROCESS_TIMEOUT=600

# File size limits
MAX_PDF_SIZE=52428800     # 50MB
MAX_CSV_SIZE=26214400     # 25MB
MAX_IMAGE_SIZE=10485760   # 10MB
MAX_FILES=10

# Australian business settings
DEFAULT_CURRENCY=AUD
FINANCIAL_YEAR_START=07-01  # July 1st
FINANCIAL_YEAR_END=06-30    # June 30th
DEFAULT_TAX_RATE=0.25       # 25% corporate tax
DIVIDEND_PAYOUT_RATIO=0.40  # 40% dividend payout
```

### 3. Performance Settings
```bash
# Concurrency control
PRO_MODEL_SEMAPHORE_LIMIT=3        # Gemini Pro model concurrent calls
FLASH_MODEL_CONCURRENT_LIMIT=10    # Gemini Flash model concurrent calls

# Feature toggles
ENABLE_AI_SEMANTIC_VALIDATION=true
ENABLE_ROBUST_JSON_PARSING=true
ENABLE_MONITORING=true
```

## Key Configuration Concepts

### 1. Model Selection Strategy
The system uses a **tiered approach**:
- **Gemini Flash**: For data extraction (Stage 1) - faster, higher quotas
- **Gemini Pro**: For analysis and projections (Stages 2-3) - more sophisticated

### 2. Concurrency Management
- **Pro Model Limit**: 3 concurrent calls (prevents quota exhaustion)
- **Flash Model Limit**: 10 concurrent calls (higher quota available)
- **API Key Rotation**: Distributes load across multiple keys

### 3. Australian Business Context
- **Financial Year**: July-June cycles (not calendar year)
- **Tax Rate**: 25% corporate tax rate
- **Dividend Policy**: 40% quarterly dividend payout
- **Seasonality**: Understands Australian business patterns

## File Processing Limits

### Why These Limits Exist
- **Processing Efficiency**: Prevents system overload
- **API Quota Management**: Stays within service limits
- **Quality Assurance**: Ensures reliable processing

### Recommended File Sizes
- **PDFs**: 10-20MB typical, 50MB maximum
- **CSVs**: 5-10MB typical, 25MB maximum
- **Images**: 2-5MB typical, 10MB maximum

## Performance Optimization

### 1. API Key Management
**Best practices:**
- Use multiple API keys for better performance
- Rotate keys to distribute load
- Monitor usage to avoid quota limits

### 2. Processing Optimization
**Key settings:**
- **Timeout Values**: Balance thoroughness with responsiveness
- **Retry Logic**: Handle temporary failures gracefully
- **Concurrent Processing**: Process multiple files simultaneously

### 3. Memory Management
**Considerations:**
- **Large Files**: Streamed processing for efficiency
- **Concurrent Requests**: Managed to prevent memory issues
- **Cleanup**: Temporary files removed automatically

## Business Rule Customization

### 1. Industry-Specific Settings
```bash
# Default settings work for most Australian businesses
# Can be customized for specific industries:

# Technology companies
DEFAULT_DSO=30              # Faster customer payments
DEFAULT_INVENTORY_DAYS=0    # No inventory

# Manufacturing
DEFAULT_DSO=60              # Longer payment terms
DEFAULT_INVENTORY_DAYS=90   # Higher inventory levels

# Retail
DEFAULT_DSO=15              # Quick customer payments
DEFAULT_INVENTORY_DAYS=45   # Moderate inventory
```

### 2. Regional Adaptations
**Australian settings (default):**
- July-June financial year
- 25% corporate tax rate
- Local seasonal patterns
- AUD currency

**Other regions can be configured:**
- Different financial year cycles
- Local tax rates
- Regional business patterns

## Deployment Options

### 1. Local Development
```bash
# Simple local setup
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### 2. Production Deployment
**Docker recommended:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Cloud Deployment
**Considerations:**
- **Scaling**: Multiple instances for high load
- **Load Balancing**: Distribute requests across instances
- **Monitoring**: Track performance and errors
- **Security**: Protect API keys and data

## Monitoring & Logging

### 1. System Health
The system provides:
- **Health check endpoint**: `/health`
- **Performance metrics**: Response times, success rates
- **Error tracking**: Detailed error logs
- **Quality monitoring**: Data quality scores

### 2. Log Levels
```bash
DEBUG   # Detailed debugging information
INFO    # General system information (default)
WARNING # Potential issues
ERROR   # System errors
```

### 3. Key Metrics to Monitor
- **Processing time**: How long analyses take
- **Success rate**: Percentage of successful analyses
- **Quality scores**: Average data quality
- **API usage**: Track quota consumption

## Security Considerations

### 1. API Key Protection
- **Environment Variables**: Never hardcode keys
- **Access Control**: Limit who can access keys
- **Key Rotation**: Regularly update API keys
- **Monitoring**: Track API key usage

### 2. Data Security
- **File Upload**: Validate file types and sizes
- **Processing**: Secure handling of financial data
- **Storage**: Temporary files cleaned up automatically
- **Transmission**: Use HTTPS in production

## Troubleshooting

### Common Issues

**"No API keys configured"**
- Solution: Set GOOGLE_API_KEY environment variable
- Check: API key format and validity

**"File too large"**
- Solution: Reduce file size or split into multiple files
- Check: File size limits in configuration

**"Processing timeout"**
- Solution: Increase OVERALL_PROCESS_TIMEOUT
- Check: File complexity and system load

**"Poor quality score"**
- Solution: Provide clearer, more complete financial data
- Check: Document quality and completeness

### Performance Issues

**Slow processing:**
- Add more API keys for better performance
- Increase concurrency limits carefully
- Check system resources (CPU, memory)

**Memory problems:**
- Reduce file sizes
- Limit concurrent processing
- Monitor system memory usage

## Best Practices

### 1. Configuration Management
- **Use environment variables** for all settings
- **Document configuration changes**
- **Test configuration changes** before production
- **Keep configuration secure**

### 2. Performance Optimization
- **Monitor system metrics** regularly
- **Optimize API key usage**
- **Balance accuracy with speed**
- **Scale resources as needed**

### 3. Quality Assurance
- **Validate configuration** on startup
- **Test with sample data** before production
- **Monitor quality scores**
- **Implement proper error handling**

## Getting Started Checklist

1. **✓ Install Python 3.8+** and required packages
2. **✓ Obtain Google Gemini API keys**
3. **✓ Configure .env file** with your settings
4. **✓ Test with sample financial documents**
5. **✓ Verify system health** using `/health` endpoint
6. **✓ Monitor performance** and adjust as needed

**Key Takeaway**: The system is designed to work out-of-the-box with minimal configuration, while providing flexibility for customization based on your specific business needs and deployment requirements. 