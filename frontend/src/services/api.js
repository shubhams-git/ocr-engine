import axios from 'axios'

// Configure base URL - you can change this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Development mode flag
const isDevelopment = import.meta.env.DEV
const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true' || !import.meta.env.VITE_API_URL

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making API request to: ${config.url}`)
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
      const message = error.response.data?.message || error.response.data?.error || 'Server error occurred'
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

    // Make API request
    const startTime = Date.now()
    const response = await apiClient.post('/ocr/process', formData)
    const endTime = Date.now()

    // Add processing time to response
    const result = {
      ...response.data,
      processingTime: endTime - startTime
    }

    return result
  } catch (error) {
    throw error
  }
}

/**
 * Get available models
 * @returns {Promise<Array>} - List of available models
 */
export const getAvailableModels = async () => {
  try {
    const response = await apiClient.get('/models')
    return response.data
  } catch (error) {
    console.warn('Failed to fetch models:', error.message)
    // Return default models if API fails
    return [
      { id: 'openai-gpt4-vision', name: 'OpenAI GPT-4 Vision', provider: 'openai' },
      { id: 'gemini-pro-vision', name: 'Google Gemini Pro Vision', provider: 'google' },
      { id: 'claude-3-vision', name: 'Anthropic Claude 3 Vision', provider: 'anthropic' },
      { id: 'mistral-vision', name: 'Mistral Vision', provider: 'mistral' }
    ]
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
 * Mock API function for testing when backend is not available
 * @param {File} file - The file to process
 * @returns {Promise<Object>} - Mock OCR results
 */
export const mockProcessOCR = async (file) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000))
  
  // Return mock data
  return {
    text: `Mock OCR Results for: ${file.name}
    
This is a simulated OCR response. In a real implementation, this would contain the actual text extracted from your uploaded image or PDF.

The text extraction would be performed by advanced AI models like:
- OpenAI GPT-4 Vision
- Google Gemini Pro Vision  
- Anthropic Claude 3 Vision
- Mistral Vision

Your file: ${file.name}
File size: ${(file.size / 1024).toFixed(2)} KB
File type: ${file.type}

This mock response demonstrates the structure that the frontend expects from the backend API.`,
    confidence: 0.95,
    metadata: {
      model: 'mock-model',
      language: 'en',
      pages: 1,
      words: 87,
      characters: 542
    }
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
  mockProcessOCR
} 