import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, BarChart3 } from 'lucide-react'
import FileUpload from './components/FileUpload'
import MultiPDFUpload from './components/MultiPDFUpload'
import ResultsDisplay from './components/ResultsDisplay'
import MultiPDFResults from './components/MultiPDFResults'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'
import { processOCR, processMultiPDFAnalysis, getHealthStatus, getAvailableModels } from './services/api'
import './App.css'

function App() {
  const [mode, setMode] = useState('single') // 'single' or 'multi'
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [ocrResults, setOcrResults] = useState(null)
  const [multiPdfResults, setMultiPdfResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState('unknown')
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash')
  const [availableModels, setAvailableModels] = useState([])

  // Fallback models if backend is not available
  const fallbackModels = [
    { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', description: 'Most capable model for complex tasks' },
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', description: 'Fast and efficient (Recommended)' },
    { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: 'Latest experimental model' },
    { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Fast and reliable' },
    { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'Advanced reasoning capabilities' }
  ]

  // Check backend status and load models on component mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check backend health
        await getHealthStatus()
        setBackendStatus('connected')
        
        // Load available models from backend
        const modelsData = await getAvailableModels()
        if (modelsData.models) {
          setAvailableModels(modelsData.models)
        } else {
          setAvailableModels(fallbackModels)
        }
        
        // Set default model if provided
        if (modelsData.default) {
          setSelectedModel(modelsData.default)
        }
      } catch (err) {
        console.warn('Backend not available:', err.message)
        setBackendStatus('disconnected')
        // Use fallback models if backend is not available
        setAvailableModels(fallbackModels)
      }
    }

    initializeApp()
  }, [])

  const handleFileUpload = async (file) => {
    setUploadedFile(file)
    setIsLoading(true)
    setError(null)
    setOcrResults(null)

    try {
      const results = await processOCR(file, { model: selectedModel })
      setOcrResults(results)
    } catch (err) {
      console.error('OCR processing error:', err)
      setError(err.message || 'Failed to process OCR')
    } finally {
      setIsLoading(false)
    }
  }

  const handleMultiPDFUpload = async (files) => {
    setUploadedFiles(files)
    setIsLoading(true)
    setError(null)
    setMultiPdfResults(null)

    try {
      const results = await processMultiPDFAnalysis(files, { model: selectedModel })
      setMultiPdfResults(results)
    } catch (err) {
      console.error('Multi-PDF analysis error:', err)
      setError(err.message || 'Failed to process multi-PDF analysis')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedFile(null)
    setUploadedFiles([])
    setOcrResults(null)
    setMultiPdfResults(null)
    setError(null)
    setIsLoading(false)
  }

  const handleModeChange = (newMode) => {
    setMode(newMode)
    handleReset()
  }

  return (
    <div className="app">
      <Header backendStatus={backendStatus} />
      
      <main className="main-content">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container"
        >
          {/* Mode Toggle */}
          {!isLoading && !ocrResults && !multiPdfResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mode-toggle"
            >
              <motion.button
                onClick={() => handleModeChange('single')}
                className={`mode-button ${mode === 'single' ? 'active' : ''}`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <FileText size={20} />
                <div>
                  <div>Single Document OCR</div>
                  <div className="mode-description">Extract text from images & PDFs</div>
                </div>
              </motion.button>
              
              <motion.button
                onClick={() => handleModeChange('multi')}
                className={`mode-button ${mode === 'multi' ? 'active' : ''}`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <BarChart3 size={20} />
                <div>
                  <div>Multi-PDF Analysis</div>
                  <div className="mode-description">Analyze, normalize & project data</div>
                </div>
              </motion.button>
            </motion.div>
          )}

          {/* Model Selection */}
          {!uploadedFile && !uploadedFiles.length && !isLoading && !ocrResults && !multiPdfResults && availableModels.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="model-selection"
            >
              <h3>Select AI Model</h3>
              <div className="model-options">
                {availableModels.map((model) => (
                  <label key={model.id} className="model-option">
                    <input
                      type="radio"
                      name="model"
                      value={model.id}
                      checked={selectedModel === model.id}
                      onChange={(e) => setSelectedModel(e.target.value)}
                    />
                    <div className="model-info">
                      <span className="model-name">
                        {model.name}
                        {model.id === 'gemini-2.5-flash' && (
                          <span className="recommended-badge">Recommended</span>
                        )}
                      </span>
                      <span className="model-description">{model.description}</span>
                    </div>
                  </label>
                ))}
              </div>
            </motion.div>
          )}

          {/* Single Document Upload */}
          {mode === 'single' && !uploadedFile && !isLoading && !ocrResults && (
            <FileUpload onFileUpload={handleFileUpload} />
          )}

          {/* Multi-PDF Upload */}
          {mode === 'multi' && !uploadedFiles.length && !isLoading && !multiPdfResults && (
            <MultiPDFUpload onFilesUpload={handleMultiPDFUpload} />
          )}

          {/* Loading Spinner */}
          {isLoading && <LoadingSpinner />}

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="error-container"
            >
              <div className="error-message">
                <h3>Error Processing {mode === 'multi' ? 'Files' : 'File'}</h3>
                <p>{error}</p>
                <div className="error-actions">
                  <button onClick={handleReset} className="retry-button">
                    Try Again
                  </button>
                  {backendStatus === 'disconnected' && (
                    <div className="error-hint">
                      <p><strong>Tip:</strong> Make sure the backend server is running on port 8000</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Single OCR Results */}
          {ocrResults && !isLoading && (
            <ResultsDisplay 
              results={ocrResults} 
              fileName={uploadedFile?.name}
              selectedModel={selectedModel}
              onReset={handleReset}
            />
          )}

          {/* Multi-PDF Results */}
          {multiPdfResults && !isLoading && (
            <MultiPDFResults
              results={multiPdfResults}
              fileNames={uploadedFiles?.map(file => file.name)}
              selectedModel={selectedModel}
              onReset={handleReset}
            />
          )}
        </motion.div>
      </main>
    </div>
  )
}

export default App
