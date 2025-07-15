import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, RefreshCw, Download, HelpCircle, 
  FileText, Brain, TrendingUp, Layers, Activity,
  CheckCircle, XCircle, Clock, AlertTriangle,
  Server, Database, Zap, BarChart3,
  ChevronRight, Play, Copy, Eye, EyeOff, TestTube
} from 'lucide-react'
import TestingGuide from './TestingGuide'
import {
  getDetailedHealth,
  testStage1,
  testStage2,
  testStage3,
  testFullProcess,
  validateServices,
  getPerformanceMetrics
} from '../services/api'

const TestingDashboard = ({ onExitTesting }) => {
  const [activeTest, setActiveTest] = useState(null)
  const [testResults, setTestResults] = useState({})
  const [stageData, setStageData] = useState({}) // Store extracted data for chaining
  const [systemHealth, setSystemHealth] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash')
  const [isLoading, setIsLoading] = useState(false)
  const [showGuide, setShowGuide] = useState(false)
  const [expandedResults, setExpandedResults] = useState({})

  // Available test modes with dependency tracking
  const testModes = [
    {
      id: 'stage1',
      name: 'Stage 1: OCR Service',
      description: 'Test data extraction and normalization',
      icon: FileText,
      color: 'var(--primary)',
      requires: 'file',
      dependsOn: null
    },
    {
      id: 'stage2',
      name: 'Stage 2: Business Analysis',
      description: 'Test business intelligence analysis',
      icon: Brain,
      color: 'var(--secondary)',
      requires: 'stage1',
      dependsOn: 'stage1'
    },
    {
      id: 'stage3',
      name: 'Stage 3: Projection Engine',
      description: 'Test financial projections',
      icon: TrendingUp,
      color: 'var(--success)',
      requires: 'stage2',
      dependsOn: 'stage2'
    },
    {
      id: 'full',
      name: 'Full Process',
      description: 'Test complete 3-stage pipeline',
      icon: Layers,
      color: 'var(--warning)',
      requires: 'files',
      dependsOn: null
    }
  ]

  useEffect(() => {
    fetchSystemHealth()
  }, [])

  const fetchSystemHealth = async () => {
    try {
      const health = await getDetailedHealth()
      setSystemHealth(health)
    } catch (error) {
      console.error('Failed to fetch system health:', error)
      setSystemHealth({ status: 'unhealthy', error: error.message })
    }
  }

  // Extract data from stage results for chaining
  const extractStageData = (result, stage) => {
    if (!result || !result.success) {
      console.error(`extractStageData - ${stage}: Result is null or unsuccessful:`, result)
      return null
    }

    switch (stage) {
      case 'stage1':
        // Stage 2 expects an array of extraction results with specific structure
        try {
          console.log('extractStageData stage1 - Input result:', result)
          console.log('extractStageData stage1 - result.result:', result.result)
          console.log('extractStageData stage1 - result.result.data:', result.result?.data)
          console.log('extractStageData stage1 - file_info:', result.file_info)
          
          let parsedData = null
          
          // Handle different possible data structures
          if (result.result?.data) {
            if (typeof result.result.data === 'string') {
              try {
                parsedData = JSON.parse(result.result.data)
              } catch (parseError) {
                console.error('Failed to parse result.result.data as JSON:', parseError)
                console.error('Raw data:', result.result.data)
                return null
              }
            } else if (typeof result.result.data === 'object') {
              parsedData = result.result.data
            }
          } else if (result.data) {
            // Sometimes data might be directly in result.data
            parsedData = typeof result.data === 'string' ? JSON.parse(result.data) : result.data
          } else {
            console.error('No data found in Stage 1 result')
            return null
          }
          
          console.log('extractStageData stage1 - Parsed data:', parsedData)
          
          if (!parsedData) {
            console.error('No parsed data available for Stage 2')
            return null
          }
          
          // Ensure we have the required filename
          const filename = result.file_info?.filename || 
                          result.file_info?.name || 
                          parsedData.source_filename || 
                          'test-file.pdf'
          
          // Format as expected by Stage 2 API (array of extraction results)
          const formattedData = [{
            filename: filename,
            success: true,
            data: parsedData,
            raw_response: typeof result.result?.data === 'string' ? result.result.data : JSON.stringify(parsedData)
          }]
          
          console.log('extractStageData stage1 - Formatted data:', formattedData)
          
          // Validate the formatted data structure
          if (!formattedData[0].data || typeof formattedData[0].data !== 'object') {
            console.error('Invalid data structure for Stage 2:', formattedData[0])
            return null
          }
          
          return formattedData
        } catch (error) {
          console.error('Failed to extract Stage 1 data:', error)
          console.error('Raw result:', result)
          return null
        }
      case 'stage2':
        // Extract business analysis data - handle different response structures
        try {
          let businessData = result.result || result.data || result
          
          // If it's a string, try to parse it
          if (typeof businessData === 'string') {
            businessData = JSON.parse(businessData)
          }
          
          console.log('extractStageData stage2 - Business data:', businessData)
          return businessData
        } catch (error) {
          console.error('Failed to extract Stage 2 data:', error)
          return null
        }
      default:
        console.warn(`Unknown stage: ${stage}`)
        return null
    }
  }

  const canRunStage = (stageId) => {
    const mode = testModes.find(m => m.id === stageId)
    if (!mode) return false

    // Stage 1 and full process can run if files are selected
    if (stageId === 'stage1' || stageId === 'full') {
      return selectedFiles.length > 0
    }

    // Stage 2 needs Stage 1 to be completed successfully
    if (stageId === 'stage2') {
      return testResults.stage1?.success && stageData.stage1
    }

    // Stage 3 needs Stage 2 to be completed successfully
    if (stageId === 'stage3') {
      return testResults.stage2?.success && stageData.stage2
    }

    return false
  }

  const getStageStatus = (stageId) => {
    if (testResults[stageId]?.success) return 'completed'
    if (testResults[stageId] && !testResults[stageId].success) return 'failed'
    if (canRunStage(stageId)) return 'ready'
    return 'waiting'
  }

  const runTest = async (testType) => {
    setIsLoading(true)
    setActiveTest(testType)

    try {
      let result
      console.log(`\n=== Running ${testType.toUpperCase()} Test ===`)
      console.log('Selected model:', selectedModel)
      console.log('Available stage data:', Object.keys(stageData))

      switch (testType) {
        case 'stage1':
          if (selectedFiles.length === 0) {
            throw new Error('Please select a file for Stage 1 testing')
          }
          console.log('Stage 1 - Selected file:', selectedFiles[0].name, 'Size:', selectedFiles[0].size)
          result = await testStage1(selectedFiles[0], selectedModel)
          console.log('Stage 1 - Raw result:', result)
          break

        case 'stage2':
          // Automatically use stage1 data
          if (!stageData.stage1) {
            throw new Error('Stage 1 must be completed first. Please run Stage 1 test successfully before Stage 2.')
          }
          
          console.log('Stage 2 - Available stage1 data:', stageData.stage1)
          console.log('Stage 2 - Data type check:', Array.isArray(stageData.stage1))
          console.log('Stage 2 - Data length:', stageData.stage1?.length)
          
          // Additional validation
          if (!Array.isArray(stageData.stage1) || stageData.stage1.length === 0) {
            throw new Error('Invalid Stage 1 data: Expected non-empty array')
          }
          
          // Validate the first item structure
          const firstItem = stageData.stage1[0]
          console.log('Stage 2 - First item structure:', firstItem)
          
          if (!firstItem.filename || !firstItem.data) {
            throw new Error('Invalid Stage 1 data structure: Missing filename or data')
          }
          
          console.log('Stage 2 - Sending data to backend...')
          result = await testStage2(stageData.stage1, selectedModel)
          console.log('Stage 2 - Raw result:', result)
          break

        case 'stage3':
          // Automatically use stage2 data
          if (!stageData.stage2) {
            throw new Error('Stage 2 must be completed first. Please run Stage 2 test successfully before Stage 3.')
          }
          
          console.log('Stage 3 - Available stage2 data:', stageData.stage2)
          console.log('Stage 3 - Sending data to backend...')
          result = await testStage3(stageData.stage2, selectedModel)
          console.log('Stage 3 - Raw result:', result)
          break

        case 'full':
          if (selectedFiles.length === 0) {
            throw new Error('Please select files for full process testing')
          }
          console.log('Full Process - Selected files:', selectedFiles.map(f => f.name))
          result = await testFullProcess(selectedFiles, selectedModel)
          console.log('Full Process - Raw result:', result)
          break

        default:
          throw new Error(`Unknown test type: ${testType}`)
      }

      console.log(`${testType.toUpperCase()} - Test completed successfully`)

      // Store test result
      setTestResults(prev => ({
        ...prev,
        [testType]: {
          ...result,
          timestamp: Date.now()
        }
      }))

      // Extract data for next stage if successful
      if (result.success) {
        console.log(`${testType.toUpperCase()} - Extracting data for next stage...`)
        const extractedData = extractStageData(result, testType)
        
        if (extractedData) {
          console.log(`${testType.toUpperCase()} - Successfully extracted data:`, extractedData)
          setStageData(prev => ({
            ...prev,
            [testType]: extractedData
          }))
        } else {
          console.warn(`${testType.toUpperCase()} - No data extracted for next stage`)
        }
      } else {
        console.error(`${testType.toUpperCase()} - Test failed:`, result.error)
      }

    } catch (error) {
      console.error(`\n=== ${testType.toUpperCase()} Test Failed ===`)
      console.error('Error message:', error.message)
      console.error('Full error:', error)
      console.error('Current stage data:', stageData)
      
      setTestResults(prev => ({
        ...prev,
        [testType]: {
          success: false,
          error: error.message,
          timestamp: Date.now(),
          debug_info: {
            stage_data_available: Object.keys(stageData),
            selected_model: selectedModel,
            selected_files: selectedFiles.map(f => ({ name: f.name, size: f.size }))
          }
        }
      }))
    } finally {
      setIsLoading(false)
      setActiveTest(null)
      console.log(`=== ${testType.toUpperCase()} Test Finished ===\n`)
    }
  }

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    setSelectedFiles(files)
    // Clear results when new files are selected
    setTestResults({})
    setStageData({})
  }

  const clearTestResults = () => {
    setTestResults({})
    setStageData({})
    setExpandedResults({})
  }

  const downloadResults = () => {
    const dataStr = JSON.stringify({
      testResults,
      stageData,
      systemHealth,
      timestamp: new Date().toISOString()
    }, null, 2)

    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `testing-results-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const toggleResultExpansion = (testType) => {
    setExpandedResults(prev => ({
      ...prev,
      [testType]: !prev[testType]
    }))
  }

  const formatJsonWithHighlighting = (obj) => {
    const jsonString = JSON.stringify(obj, null, 2)
    return jsonString
      .replace(/"([^"]+)":/g, '<span class="json-key">"$1":</span>')
      .replace(/: "([^"]+)"/g, ': <span class="json-string">"$1"</span>')
      .replace(/: (\d+)/g, ': <span class="json-number">$1</span>')
      .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'var(--success)'
      case 'failed': return 'var(--error)'
      case 'ready': return 'var(--primary)'
      case 'waiting': return 'var(--text-muted)'
      default: return 'var(--text-secondary)'
    }
  }

  const formatProcessingTime = (time) => {
    if (time < 1) return `${Math.round(time * 1000)}ms`
    return `${time.toFixed(2)}s`
  }

  return (
    <>
      <div className="testing-dashboard">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="dashboard-header"
        >
          <div className="header-title">
            <TestTube size={24} />
            <h2>Enhanced Testing Dashboard</h2>
          </div>
          <div className="header-actions">
            {onExitTesting && (
              <button onClick={onExitTesting} className="action-btn primary">
                <ArrowLeft size={16} />
                Exit Testing
              </button>
            )}
            <button onClick={fetchSystemHealth} className="action-btn secondary">
              <RefreshCw size={16} />
              Refresh Health
            </button>
            <button onClick={downloadResults} className="action-btn secondary">
              <Download size={16} />
              Download Results
            </button>
            <button onClick={clearTestResults} className="action-btn secondary">
              <RefreshCw size={16} />
              Clear Results
            </button>
            <button onClick={() => setShowGuide(true)} className="action-btn secondary">
              <HelpCircle size={16} />
              Guide
            </button>
          </div>
        </motion.div>

        {/* System Health */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="health-overview"
        >
          <div className="health-header">
            <h3>System Health</h3>
            <div className={`health-status ${systemHealth?.status || 'unknown'}`}>
              <Server size={16} />
              {systemHealth?.status || 'Unknown'}
            </div>
          </div>

          {systemHealth && (
            <div className="services-grid">
              {Object.entries(systemHealth.services || {}).map(([service, data]) => (
                <div key={service} className="service-card">
                  <div className="service-header">
                    <span className="service-name">{service}</span>
                    <div className={`service-status ${data.status}`}>
                      {data.status === 'healthy' ? <CheckCircle size={16} /> : <XCircle size={16} />}
                      {data.status}
                    </div>
                  </div>
                  {data.response_time && (
                    <div className="service-metric">
                      <Clock size={14} />
                      {formatProcessingTime(data.response_time)}
                    </div>
                  )}
                  {data.error && (
                    <div className="service-error">{data.error}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Test Configuration */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="test-configuration"
        >
          <div className="config-header">
            <Database size={20} />
            <h3>Test Configuration</h3>
          </div>

          <div className="config-grid">
            <div className="config-section">
              <label>AI Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="config-select"
              >
                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended)</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
              </select>
            </div>

            <div className="config-section">
              <label>Test Files</label>
              <input
                type="file"
                multiple
                accept=".pdf,.csv"
                onChange={handleFileSelect}
                className="config-file"
              />
              {selectedFiles.length > 0 && (
                <div className="selected-files-info">
                  {selectedFiles.length} file(s) selected: {selectedFiles.map(f => f.name).join(', ')}
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Enhanced Test Modes with Stage Flow */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="test-modes"
        >
          <div className="modes-header">
            <Zap size={20} />
            <h3>3-Stage Testing Pipeline</h3>
          </div>

          <div className="pipeline-flow">
            {testModes.map((mode, index) => {
              const status = getStageStatus(mode.id)
              const canRun = canRunStage(mode.id)
              const Icon = mode.icon
              const isActive = activeTest === mode.id

              return (
                <div key={mode.id} className="pipeline-stage">
                  <motion.div
                    className={`test-mode-card ${status} ${isActive ? 'active' : ''}`}
                    whileHover={canRun ? { scale: 1.02 } : {}}
                    style={{ borderColor: getStatusColor(status) }}
                  >
                    <div className="mode-header">
                      <Icon size={24} style={{ color: mode.color }} />
                      <h4>{mode.name}</h4>
                      <div className={`stage-status ${status}`}>
                        {status === 'completed' && <CheckCircle size={16} />}
                        {status === 'failed' && <XCircle size={16} />}
                        {status === 'ready' && <Play size={16} />}
                        {status === 'waiting' && <Clock size={16} />}
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </div>
                    </div>

                    <p className="mode-description">{mode.description}</p>

                    {mode.dependsOn && (
                      <div className="dependency-info">
                        <ChevronRight size={14} />
                        Requires: {testModes.find(m => m.id === mode.dependsOn)?.name}
                      </div>
                    )}

                    <button
                      onClick={() => runTest(mode.id)}
                      disabled={!canRun || isLoading}
                      className={`test-btn ${canRun ? 'ready' : 'waiting'}`}
                      style={{ background: canRun ? mode.color : 'var(--text-muted)' }}
                    >
                      {isActive ? (
                        <>
                          <RefreshCw size={16} className="spinning" />
                          Testing...
                        </>
                      ) : (
                        <>
                          <Play size={16} />
                          {status === 'completed' ? 'Test Again' : 'Run Test'}
                        </>
                      )}
                    </button>
                  </motion.div>

                  {index < testModes.length - 1 && mode.id !== 'full' && (
                    <div className="pipeline-arrow">
                      <ChevronRight size={20} />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>

        {/* Enhanced Test Results */}
        <AnimatePresence>
          {Object.keys(testResults).length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="test-results"
            >
              <div className="results-header">
                <BarChart3 size={20} />
                <h3>Test Results</h3>
              </div>

              <div className="results-list">
                {Object.entries(testResults).map(([testType, result]) => {
                  const mode = testModes.find(m => m.id === testType)
                  const Icon = mode?.icon || Activity
                  const isExpanded = expandedResults[testType]

                  return (
                    <motion.div
                      key={testType}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="result-card enhanced"
                    >
                      <div className="result-header" onClick={() => toggleResultExpansion(testType)}>
                        <div className="result-title">
                          <Icon size={20} style={{ color: mode?.color }} />
                          <h4>{mode?.name || testType}</h4>
                        </div>
                        <div className="result-controls">
                          <div className={`result-status ${result.success ? 'success' : 'error'}`}>
                            {result.success ? <CheckCircle size={16} /> : <XCircle size={16} />}
                            {result.success ? 'Success' : 'Failed'}
                          </div>
                          <button className="expand-btn">
                            {isExpanded ? <EyeOff size={16} /> : <Eye size={16} />}
                          </button>
                        </div>
                      </div>

                      <div className="result-metrics">
                        {result.processing_time && (
                          <div className="metric">
                            <Clock size={14} />
                            {formatProcessingTime(result.processing_time)}
                          </div>
                        )}

                        {result.model_used && (
                          <div className="metric">
                            <Brain size={14} />
                            {result.model_used}
                          </div>
                        )}
                      </div>

                      {result.error && (
                        <div className="result-error-detail">
                          <AlertTriangle size={16} />
                          <div className="error-content">
                            <strong>Error:</strong> {result.error}
                            {result.debug_info && (
                              <details className="error-debug-info">
                                <summary>Debug Information</summary>
                                <div className="debug-details">
                                  <div><strong>Model Used:</strong> {result.debug_info.selected_model}</div>
                                  <div><strong>Stage Data Available:</strong> {result.debug_info.stage_data_available.join(', ') || 'None'}</div>
                                  {result.debug_info.selected_files && (
                                    <div><strong>Selected Files:</strong> {result.debug_info.selected_files.map(f => f.name).join(', ')}</div>
                                  )}
                                </div>
                              </details>
                            )}
                          </div>
                        </div>
                      )}

                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="result-details"
                          >
                            <div className="result-actions">
                              <button
                                onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                                className="action-btn secondary small"
                              >
                                <Copy size={14} />
                                Copy JSON
                              </button>
                            </div>

                            <div className="json-display">
                              <div
                                className="json-content enhanced"
                                dangerouslySetInnerHTML={{
                                  __html: formatJsonWithHighlighting(result)
                                }}
                              />
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <TestingGuide isOpen={showGuide} onClose={() => setShowGuide(false)} />
    </>
  )
}

export default TestingDashboard 