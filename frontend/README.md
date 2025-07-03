# OCR Engine Frontend 🎯

A modern React application for extracting text from images and PDFs using Google Gemini AI.

## 🌟 Features

- **📁 File Upload** - Drag & drop or browse for images (PNG, JPG, etc.) and PDF documents
- **🤖 AI Models** - Choose from multiple Google Gemini models
- **📊 Results Display** - View extracted text with statistics and processing details
- **💾 Export** - Copy text to clipboard or download as a file
- **📱 Responsive** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites
- **Node.js** (version 16 or higher)
- **Backend server** running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the application**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5173
   ```

## 🎯 How to Use

1. **Select a Model** - Choose your preferred Gemini AI model
2. **Upload a File** - Drag & drop or browse for your image/PDF
3. **Process** - Wait for AI to extract the text
4. **View Results** - See extracted text with statistics
5. **Export** - Copy or download the results

## 📁 Supported File Types

- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP (max 10MB)
- **Documents**: PDF (max 50MB)

## 🛠️ Available Models

- **Gemini 1.5 Flash** (Recommended) - Fast and efficient
- **Gemini 1.5 Pro** - Most capable
- **Gemini 2.0 Flash** (Experimental) - Latest model

## 🔧 Configuration

The frontend connects to the backend server at `http://localhost:8000`. Make sure your backend is running before using the application.

## 📊 Technology Stack

- **React 18** - Modern JavaScript framework
- **Vite** - Fast build tool and dev server
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client for API requests
- **React Dropzone** - File upload component

## 🎯 Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |

## 🧪 Testing

Use `simple_test.html` for quick API testing or `test_network_debug.html` for debugging network connectivity.

## 🎨 Features Details

- **Real-time file validation** with helpful error messages
- **Progress indicators** during processing
- **Responsive design** that works on all devices
- **Smooth animations** for better user experience
- **Export options** for extracted text

---

**Status**: ✅ Production Ready | Backend: `http://localhost:8000`
