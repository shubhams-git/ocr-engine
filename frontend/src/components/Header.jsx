import { motion } from 'framer-motion'
import { Eye, FileText, Zap } from 'lucide-react'

const Header = ({ backendStatus = 'unknown' }) => {
  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Backend Connected'
      case 'disconnected':
        return 'Backend Offline (Mock Mode)'
      default:
        return 'Checking Backend...'
    }
  }

  return (
    <header className="header">
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="header-content"
      >
        <motion.div
          className="logo"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Eye className="logo-icon" />
          <h1>OCR Engine Tester</h1>
        </motion.div>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="header-description"
        >
          Upload images or documents to extract text using advanced AI models
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="feature-badges"
        >
          <div className="badge">
            <FileText size={16} />
            <span>Multiple Formats</span>
          </div>
          <div className="badge">
            <Zap size={16} />
            <span>AI Powered</span>
          </div>
          <div className={`badge backend-status ${backendStatus}`}>
            <div className={`status-indicator ${backendStatus}`}></div>
            <span>{getStatusText(backendStatus)}</span>
          </div>
        </motion.div>
      </motion.div>
    </header>
  )
}

export default Header 