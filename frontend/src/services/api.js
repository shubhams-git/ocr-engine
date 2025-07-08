import axios from 'axios'

// Configure base URL to match actual backend
const API_BASE_URL = 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 1 minute timeout
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
 * Process OCR on uploaded file
 * @param {File} file - The file to process
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} - OCR results
 */
export const processOCR = async (file, options = {}) => {
  // Validate file
  if (!file) {
    throw new Error('No file provided')
  }

  // Check file size (50MB limit)
  if (file.size > 50 * 1024 * 1024) {
    throw new Error('File size too large. Maximum size is 50MB.')
  }

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
    if (file.size > 50 * 1024 * 1024) {
      throw new Error(`File ${file.name} is too large. Maximum size is 50MB.`)
    }
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      throw new Error(`File ${file.name} is not a PDF. Only PDF files are supported.`)
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
    timeout: 180000, // 3 minutes timeout for multi-PDF processing
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