# OCR Engine - AI-Powered Document Text Extraction

A modern web application that extracts text from images and PDFs using Google's Gemini AI models.

## 🚀 Features

- **Multiple AI Models**: Support for Gemini 2.5 Pro, 2.5 Flash, 1.5 Pro, and 1.5 Flash
- **File Support**: Images (PNG, JPG, JPEG) and PDF documents  
- **Modern UI**: React-based frontend with drag-and-drop upload
- **Real-time Processing**: Fast OCR with live status updates
- **API Key Rotation**: Multiple API keys for reliability
- **Export Options**: Copy to clipboard or download results

## 🏗️ Architecture

```
ocr-engine/
├── frontend/          # React + Vite application (Port 5173)
├── backend/           # FastAPI server (Port 8000)
├── integration_test.py # End-to-end testing
└── start_integration.bat # Windows setup script
```

## 🔧 Setup Instructions

### Prerequisites
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)  
- **Gemini API Keys** ([Get them here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows Command Prompt:
   venv\Scripts\activate
   
   # Windows Git Bash:
   source venv/Scripts/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Copy the template and add your API keys:
   cp .env.template .env
   
   # Edit .env and add your Gemini API keys:
   # GEMINI_API_KEY_1=your_actual_api_key_here
   # GEMINI_API_KEY_2=your_second_api_key_here
   # ... (up to 10 keys for reliability)
   ```

5. **Start the backend server:**
   ```bash
   python run.py
   ```
   Server will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   Application will be available at: http://localhost:5173

## 🌐 API Endpoints

- **Main API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **Available Models**: http://localhost:8000/api/models  
- **OCR Processing**: http://localhost:8000/api/ocr/process
- **Interactive Docs**: http://localhost:8000/docs

## 🧪 Testing

Run the integration test to verify everything works:

```bash
python integration_test.py
```

Or use the Windows batch script:
```cmd
start_integration.bat
```

## 🔒 Security Notes

- **Never commit `.env` files** - they contain sensitive API keys
- **API keys are automatically rotated** for reliability
- **All sensitive files are in `.gitignore`**

## 🚀 Production Deployment

1. Set `DEBUG=False` in backend `.env`
2. Configure proper CORS origins
3. Use environment variables for API keys
4. Build frontend: `npm run build`
5. Serve with proper web server (nginx, etc.)

## 🛠️ Development Workflow

```bash
# Daily development:
cd backend && source venv/Scripts/activate && python run.py &
cd frontend && npm run dev

# Testing:
python integration_test.py

# Before committing:
# Ensure .env files are not staged
git status
```

## 📋 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly  
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.