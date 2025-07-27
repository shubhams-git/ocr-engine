# Configuration & Setup Guide

## Overview

This guide covers the essential setup and configuration needed to run the Financial Projection System effectively.

## System Requirements

### Hardware Needs
- **CPU**: 4+ cores (8+ recommended)
- **Memory**: 8GB RAM minimum (16GB+ recommended for large documents)
- **Storage**: 20GB available space
- **Network**: Stable internet connection for AI API calls

### Software Requirements
- **Python 3.8+**
- **FastAPI framework**
- **Google Gemini API access**
- **Standard Python libraries** (see `backend/requirements.txt`)

## Essential Configuration (`backend/.env` file)

Create a `.env` file inside the `backend` directory.

### 1. API Keys Setup (Required)
You need at least one Google Gemini API key. Multiple keys are highly recommended for resilience and performance.

```bash
# Provide one or more keys as a comma-separated list or on separate lines.
# The system will rotate through them automatically.
GEMINI_API_KEY_1=your_first_api_key
GEMINI_API_KEY_2=your_second_api_key
GEMINI_API_KEY_3=your_third_api_key
```

### 2. Core Processing Settings
These settings control the performance and stability of the system. The defaults are optimized to prevent API overload errors.

```bash
# --- TIMEOUTS ---
# Max time for a single API call to Gemini
GEMINI_API_TIMEOUT=720 # (12 minutes)
# Max time for the entire 4-stage process for a single request
OVERALL_PROCESS_TIMEOUT=1200 # (20 minutes)

# --- RETRY LOGIC ---
# Controls how the system handles temporary API errors
GEMINI_MAX_RETRIES=6
GEMINI_BASE_RETRY_DELAY=15 # (seconds)
GEMINI_MAX_RETRY_DELAY=120 # (seconds)
GEMINI_EXPONENTIAL_MULTIPLIER=1.5
GEMINI_OVERLOAD_MULTIPLIER=2.0

# --- SMART RATE LIMITING (PRO MODEL PROTECTION) ---
# These settings are crucial for preventing 503 overload errors.
# The system dynamically waits based on the longest required delay.
PRO_MODEL_MIN_DELAY=12.0 # (seconds) Standard delay between any two Pro calls.
PRO_MODEL_ERROR_DELAY=20.0 # (seconds) Delay after any non-overload error.
PRO_MODEL_OVERLOAD_DELAY=45.0 # (seconds) Longer delay after a 503/overload error.
```

### 3. Server and Frontend Configuration
```bash
# --- SERVER SETTINGS ---
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# --- CORS ---
# URL of the frontend application for Cross-Origin Resource Sharing
FRONTEND_URL=http://localhost:5173
```

## Key Configuration Concepts

### 1. Unified Model Strategy
The system uses a **unified model architecture**.
- **`gemini-2.5-pro`** is used for all four stages of the analysis.
- This ensures maximum analytical power and consistency throughout the process.
- There is no need to configure separate models for different stages.

### 2. Smart Rate Limiting
This is the most critical performance feature. Instead of simple, fixed delays, the system uses a dynamic "smart delay" before each call to the `gemini-2.5-pro` model.
- It checks the time since the last call, the last error, and the last overload.
- It applies the **longest necessary delay**, ensuring it respects API limits without waiting longer than needed.
- This strategy is designed to **eliminate 503 Service Unavailable errors** from the API.

### 3. Concurrency Management
- The system is configured to process **one Pro model call at a time** across the entire application, managed by a semaphore.
- This sequential processing is essential for the 4-stage pipeline, as each stage's output is the input for the next, building a chain of context and analysis.

## Deployment

### 1. Local Development
From the project root directory:
```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Configure your backend/.env file

# 3. Run the backend server
uvicorn backend.main:app --reload
```
The backend will be available at `http://localhost:8000`.

From a separate terminal, run the frontend:
```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install frontend dependencies
npm install

# 3. Run the frontend development server
npm run dev
```
The frontend will be available at `http://localhost:5173`.

### 2. Production Deployment
Using Docker is recommended for production. You can build separate containers for the frontend and backend and use a reverse proxy like Nginx to manage traffic.

## Monitoring & Logging

### 1. System Health
- **Health Check Endpoint**: `GET /health` provides a simple status check.
- **Admin Endpoints**: The `/admin` routes provide more detailed health checks and allow for testing individual stages of the pipeline.

### 2. Log Levels
Set `LOG_LEVEL` in your `.env` file:
- `INFO`: Default level for general operational messages.
- `DEBUG`: Very detailed logs, useful for troubleshooting specific issues.

### 3. Key Metrics to Monitor
- **Processing Time**: The `data_analysis_summary` in the final response contains detailed timings for each of the four stages.
- **API Errors**: Monitor logs for any API call failures, especially overload warnings, though the smart rate-limiter aims to prevent these.
- **Projection Completeness**: The logs and the final response indicate how many of the required projection metrics were successfully generated.

## Troubleshooting

**"No API keys configured"**
- **Solution**: Ensure your `backend/.env` file exists and contains at least one `GEMINI_API_KEY_1`.

**`504 Gateway Timeout` or `Process exceeded X seconds limit`**
- **Cause**: The entire 4-stage process is taking longer than the `OVERALL_PROCESS_TIMEOUT`. This can happen with a large number of very complex, multi-page documents.
- **Solution**: Try reducing the number of files in a single request.

**Poor Quality Projections or Errors in Analysis**
- **Cause**: The quality of the input documents is low (blurry scans, non-standard formats, missing data).
- **Solution**: Ensure you are providing clear, complete P&L and Balance Sheet documents covering at least 12-24 months. The quality of the output is directly dependent on the quality of the input.

**Key Takeaway**: The system is highly optimized out-of-the-box. The most important configuration steps are providing your Gemini API keys and ensuring the `FRONTEND_URL` matches your setup. The smart rate-limiting and timeout settings are pre-tuned for stability. 