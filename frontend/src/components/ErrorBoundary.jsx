import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw, Bug, Copy, ExternalLink, Home } from 'lucide-react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null,
      isRetrying: false,
      retryCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo)
    }
  }

  handleRetry = () => {
    this.setState({ 
      isRetrying: true,
      retryCount: this.state.retryCount + 1
    })
    
    setTimeout(() => {
      this.setState({ 
        hasError: false,
        error: null,
        errorInfo: null,
        isRetrying: false
      })
    }, 1000)
  }

  handleCopyError = async () => {
    const errorDetails = `
Error: ${this.state.error?.message || 'Unknown error'}
Stack: ${this.state.error?.stack || 'No stack trace'}
Component Stack: ${this.state.errorInfo?.componentStack || 'No component stack'}
Timestamp: ${new Date().toISOString()}
Retry Count: ${this.state.retryCount}
    `.trim()

    try {
      await navigator.clipboard.writeText(errorDetails)
      alert('Error details copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy error details:', err)
    }
  }

  handleReportIssue = () => {
    const errorDetails = encodeURIComponent(`
Error: ${this.state.error?.message || 'Unknown error'}
Stack: ${this.state.error?.stack || 'No stack trace'}
Component Stack: ${this.state.errorInfo?.componentStack || 'No component stack'}
    `.trim())
    
    // Open GitHub issues page (replace with actual repo URL)
    window.open(`https://github.com/yourorg/ocr-engine/issues/new?body=${errorDetails}`, '_blank')
  }

  handleResetApplication = () => {
    // Clear local storage and reload
    localStorage.clear()
    sessionStorage.clear()
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="error-container"
          >
            <div className="error-header">
              <AlertTriangle size={48} className="error-icon" />
              <h2>Something went wrong</h2>
              <p className="error-subtitle">
                The application encountered an unexpected error. Don't worry, we can help you recover.
              </p>
            </div>

            <div className="error-details">
              <div className="error-message">
                <h3>Error Details</h3>
                <div className="error-text">
                  <strong>Message:</strong> {this.state.error?.message || 'Unknown error occurred'}
                </div>
                
                {this.state.error?.stack && (
                  <details className="error-stack">
                    <summary>Stack Trace</summary>
                    <pre className="stack-trace">
                      {this.state.error.stack}
                    </pre>
                  </details>
                )}

                {this.state.errorInfo?.componentStack && (
                  <details className="error-component-stack">
                    <summary>Component Stack</summary>
                    <pre className="component-stack">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>

              <div className="error-context">
                <h3>Context Information</h3>
                <div className="context-grid">
                  <div className="context-item">
                    <span className="context-label">Timestamp:</span>
                    <span className="context-value">{new Date().toLocaleString()}</span>
                  </div>
                  <div className="context-item">
                    <span className="context-label">Retry Count:</span>
                    <span className="context-value">{this.state.retryCount}</span>
                  </div>
                  <div className="context-item">
                    <span className="context-label">User Agent:</span>
                    <span className="context-value">{navigator.userAgent}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="error-actions">
              <div className="primary-actions">
                <motion.button
                  onClick={this.handleRetry}
                  disabled={this.state.isRetrying}
                  className="action-button primary retry-button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {this.state.isRetrying ? (
                    <>
                      <RefreshCw size={18} className="spinning" />
                      Retrying...
                    </>
                  ) : (
                    <>
                      <RefreshCw size={18} />
                      Try Again
                    </>
                  )}
                </motion.button>

                <motion.button
                  onClick={this.handleResetApplication}
                  className="action-button secondary reset-button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={18} />
                  Reset Application
                </motion.button>
              </div>

              <div className="secondary-actions">
                <motion.button
                  onClick={this.handleCopyError}
                  className="action-button tertiary copy-button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Copy size={18} />
                  Copy Error Details
                </motion.button>

                <motion.button
                  onClick={this.handleReportIssue}
                  className="action-button tertiary report-button"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Bug size={18} />
                  Report Issue
                </motion.button>
              </div>
            </div>

            <div className="error-help">
              <h3>Need Help?</h3>
              <div className="help-content">
                <div className="help-item">
                  <strong>Common Solutions:</strong>
                  <ul>
                    <li>Refresh the page and try again</li>
                    <li>Clear your browser cache and cookies</li>
                    <li>Try using a different browser</li>
                    <li>Check if the backend server is running</li>
                  </ul>
                </div>
                
                <div className="help-item">
                  <strong>If the problem persists:</strong>
                  <ul>
                    <li>Copy the error details and report the issue</li>
                    <li>Check the browser console for additional information</li>
                    <li>Contact the development team</li>
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )
    }

    return this.props.children
  }
}

// Enhanced Error Display Component for non-boundary errors
export const ErrorDisplay = ({ error, onRetry, onDismiss, title = "Error" }) => {
  const [copied, setCopied] = useState(false)

  const handleCopyError = async () => {
    try {
      await navigator.clipboard.writeText(error?.message || error || 'Unknown error')
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy error:', err)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="error-display"
    >
      <div className="error-display-header">
        <AlertTriangle size={24} className="error-icon" />
        <h3>{title}</h3>
      </div>

      <div className="error-display-content">
        <p className="error-message">
          {error?.message || error || 'An unexpected error occurred'}
        </p>
        
        {error?.details && (
          <div className="error-details">
            <strong>Details:</strong> {error.details}
          </div>
        )}
      </div>

      <div className="error-display-actions">
        {onRetry && (
          <motion.button
            onClick={onRetry}
            className="action-button primary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RefreshCw size={16} />
            Retry
          </motion.button>
        )}

        <motion.button
          onClick={handleCopyError}
          className={`action-button tertiary ${copied ? 'copied' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Copy size={16} />
          {copied ? 'Copied!' : 'Copy Error'}
        </motion.button>

        {onDismiss && (
          <motion.button
            onClick={onDismiss}
            className="action-button secondary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Dismiss
          </motion.button>
        )}
      </div>
    </motion.div>
  )
}

export default ErrorBoundary 