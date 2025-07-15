import axios from 'axios'

// Configure base URL to match actual backend
const API_BASE_URL = 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: import.meta.env.VITE_API_TIMEOUT || 600000, // 10 minute timeout (from env or default)
})

// Utility function to clean and parse JSON responses
const cleanAndParseJSON = (responseText) => {
  try {
    // If it's already an object, return as is
    if (typeof responseText === 'object' && responseText !== null) {
      return responseText
    }
    
    // Convert to string if needed
    let cleanText = String(responseText)
    
    // Remove leading/trailing whitespace
    cleanText = cleanText.trim()
    
    // Remove markdown code blocks
    cleanText = cleanText.replace(/^```(?:json)?\s*\n?/i, '')
    cleanText = cleanText.replace(/\n?```\s*$/i, '')
    
    // Remove any leading text before JSON (look for first { or [)
    const jsonStart = Math.min(
      cleanText.indexOf('{') !== -1 ? cleanText.indexOf('{') : Infinity,
      cleanText.indexOf('[') !== -1 ? cleanText.indexOf('[') : Infinity
    )
    
    if (jsonStart !== Infinity && jsonStart > 0) {
      cleanText = cleanText.substring(jsonStart)
    }
    
    // Remove any trailing text after JSON (look for last } or ])
    let jsonEnd = Math.max(
      cleanText.lastIndexOf('}'),
      cleanText.lastIndexOf(']')
    )
    
    if (jsonEnd !== -1 && jsonEnd < cleanText.length - 1) {
      cleanText = cleanText.substring(0, jsonEnd + 1)
    }
    
    // Parse the cleaned JSON
    return JSON.parse(cleanText)
  } catch (parseError) {
    console.error('JSON parsing failed:', parseError)
    console.error('Original text:', responseText)
    throw new Error(`Invalid JSON response: ${parseError.message}`)
  }
}

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Clean and parse JSON responses if needed
    if (response.data && typeof response.data === 'string') {
      try {
        response.data = cleanAndParseJSON(response.data)
      } catch (error) {
        console.warn('Failed to parse response as JSON:', error.message)
        // Keep original response if parsing fails
      }
    }
    return response
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      let message = 'Server error occurred'
      
      if (error.response.data) {
        if (typeof error.response.data === 'string') {
          message = error.response.data
        } else if (error.response.data.detail) {
          message = typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail)
        } else if (error.response.data.error) {
          message = typeof error.response.data.error === 'string' 
            ? error.response.data.error 
            : JSON.stringify(error.response.data.error)
        } else {
          message = JSON.stringify(error.response.data)
        }
      }
      
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

/**
 * Get detailed health status of all services
 * @returns {Promise<Object>} - Detailed health status
 */
export const getDetailedHealth = async () => {
  const response = await apiClient.get('/admin/health/detailed')
  return response.data
}

/**
 * Test Stage 1 (OCR Service) independently
 * @param {File} file - File to test
 * @param {string} model - Model to use
 * @returns {Promise<Object>} - Test results
 */
export const testStage1 = async (file, model = 'gemini-2.5-flash') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('model', model)
  
  const response = await apiClient.post('/admin/test/stage1', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  })
  return response.data
}

/**
 * Test Stage 2 (Business Analysis Service) independently
 * @param {Array} extractedData - Extracted data from Stage 1
 * @param {string} model - Model to use
 * @returns {Promise<Object>} - Test results
 */
export const testStage2 = async (extractedData, model = 'gemini-2.5-flash') => {
  console.log('testStage2 - Input extractedData:', extractedData)
  console.log('testStage2 - Type check:', Array.isArray(extractedData))
  console.log('testStage2 - Model:', model)
  
  // Validate input data
  if (!extractedData || !Array.isArray(extractedData)) {
    throw new Error('Invalid extracted data: Expected an array of extraction results')
  }
  
  if (extractedData.length === 0) {
    throw new Error('No extracted data provided: Array is empty')
  }
  
  // Validate each extraction result has required structure
  for (let i = 0; i < extractedData.length; i++) {
    const item = extractedData[i]
    if (!item || typeof item !== 'object') {
      throw new Error(`Invalid extraction result at index ${i}: Expected object`)
    }
    if (!item.hasOwnProperty('filename') || !item.hasOwnProperty('success') || !item.hasOwnProperty('data')) {
      console.warn(`Extraction result at index ${i} missing required fields:`, item)
      throw new Error(`Invalid extraction result at index ${i}: Missing required fields (filename, success, data)`)
    }
  }
  
  const requestBody = {
    extracted_data: extractedData,
    model: model
  }
  
  console.log('testStage2 - Validated request body:', requestBody)
  
  try {
    const response = await apiClient.post('/admin/test/stage2', requestBody, {
      timeout: 300000, // 5 minute timeout for Stage 2
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    console.log('testStage2 - Raw response:', response)
    console.log('testStage2 - Response data:', response.data)
    
    return response.data
  } catch (error) {
    console.error('testStage2 - Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      extractedDataSample: extractedData.slice(0, 1) // Log first item for debugging
    })
    
    // Provide more specific error messages
    if (error.response?.status === 422) {
      throw new Error(`Validation error: ${error.response.data?.detail || 'Invalid request format'}`)
    } else if (error.response?.status === 500) {
      throw new Error(`Server error in Stage 2: ${error.response.data?.detail || error.message}`)
    }
    
    throw error
  }
}

/**
 * Test Stage 3 (Projection Service) independently
 * @param {Object} businessAnalysis - Business analysis data from Stage 2
 * @param {string} model - Model to use
 * @returns {Promise<Object>} - Test results
 */
export const testStage3 = async (businessAnalysis, model = 'gemini-2.5-flash') => {
  const response = await apiClient.post('/admin/test/stage3', {
    business_analysis: businessAnalysis,
    model: model
  })
  return response.data
}

/**
 * Test the complete 3-stage process with detailed timing
 * @param {File[]} files - Files to test
 * @param {string} model - Model to use
 * @returns {Promise<Object>} - Test results
 */
export const testFullProcess = async (files, model = 'gemini-2.5-flash') => {
  const formData = new FormData()
  
  files.forEach(file => {
    formData.append('files', file)
  })
  formData.append('model', model)
  
  const response = await apiClient.post('/admin/test/full-process', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 600000, // 10 minutes timeout for full process
  })
  return response.data
}

/**
 * Validate all services are properly configured
 * @returns {Promise<Object>} - Validation results
 */
export const validateServices = async () => {
  const response = await apiClient.get('/admin/test/validate-services')
  return response.data
}

/**
 * Get performance metrics for the system
 * @returns {Promise<Object>} - Performance metrics
 */
export const getPerformanceMetrics = async () => {
  const response = await apiClient.get('/admin/performance/metrics')
  return response.data
}

// Export functions
export default {
  processOCR,
  processMultiPDFAnalysis,
  getHealthStatus,
  getAvailableModels,
  // Testing functions
  getDetailedHealth,
  testStage1,
  testStage2,
  testStage3,
  testFullProcess,
  validateServices,
  getPerformanceMetrics
} 