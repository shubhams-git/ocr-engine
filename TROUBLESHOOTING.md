# Frontend-Backend Integration Troubleshooting Guide

## 🔧 Quick Setup Commands

### 1. Create Environment Files
```bash
# Backend environment
cat > backend/.env << 'EOF'
HOST=0.0.0.0
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:5173

# Replace with your actual Gemini API keys from https://aistudio.google.com/
GEMINI_API_KEY_1=your_actual_gemini_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here
GEMINI_API_KEY_5=your_fifth_api_key_here
GEMINI_API_KEY_6=your_sixth_api_key_here
GEMINI_API_KEY_7=your_seventh_api_key_here
GEMINI_API_KEY_8=your_eighth_api_key_here
GEMINI_API_KEY_9=your_ninth_api_key_here
GEMINI_API_KEY_10=your_tenth_api_key_here

MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
API_TIMEOUT=30
RATE_LIMIT=100
EOF

# Frontend environment  
cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000/api
VITE_MOCK_MODE=false
EOF
```

### 2. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Start Servers

#### Option A: Command Prompt (Recommended for Windows)
```cmd
# Terminal 1 - Backend
cd backend
python start_server.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

#### Option B: Git Bash (if Command Prompt doesn't work)
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend  
npm run dev
```

## 🐛 Common Issues and Solutions

### Issue 1: Backend "Connection Refused" on Port 8000

**Symptoms:**
- `curl http://localhost:8000` fails
- Frontend shows "Backend not available"

**Solutions:**
1. **Check if port is in use:**
   ```bash
   netstat -an | grep :8000
   ```

2. **Try different port:**
   ```bash
   # In backend/.env, change:
   PORT=8001
   # In frontend/.env, change:
   VITE_API_URL=http://localhost:8001/api
   ```

3. **Use Windows Command Prompt instead of Git Bash:**
   ```cmd
   cd backend
   python start_server.py
   ```

4. **Check Windows Firewall:**
   - Open Windows Defender Firewall
   - Allow Python through firewall for both private and public networks

### Issue 2: "No Gemini API Keys Found"

**Symptoms:**
- Backend starts but API calls fail
- Error: "PLEASE_SET_ENV_VARIABLES"

**Solution:**
1. Get API keys from https://aistudio.google.com/
2. Edit `backend/.env` with real API keys:
   ```
   GEMINI_API_KEY_1=AIzaSyC...your_actual_key_here
   ```
3. Restart backend server

### Issue 3: Frontend Shows "CORS Error"

**Symptoms:**
- Frontend loads but API calls fail
- Browser console shows CORS errors

**Solution:**
Backend CORS is already configured. If still failing:
```python
# In backend/app/main.py, verify CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 4: PyMuPDF Segmentation Fault (Windows)

**Symptoms:**
- Backend crashes when processing PDFs
- "Segmentation fault" error

**Solution:**
PDF processing has fallback mechanisms. If it still fails:
```bash
pip uninstall PyMuPDF
pip install PyMuPDF==1.23.26  # Use specific stable version
```

### Issue 5: Frontend Not Loading at localhost:5173

**Symptoms:**
- `npm run dev` fails
- Port 5173 not accessible

**Solutions:**
1. **Check if port is in use:**
   ```bash
   netstat -an | grep :5173
   ```

2. **Use different port:**
   ```bash
   cd frontend
   npm run dev -- --port 3000
   # Update backend CORS settings accordingly
   ```

3. **Clear npm cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

## ✅ Verification Steps

### 1. Test Backend Endpoints
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/models  
curl http://localhost:8000/api/formats
```

### 2. Test Frontend Access
```bash
curl http://localhost:5173
```

### 3. Test Integration
1. Open http://localhost:5173 in browser
2. Upload a test image or PDF
3. Select a model (Gemini 2.5 Flash recommended)
4. Verify OCR results appear

## 🚀 Alternative Quick Start (Windows)

If the above doesn't work, use this simplified approach:

1. **Install Python dependencies:**
   ```cmd
   cd backend
   pip install fastapi uvicorn python-multipart python-dotenv google-generativeai pillow requests
   ```

2. **Start backend with basic command:**
   ```cmd
   python -c "
   import uvicorn
   from app.main import app
   uvicorn.run(app, host='127.0.0.1', port=8000)
   "
   ```

3. **Start frontend:**
   ```cmd
   cd frontend
   npm run dev
   ```

## 📞 Getting Help

If issues persist:
1. Check all error messages in both terminal windows
2. Verify .env files have real API keys (not placeholder text)
3. Try running each component individually
4. Use mock mode for frontend testing: set `VITE_MOCK_MODE=true` in frontend/.env

## 🎯 Success Indicators

You'll know the integration is working when:
- ✅ Backend shows: "Server running at http://0.0.0.0:8000"
- ✅ Frontend shows: "Local: http://localhost:5173/"
- ✅ Browser at localhost:5173 shows the OCR interface
- ✅ File upload and processing works end-to-end
- ✅ Backend status indicator in frontend shows "Connected" 