import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Loader2, FileSearch, Brain, CheckCircle } from 'lucide-react'

const LoadingSpinner = () => {
  const [currentStep, setCurrentStep] = useState(0)
  
  const steps = [
    { icon: FileSearch, text: "Analyzing file..." },
    { icon: Brain, text: "Processing with AI..." },
    { icon: CheckCircle, text: "Extracting text..." }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % steps.length)
    }, 2000)
    
    return () => clearInterval(interval)
  }, [steps.length])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.4 }}
      className="loading-container"
    >
      <motion.div
        className="loading-content"
        initial={{ y: 20 }}
        animate={{ y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {/* Main Spinner */}
        <motion.div
          className="spinner-wrapper"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="main-spinner"
          >
            <Loader2 size={64} />
          </motion.div>
          
          {/* Orbital dots */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="orbital-dots"
          >
            <div className="dot dot-1"></div>
            <div className="dot dot-2"></div>
            <div className="dot dot-3"></div>
          </motion.div>
        </motion.div>

        {/* Processing Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="processing-steps"
        >
          <h3>Processing Your File</h3>
          
          <div className="steps-container">
            {steps.map((step, index) => {
              const Icon = step.icon
              const isActive = index === currentStep
              const isCompleted = index < currentStep
              
              return (
                <motion.div
                  key={index}
                  className={`step ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                  initial={{ opacity: 0.5, scale: 0.9 }}
                  animate={{ 
                    opacity: isActive ? 1 : 0.6,
                    scale: isActive ? 1.05 : 1
                  }}
                  transition={{ duration: 0.3 }}
                >
                  <motion.div
                    className="step-icon"
                    animate={{ 
                      rotate: isActive ? 360 : 0,
                      scale: isActive ? 1.1 : 1
                    }}
                    transition={{ 
                      rotate: { duration: 2, repeat: isActive ? Infinity : 0, ease: "linear" },
                      scale: { duration: 0.3 }
                    }}
                  >
                    <Icon size={20} />
                  </motion.div>
                  <span className="step-text">{step.text}</span>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: 1, width: "100%" }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="progress-container"
        >
          <div className="progress-bar">
            <motion.div
              className="progress-fill"
              initial={{ width: "0%" }}
              animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <span className="progress-text">
            {Math.round(((currentStep + 1) / steps.length) * 100)}%
          </span>
        </motion.div>

        {/* Fun fact */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="loading-tip"
        >
          💡 Our AI can process multiple languages and complex layouts
        </motion.p>
      </motion.div>
    </motion.div>
  )
}

export default LoadingSpinner 