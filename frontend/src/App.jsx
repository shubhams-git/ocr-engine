import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import FileUpload from './components/FileUpload'
import ResultsDisplay from './components/ResultsDisplay'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'
import { processOCR, getHealthStatus, getAvailableModels } from './services/api'
import './App.css'

function App() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [ocrResults, setOcrResults] = useState(null)
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

  const handleReset = () => {
    setUploadedFile(null)
    setOcrResults(null)
    setError(null)
    setIsLoading(false)
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
          {/* Model Selection */}
          {!uploadedFile && !isLoading && !ocrResults && availableModels.length > 0 && (
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

          {!uploadedFile && !isLoading && !ocrResults && (
            <FileUpload onFileUpload={handleFileUpload} />
          )}

          {isLoading && <LoadingSpinner />}

          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="error-container"
            >
              <div className="error-message">
                <h3>Error Processing File</h3>
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

          {ocrResults && !isLoading && (
            <ResultsDisplay 
              results={ocrResults} 
              fileName={uploadedFile?.name}
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
