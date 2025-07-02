import { useState } from 'react'
import { motion } from 'framer-motion'
import FileUpload from './components/FileUpload'
import ResultsDisplay from './components/ResultsDisplay'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'
import { processOCRWithFallback as processOCR } from './services/api'
import './App.css'

function App() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [ocrResults, setOcrResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileUpload = async (file) => {
    setUploadedFile(file)
    setIsLoading(true)
    setError(null)
    setOcrResults(null)

    try {
      const results = await processOCR(file)
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
      <Header />
      
      <main className="main-content">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="container"
        >
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
              onReset={handleReset}
            />
          )}
        </motion.div>
      </main>
      </div>
  )
}

export default App
