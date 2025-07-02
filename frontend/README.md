# OCR Engine Tester Frontend 🎯

A beautiful, modern React application for testing OCR (Optical Character Recognition) engines. Upload images or PDFs, and watch as AI models extract text with stunning animations and detailed results.

## 🌟 What This Project Does

This frontend application allows you to:
- **📁 Upload files** - Drag & drop images (PNG, JPG, etc.) or PDF documents
- **🤖 Extract text** - Uses AI models like OpenAI GPT-4 Vision, Google Gemini, or Claude
- **📊 View results** - See extracted text with word count, confidence scores, and statistics
- **💾 Export data** - Copy text to clipboard or download as a file
- **📱 Works everywhere** - Responsive design for desktop, tablet, and mobile

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** (version 16 or higher) - [Download here](https://nodejs.org/)
- **A web browser** (Chrome, Firefox, Safari, Edge)

### Installation & Setup

1. **Open your terminal** and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. **Install dependencies** (one-time setup):
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

That's it! 🎉 The application should now be running.

## 📱 How to Use the Application

### Step 1: Upload a File
- **Drag & drop** any image or PDF onto the upload area
- **Or click** the upload area to browse and select a file
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP, PDF
- **Maximum size**: 10MB per file

### Step 2: Watch the Processing
- See beautiful animations as your file is processed
- Progress indicators show current processing step
- Estimated processing time is displayed

### Step 3: View Results
- **Extracted Text**: See all text found in your file
- **Statistics**: Word count, character count, line count
- **Confidence Score**: How confident the AI is about the results
- **Processing Details**: Model used, language detected, processing time

### Step 4: Export Your Results
- **Copy to Clipboard**: Click the copy button to copy text
- **Download as File**: Save extracted text as a .txt file
- **Process Another**: Upload a new file to test again

## 🎨 Features Showcase

### Beautiful Design
- **Modern gradient backgrounds** with smooth color transitions
- **Smooth animations** powered by Framer Motion
- **Responsive layout** that looks great on any device
- **Accessibility features** with proper keyboard navigation

### Smart File Handling
- **Drag & drop interface** with visual feedback
- **File validation** with helpful error messages
- **Format detection** shows supported file types
- **Size checking** prevents oversized uploads

### Professional Results Display
- **Clean text presentation** with proper formatting
- **Detailed statistics** about your document
- **Processing metadata** including model information
- **Export options** for further use

## 🔧 Current Setup (Mock Mode)

**Important**: The application currently runs in **Mock Mode**, which means:

✅ **Works immediately** - No backend server required  
✅ **Simulates real processing** - Realistic delays and animations  
✅ **Returns sample results** - Test the full user experience  
✅ **Perfect for testing** - Try all features without limitations

### Sample Text Output
When you upload a file, you'll see something like:
```
Mock OCR Results for: your-file.jpg

This is a simulated OCR response showing how the real 
application will work when connected to AI models like:
- OpenAI GPT-4 Vision
- Google Gemini Pro Vision  
- Anthropic Claude 3 Vision
- Mistral Vision

File: your-file.jpg
File size: 245.67 KB
File type: image/jpeg
```

## 🚀 Switching to Real Backend (When Ready)

When you're ready to connect to a real OCR backend:

1. **Update environment file** (`.env`):
   ```env
   VITE_API_URL=http://your-backend-url/api
   VITE_MOCK_MODE=false
   ```

2. **Restart the application**:
   ```bash
   npm run dev
   ```

3. **Your backend needs these endpoints**:
   - `POST /api/ocr/process` - Process uploaded files
   - `GET /api/health` - Health check
   - `GET /api/models` - Available AI models

See `API_GUIDE.md` for complete backend integration details.

## 🛠️ Technology Stack

- **⚛️ React 18** - Modern JavaScript framework
- **⚡ Vite** - Super fast build tool and dev server
- **🎬 Framer Motion** - Smooth animations and transitions
- **📡 Axios** - HTTP client for API requests
- **📁 React Dropzone** - Drag & drop file uploads
- **🎨 Lucide React** - Beautiful SVG icons
- **🎯 CSS Custom Properties** - Modern styling system

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.jsx       # App header with branding
│   │   ├── FileUpload.jsx   # Drag & drop file upload
│   │   ├── LoadingSpinner.jsx # Loading animations
│   │   └── ResultsDisplay.jsx # OCR results display
│   ├── services/
│   │   └── api.js          # API client with mock support
│   ├── App.jsx             # Main application component
│   ├── App.css             # Application styles
│   └── main.jsx            # Application entry point
├── public/                 # Static assets
├── .env                    # Environment configuration
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## 🎯 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Check code quality |

## 🔍 Testing the Application

### Try These Test Cases:

1. **Upload an image** with text (screenshot, photo of document, etc.)
2. **Upload a PDF** with text content
3. **Test drag & drop** by dragging files onto the upload area
4. **Try invalid files** to see error handling
5. **Test on mobile** by opening on your phone
6. **Copy text** and paste it elsewhere
7. **Download results** as a text file

### Expected Behavior:
- Smooth animations during upload and processing
- Realistic loading times (2-5 seconds)
- Detailed statistics about your file
- Clean, readable text output
- Responsive design on all screen sizes

## 🎨 Customization

### Changing Colors
Edit `src/App.css` and modify the CSS variables:
```css
:root {
  --primary: #6366f1;        /* Main brand color */
  --secondary: #06b6d4;      /* Accent color */
  --success: #10b981;        /* Success states */
  --error: #ef4444;          /* Error states */
}
```

### Modifying Features
- **File size limit**: Change `maxSize` in `FileUpload.jsx`
- **Supported formats**: Update `accept` object in `FileUpload.jsx`
- **Processing steps**: Modify `steps` array in `LoadingSpinner.jsx`
- **Mock responses**: Edit `mockProcessOCR` function in `api.js`

## ❗ Troubleshooting

### Common Issues:

**"npm command not found"**
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Restart your terminal after installation

**"Port 5173 already in use"**
- Another app is using the port
- Kill the other process or use: `npm run dev -- --port 3000`

**"Dependencies not found"**
- Run `npm install` in the frontend directory
- Make sure you're in the correct folder

**"Application won't start"**
- Check you're in the `frontend` directory
- Run `npm install` first
- Check for error messages in terminal

**"Files won't upload"**
- Check file size (max 10MB)
- Ensure file format is supported
- Try a different file

### Getting Help:
- Check the browser console for error messages
- Review the terminal output for build errors
- Ensure all dependencies are installed correctly

## 📱 Mobile Usage

The application works perfectly on mobile devices:
- **Touch-friendly** file upload
- **Responsive layout** adapts to screen size
- **Mobile-optimized** buttons and interactions
- **Swipe gestures** supported where appropriate

## 🚀 Production Deployment

To deploy this application:

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to any static hosting service:
   - Netlify
   - Vercel
   - GitHub Pages
   - AWS S3
   - Any web server

3. **Configure environment variables** for production

## 🤝 Contributing

This project is part of a larger OCR engine system. To contribute:
1. Test the current functionality thoroughly
2. Report any bugs or issues
3. Suggest improvements for user experience
4. Help with backend integration testing

## 📄 License

Part of the OCR Engine project. See the main project for license details.

---

## 🎯 Quick Commands Reference

```bash
# First time setup
cd frontend
npm install

# Start development
npm run dev

# Open in browser
# http://localhost:5173

# Build for production
npm run build
```

**Status**: ✅ Frontend Complete | 🚧 Backend Integration Ready

**Have questions?** Check `API_GUIDE.md` for backend integration details!
