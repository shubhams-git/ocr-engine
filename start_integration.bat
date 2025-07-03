@echo off
echo 🔗 Starting OCR Engine Frontend-Backend Integration
echo ================================================

echo.
echo 📝 Step 1: Setting up environment files...

REM Create backend .env if it doesn't exist
if not exist "backend\.env" (
    echo Creating backend .env file...
    (
        echo # Backend Environment Variables
        echo HOST=0.0.0.0
        echo PORT=8000
        echo DEBUG=True
        echo FRONTEND_URL=http://localhost:5173
        echo.
        echo # Gemini API Keys ^(Replace with your actual keys^)
        echo # Get your keys from: https://aistudio.google.com/
        echo GEMINI_API_KEY_1=your_actual_gemini_api_key_here
        echo GEMINI_API_KEY_2=your_second_api_key_here
        echo GEMINI_API_KEY_3=your_third_api_key_here
        echo GEMINI_API_KEY_4=your_fourth_api_key_here
        echo GEMINI_API_KEY_5=your_fifth_api_key_here
        echo GEMINI_API_KEY_6=your_sixth_api_key_here
        echo GEMINI_API_KEY_7=your_seventh_api_key_here
        echo GEMINI_API_KEY_8=your_eighth_api_key_here
        echo GEMINI_API_KEY_9=your_ninth_api_key_here
        echo GEMINI_API_KEY_10=your_tenth_api_key_here
        echo.
        echo # File Upload Settings
        echo MAX_FILE_SIZE=10485760
        echo UPLOAD_DIR=uploads
        echo.
        echo # API Settings
        echo API_TIMEOUT=30
        echo RATE_LIMIT=100
    ) > backend\.env
    echo ✅ Created backend\.env
    echo ⚠️  Please edit backend\.env and add your actual Gemini API keys!
    pause
)

REM Create frontend .env if it doesn't exist
if not exist "frontend\.env" (
    echo Creating frontend .env file...
    (
        echo # Frontend Environment Variables
        echo VITE_API_URL=http://localhost:8000/api
        echo VITE_MOCK_MODE=false
    ) > frontend\.env
    echo ✅ Created frontend\.env
)

echo.
echo 🔧 Step 2: Installing dependencies...

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo 🚀 Step 3: Starting servers...

echo Starting backend server...
start "OCR Backend" cmd /k "cd backend && python start_server.py"

timeout /t 5 /nobreak >nul

echo Starting frontend server...
start "OCR Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 🎉 Integration started!
echo 📋 Services should be running at:
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔍 Testing connectivity...

timeout /t 10 /nobreak >nul

curl -s http://localhost:8000/api/health >nul
if %errorlevel% == 0 (
    echo ✅ Backend is responding
) else (
    echo ❌ Backend is not responding
)

curl -s http://localhost:5173 >nul
if %errorlevel% == 0 (
    echo ✅ Frontend is responding
) else (
    echo ❌ Frontend is not responding
)

echo.
echo Press any key to exit...
pause 