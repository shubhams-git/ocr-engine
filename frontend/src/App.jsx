import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import FileUpload from './components/FileUpload'
import ResultsDisplay from './components/ResultsDisplay'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'
import { processOCRWithFallback as processOCR, getAvailableModels, getHealthStatus } from './services/api'
import './App.css'

function App() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [ocrResults, setOcrResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [availableModels, setAvailableModels] = useState([])
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash')
  const [backendStatus, setBackendStatus] = useState('unknown')

  // Check backend status and load models on component mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check backend health
        await getHealthStatus()
        setBackendStatus('connected')
        
        // Load available models
        const modelsData = await getAvailableModels()
        setAvailableModels(modelsData.models || modelsData)
        if (modelsData.default) {
          setSelectedModel(modelsData.default)
        }
      } catch (err) {
        console.warn('Backend not available:', err.message)
        setBackendStatus('disconnected')
        // Load default models for offline mode
        const modelsData = await getAvailableModels()
        setAvailableModels(modelsData.models || modelsData)
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
      const options = {
        model: selectedModel,
        language: 'en' // You can add language selection later
      }
      
      const results = await processOCR(file, options)
      setOcrResults(results)
    } catch (err) {
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
                      <span className="model-name">{model.name}</span>
                      {model.description && (
                        <span className="model-description">{model.description}</span>
                      )}
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
                <button onClick={handleReset} className="retry-button">
                  Try Again
                </button>
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
