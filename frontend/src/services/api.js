import axios from 'axios'

// Configure base URL - you can change this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Development mode flag
const isDevelopment = import.meta.env.DEV
const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true' || !import.meta.env.VITE_API_URL

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for OCR processing
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making API request to: ${config.baseURL}${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || error.response.data?.message || 'Server error occurred'
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
  try {
    // Validate file
    if (!file) {
      throw new Error('No file provided')
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      throw new Error('File size too large. Maximum size is 10MB.')
    }

    // Check file type
    const allowedTypes = [
      'image/png',
      'image/jpeg',
      'image/jpg',
      'image/gif',
      'image/bmp',
      'image/tiff',
      'image/webp',
      'application/pdf'
    ]
    
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Unsupported file type. Please upload an image or PDF file.')
    }

    // Create FormData
    const formData = new FormData()
    formData.append('file', file)
    
    // Add any additional options
    if (options.model) {
      formData.append('model', options.model)
    }
    if (options.language) {
      formData.append('language', options.language)
    }

    // Make API request with proper headers for file upload
    const response = await apiClient.post('/ocr/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })

    // Process backend response
    const result = response.data
    
    // Ensure consistent response format for frontend
    return {
      text: result.text,
      extractedText: result.text, // Alias for backward compatibility
      confidence: result.confidence,
      metadata: result.metadata,
      processingTime: result.processing_time_ms, // Use backend's timing
      processing_time_ms: result.processing_time_ms // Keep original field
    }
  } catch (error) {
    throw error
  }
}

/**
 * Get available models
 * @returns {Promise<Object>} - Available models information
 */
export const getAvailableModels = async () => {
  try {
    const response = await apiClient.get('/models')
    return response.data
  } catch (error) {
    console.warn('Failed to fetch models:', error.message)
    // Return default Gemini models if API fails
    return {
      models: [
        { 
          id: 'gemini-2.5-pro', 
          name: 'Gemini 2.5 Pro', 
          provider: 'google',
          description: 'Most capable model for complex OCR tasks'
        },
        { 
          id: 'gemini-2.5-flash', 
          name: 'Gemini 2.5 Flash', 
          provider: 'google',
          description: 'Fast and efficient model for quick OCR (recommended)'
        },
        { 
          id: 'gemini-1.5-pro', 
          name: 'Gemini 1.5 Pro', 
          provider: 'google',
          description: 'Previous generation pro model'
        },
        { 
          id: 'gemini-1.5-flash', 
          name: 'Gemini 1.5 Flash', 
          provider: 'google',
          description: 'Previous generation flash model'
        }
      ],
      default: 'gemini-2.5-flash',
      recommended: 'gemini-2.5-flash',
      total_count: 4
    }
  }
}

/**
 * Get API health status
 * @returns {Promise<Object>} - Health status
 */
export const getHealthStatus = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Backend service is not available')
  }
}

/**
 * Get supported file formats
 * @returns {Promise<Object>} - Supported formats
 */
export const getSupportedFormats = async () => {
  try {
    const response = await apiClient.get('/formats')
    return response.data
  } catch (error) {
    console.warn('Failed to fetch supported formats:', error.message)
    // Return default formats if API fails
    return {
      supported_formats: {
        images: {
          extensions: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
          mime_types: ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp']
        },
        documents: {
          extensions: ['.pdf'],
          mime_types: ['application/pdf']
        }
      },
      total_types: 8
    }
  }
}

/**
 * Get API statistics
 * @returns {Promise<Object>} - API usage statistics
 */
export const getApiStats = async () => {
  try {
    const response = await apiClient.get('/stats')
    return response.data
  } catch (error) {
    console.warn('Failed to fetch API stats:', error.message)
    return null
  }
}

/**
 * Enhanced mock API function that simulates real OCR processing
 * @param {File} file - The file to process
 * @returns {Promise<Object>} - Mock OCR results
 */
export const mockProcessOCR = async (file) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000))
  
  // Generate realistic mock data based on file type
  let mockText = ""
  let confidence = 0.95
  
  if (file.type === 'application/pdf') {
    mockText = `Mock PDF OCR Results for: ${file.name}

This is a simulated OCR response for a PDF document. In a real implementation, this would contain the actual text extracted from your uploaded PDF.

The text extraction would be performed by advanced AI models like:
- Gemini 2.5 Pro
- Gemini 2.5 Flash (recommended)
- Gemini 1.5 Pro
- Gemini 1.5 Flash

Your PDF file: ${file.name}
File size: ${(file.size / 1024).toFixed(2)} KB
File type: ${file.type}

This mock response demonstrates the structure that the frontend expects from the backend API. The real backend would use Google's Gemini API to extract text from your PDF document.`
  } else {
    mockText = `Mock Image OCR Results for: ${file.name}

This is a simulated OCR response for an image file. In a real implementation, this would contain the actual text extracted from your uploaded image.

The text extraction would be performed by advanced AI models like:
- Gemini 2.5 Pro
- Gemini 2.5 Flash (recommended)
- Gemini 1.5 Pro
- Gemini 1.5 Flash

Your image file: ${file.name}
File size: ${(file.size / 1024).toFixed(2)} KB
File type: ${file.type}

This mock response demonstrates the structure that the frontend expects from the backend API. The real backend would use Google's Gemini API to extract text from your image.`
  }
  
  // Return mock data
  return {
    text: mockText,
    extractedText: mockText, // Alias for compatibility
    confidence: confidence,
    metadata: {
      model: 'gemini-2.5-flash',
      language: 'en',
      filename: file.name,
      file_type: file.type,
      file_size: file.size,
      pages: 1,
      words: mockText.split(/\s+/).length,
      characters: mockText.length
    },
    processingTime: 2500,
    processing_time_ms: 2500
  }
}

// Development helper: Use mock API if backend is not available
export const processOCRWithFallback = async (file, options = {}) => {
  // If explicitly in mock mode, always use mock
  if (MOCK_MODE) {
    console.log('Running in mock mode - using mock OCR data')
    return await mockProcessOCR(file)
  }

  // In development, try real API first, fallback to mock if it fails
  if (isDevelopment) {
    try {
      // Try real API first
      await getHealthStatus()
      return await processOCR(file, options)
    } catch (error) {
      console.warn('Backend not available, using mock data:', error.message)
      return await mockProcessOCR(file)
    }
  } else {
    // In production, always try real API
    return await processOCR(file, options)
  }
}

export default {
  processOCR,
  processOCRWithFallback,
  getAvailableModels,
  getHealthStatus,
  getSupportedFormats,
  getApiStats,
  mockProcessOCR
} 