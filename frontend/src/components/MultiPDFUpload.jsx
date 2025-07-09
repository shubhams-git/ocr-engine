import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, AlertCircle, X, Plus, BarChart3, FileSpreadsheet } from 'lucide-react'

const MultiPDFUpload = ({ onFilesUpload }) => {
  const [selectedFiles, setSelectedFiles] = useState([])

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const rejectedFile = rejectedFiles[0]
      let errorMessage = 'File upload failed: '
      
      if (rejectedFile.errors) {
        const errors = rejectedFile.errors.map(error => {
          switch (error.code) {
            case 'file-too-large':
              return 'File size too large. Maximum size is 50MB for PDFs and 25MB for CSV files.'
            case 'file-invalid-type':
              return 'Only PDF and CSV files are supported for multi-document analysis.'
            case 'too-many-files':
              return 'Too many files. Maximum is 10 files.'
            default:
              return error.message
          }
        }).join(' ')
        errorMessage += errors
      } else {
        errorMessage += 'Please upload only PDF or CSV files.'
      }
      
      alert(errorMessage)
      return
    }
    
    if (acceptedFiles.length > 0) {
      const newFiles = [...selectedFiles, ...acceptedFiles]
      if (newFiles.length > 10) {
        alert('Maximum 10 files allowed. Please remove some files first.')
        return
      }
      setSelectedFiles(newFiles)
    }
  }, [selectedFiles])

  const removeFile = (indexToRemove) => {
    setSelectedFiles(files => files.filter((_, index) => index !== indexToRemove))
  }

  const handleAnalyze = () => {
    if (selectedFiles.length > 0) {
      onFilesUpload(selectedFiles)
    }
  }

  const getFileIcon = (fileName) => {
    if (fileName.toLowerCase().endsWith('.csv')) {
      return <FileSpreadsheet size={20} className="file-icon csv-icon" />
    }
    return <FileText size={20} className="file-icon pdf-icon" />
  }

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/csv': ['.csv']
    },
    multiple: true,
    maxSize: 50 * 1024 * 1024, // 50MB max per file (will validate individual file types)
    maxFiles: 10,
  })

  const getDropzoneClass = () => {
    let baseClass = 'dropzone'
    if (isDragActive) baseClass += ' drag-active'
    if (isDragAccept) baseClass += ' drag-accept'
    if (isDragReject) baseClass += ' drag-reject'
    return baseClass
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="file-upload-container"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="multi-pdf-header"
      >
        <div className="feature-icon">
          <BarChart3 size={32} />
        </div>
        <h2>Multi-Document Analysis</h2>
        <p>Upload 1-10 PDF documents and CSV files for comprehensive data analysis, normalization, and projections</p>
      </motion.div>

      {/* File Upload Area */}
      <motion.div
        {...getRootProps()}
        className={getDropzoneClass()}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        <input {...getInputProps()} />
        
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="dropzone-content"
        >
          <motion.div
            animate={{ 
              y: isDragActive ? -10 : 0,
              scale: isDragActive ? 1.1 : 1
            }}
            transition={{ type: "spring", stiffness: 300 }}
            className="upload-icon"
          >
            {isDragReject ? (
              <AlertCircle size={48} className="icon-error" />
            ) : selectedFiles.length > 0 ? (
              <Plus size={48} className="icon-upload" />
            ) : (
              <Upload size={48} className="icon-upload" />
            )}
          </motion.div>
          
          <h3 className="dropzone-title">
            {isDragActive
              ? isDragReject
                ? 'Only PDF and CSV files are supported'
                : 'Drop your files here'
              : selectedFiles.length > 0
                ? 'Add More Files'
                : 'Upload Documents'
            }
          </h3>
          
          <p className="dropzone-subtitle">
            {isDragActive
              ? ''
              : selectedFiles.length > 0
                ? `${selectedFiles.length}/10 files selected`
                : 'Drag & drop 1-10 PDF or CSV files here, or click to browse'
            }
          </p>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="supported-formats"
          >
            <div className="format-group">
              <FileText size={16} />
              <span>PDF Documents (max 50MB each)</span>
            </div>
            <div className="format-group">
              <FileSpreadsheet size={16} />
              <span>CSV Files (max 25MB each)</span>
            </div>
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Selected Files Display */}
      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="selected-files"
          >
            <h4>Selected Files ({selectedFiles.length}/10)</h4>
            <div className="files-list">
              {selectedFiles.map((file, index) => (
                <motion.div
                  key={`${file.name}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className="file-item"
                >
                  <div className="file-info">
                    {getFileIcon(file.name)}
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                  <motion.button
                    onClick={() => removeFile(index)}
                    className="remove-file"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <X size={16} />
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Buttons */}
      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="upload-actions"
          >
            <div className="action-buttons">
              <motion.button
                onClick={() => setSelectedFiles([])}
                className="action-button secondary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Clear All
              </motion.button>
              
              <motion.button
                onClick={handleAnalyze}
                disabled={selectedFiles.length === 0}
                className="action-button primary"
                whileHover={{ scale: selectedFiles.length > 0 ? 1.05 : 1 }}
                whileTap={{ scale: selectedFiles.length > 0 ? 0.95 : 1 }}
              >
                <BarChart3 size={18} />
                Analyze Documents
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Features Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="upload-features"
      >
        <div className="feature">
          <span className="feature-icon">📊</span>
          <span>Data Extraction & Normalization</span>
        </div>
        <div className="feature">
          <span className="feature-icon">📈</span>
          <span>Trend Analysis & Projections</span>
        </div>
        <div className="feature">
          <span className="feature-icon">🔄</span>
          <span>Cross-Document Comparison</span>
        </div>
        <div className="feature">
          <span className="feature-icon">🧠</span>
          <span>AI-Powered Insights</span>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default MultiPDFUpload 