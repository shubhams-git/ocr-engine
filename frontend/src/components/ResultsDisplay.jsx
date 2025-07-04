import { useState } from 'react'
import { motion } from 'framer-motion'
import { Copy, Download, RefreshCw, CheckCircle, FileText, Clock, Zap, Cpu } from 'lucide-react'

const ResultsDisplay = ({ results, fileName, onReset }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(results.text || '')
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  const handleDownload = () => {
    const element = document.createElement('a')
    const file = new Blob([results.text || ''], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `${fileName?.split('.')[0] || 'ocr'}_extracted.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown'
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getWordsCount = () => {
    return (results.text || '').split(/\s+/).filter(word => word.length > 0).length
  }

  const getCharactersCount = () => {
    return (results.text || '').length
  }

  const getLinesCount = () => {
    return (results.text || '').split('\n').filter(line => line.trim().length > 0).length
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="results-container"
    >
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="results-header"
      >
        <div className="success-badge">
          <CheckCircle className="success-icon" />
          <span>Text Extracted Successfully!</span>
        </div>
        
        <div className="file-info">
          <FileText className="file-icon" />
          <div className="file-details">
            <h3>{results.file_name || fileName || 'Uploaded File'}</h3>
            <div className="file-meta">
              <span className="meta-item">
                <Clock size={14} />
                {results.processing_time_ms}ms
              </span>
              <span className="meta-item">
                <Cpu size={14} />
                {results.model_used}
              </span>
              {results.file_size && (
                <span className="meta-item">
                  <Zap size={14} />
                  {formatFileSize(results.file_size)}
                </span>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="results-stats"
      >
        <div className="stat">
          <div className="stat-value">{getWordsCount()}</div>
          <div className="stat-label">Words</div>
        </div>
        <div className="stat">
          <div className="stat-value">{getCharactersCount()}</div>
          <div className="stat-label">Characters</div>
        </div>
        <div className="stat">
          <div className="stat-value">{getLinesCount()}</div>
          <div className="stat-label">Lines</div>
        </div>
        <div className="stat">
          <div className="stat-value">{results.processing_time_ms}ms</div>
          <div className="stat-label">Processing Time</div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="results-actions"
      >
        <motion.button
          onClick={handleCopy}
          className={`action-button copy-button ${copied ? 'copied' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={copied}
        >
          {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
          {copied ? 'Copied!' : 'Copy Text'}
        </motion.button>
        
        <motion.button
          onClick={handleDownload}
          className="action-button download-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Download size={18} />
          Download
        </motion.button>
        
        <motion.button
          onClick={onReset}
          className="action-button reset-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <RefreshCw size={18} />
          Process Another
        </motion.button>
      </motion.div>

      {/* Extracted Text Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="extracted-text-container"
      >
        <h3>Extracted Text</h3>
        <motion.div
          className="text-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <pre className="extracted-text">
            {results.text || 'No text found in the document.'}
          </pre>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}

export default ResultsDisplay 