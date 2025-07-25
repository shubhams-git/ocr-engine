import axios from 'axios'

// Configure base URL to match actual backend
const API_BASE_URL = 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minute timeout
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'Server error occurred'
      throw new Error(`${error.response.status}: ${message}`)
    } else if (error.request) {
      // Request made but no response received
      throw new Error('No response from server. Please check if the backend is running.')
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
)

/**
 * Get file size limit based on file type
 * @param {File} file - The file to check
 * @returns {number} - Size limit in bytes
 */
const getFileSizeLimit = (file) => {
  const fileName = file.name.toLowerCase()
  
  if (fileName.endsWith('.pdf')) {
    return 50 * 1024 * 1024 // 50MB for PDFs
  } else if (fileName.endsWith('.csv')) {
    return 25 * 1024 * 1024 // 25MB for CSV files
  } else {
    return 10 * 1024 * 1024 // 10MB for images
  }
}

/**
 * Validate file type and size
 * @param {File} file - The file to validate
 * @throws {Error} - If file is invalid
 */
const validateFile = (file) => {
  if (!file) {
    throw new Error('No file provided')
  }

  const fileName = file.name.toLowerCase()
  const fileType = file.type.toLowerCase()
  
  // Check file type
  const isImage = fileType.startsWith('image/') || 
    ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'].some(ext => fileName.endsWith(ext))
  const isPDF = fileType === 'application/pdf' || fileName.endsWith('.pdf')
  const isCSV = fileType.includes('csv') || fileName.endsWith('.csv') ||
    fileType === 'text/csv' || fileType === 'application/csv' || fileType === 'application/vnd.ms-excel'
  
  if (!isImage && !isPDF && !isCSV) {
    throw new Error('Unsupported file type. Please upload an image (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP), PDF, or CSV file.')
  }

  // Check file size based on type
  const sizeLimit = getFileSizeLimit(file)
  if (file.size > sizeLimit) {
    const sizeLimitMB = Math.round(sizeLimit / (1024 * 1024))
    const fileType = isPDF ? 'PDF' : isCSV ? 'CSV' : 'image'
    throw new Error(`File size too large. Maximum size for ${fileType} files is ${sizeLimitMB}MB.`)
  }
}

/**
 * Process OCR on uploaded file
 * @param {File} file - The file to process
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} - OCR results
 */
export const processOCR = async (file, options = {}) => {
  // Validate file
  validateFile(file)

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)
  
  // Add model if specified
  if (options.model) {
    formData.append('model', options.model)
  }

  // Make API request
  const response = await apiClient.post('/ocr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  })

  return response.data
}

/**
 * Get API health status
 * @returns {Promise<Object>} - Health status
 */
export const getHealthStatus = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

/**
 * Get available models
 * @returns {Promise<Object>} - Available models information
 */
export const getAvailableModels = async () => {
  const response = await apiClient.get('/models')
  return response.data
}

/**
 * Process multi-PDF analysis
 * @param {File[]} files - Array of PDF files to analyze
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} - Multi-PDF analysis results
 */
export const processMultiPDFAnalysis = async (files, options = {}) => {
  // Validate files
  if (!files || files.length === 0) {
    throw new Error('No files provided')
  }

  if (files.length > 10) {
    throw new Error('Too many files. Maximum is 10 files.')
  }

  // Check each file
  for (const file of files) {
    const fileName = file.name.toLowerCase()
    const fileType = file.type.toLowerCase()
    
    // Check if file is PDF or CSV
    const isPDF = fileType === 'application/pdf' || fileName.endsWith('.pdf')
    const isCSV = fileType.includes('csv') || fileName.endsWith('.csv') ||
      fileType === 'text/csv' || fileType === 'application/csv' || fileType === 'application/vnd.ms-excel'
    
    if (!isPDF && !isCSV) {
      throw new Error(`File ${file.name} is not a supported file type. Please upload PDF or CSV files only.`)
    }
    
    // Check file size based on type (PDFs: 50MB, CSVs: 25MB)
    const maxSize = isPDF ? 50 * 1024 * 1024 : 25 * 1024 * 1024
    const maxSizeMB = isPDF ? 50 : 25
    
    if (file.size > maxSize) {
      const fileTypeStr = isPDF ? 'PDF' : 'CSV'
      throw new Error(`File ${file.name} is too large. Maximum size for ${fileTypeStr} files is ${maxSizeMB}MB.`)
    }
  }

  // Create FormData
  const formData = new FormData()
  
  // Add all files
  files.forEach(file => {
    formData.append('files', file)
  })
  
  // Add model if specified
  if (options.model) {
    formData.append('model', options.model)
  }

  // Make API request with longer timeout for multiple files
  const response = await apiClient.post('/multi-pdf/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 600000, // 10 minutes timeout for multi-PDF processing
  })

  return response.data
}

// Export functions
export default {
  processOCR,
  processMultiPDFAnalysis,
  getHealthStatus,
  getAvailableModels
} 