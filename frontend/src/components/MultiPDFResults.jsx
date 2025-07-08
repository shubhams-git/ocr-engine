import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Copy, 
  Download, 
  RefreshCw, 
  CheckCircle, 
  FileText, 
  BarChart3, 
  TrendingUp,
  Database,
  Lightbulb,
  ChevronDown,
  ChevronRight,
  Files,
  AlertTriangle,
  Target,
  TrendingDown,
  Shield,
  Info,
  HelpCircle
} from 'lucide-react'

const MultiPDFResults = ({ results, fileNames, selectedModel, onReset }) => {
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState({
    extracted: true,
    normalized: true,
    projections: true,
    explanation: true
  })
  const [showConfidenceTooltip, setShowConfidenceTooltip] = useState(false)

  const handleCopy = async () => {
    try {
      const dataToShare = {
        extracted_data: results.extracted_data,
        normalized_data: results.normalized_data,
        projections: results.projections,
        explanation: results.explanation
      }
      await navigator.clipboard.writeText(JSON.stringify(dataToShare, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy analysis:', err)
    }
  }

  const handleDownload = () => {
    const analysisData = {
      files_analyzed: fileNames,
      model_used: selectedModel,
      analysis_timestamp: new Date().toISOString(),
      results: {
        extracted_data: results.extracted_data,
        normalized_data: results.normalized_data,
        projections: results.projections,
        explanation: results.explanation
      }
    }
    
    const element = document.createElement('a')
    const file = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' })
    element.href = URL.createObjectURL(file)
    element.download = `multi-pdf-analysis-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const formatJsonWithSyntaxHighlighting = (obj) => {
    const jsonString = JSON.stringify(obj, null, 2)
    
    // Simple syntax highlighting with regex
    return jsonString
      .replace(/("([^"\\]|\\.)*")\s*:/g, '<span class="json-key">$1</span>:')
      .replace(/:\s*("([^"\\]|\\.)*")/g, ': <span class="json-string">$1</span>')
      .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
      .replace(/:\s*(true|false|null)/g, ': <span class="json-boolean">$1</span>')
  }

  const getConfidenceExplanation = (level) => {
    const explanations = {
      high: 'High Confidence (>80%): Strong data foundation with reliable trends',
      medium: 'Medium Confidence (60-80%): Good data but some uncertainty factors',
      low: 'Low Confidence (<60%): Limited data or high uncertainty in projections'
    }
    return explanations[level] || 'Confidence level indicates reliability of the projection'
  }

  const renderFormattedExplanation = (explanation) => {
    if (!explanation) return <p>No explanation provided</p>

    // Split explanation into sections based on common patterns
    const sections = explanation.split(/\n\s*\n/).filter(section => section.trim())
    
    return (
      <div className="formatted-explanation">
        {sections.map((section, index) => {
          const trimmedSection = section.trim()
          
          // Check if it's a heading (starts with **text** or #)
          if (trimmedSection.match(/^\*\*.*\*\*/) || trimmedSection.startsWith('#')) {
            const headingText = trimmedSection.replace(/^\*\*(.*)\*\*/, '$1').replace(/^#+\s*/, '')
            return (
              <motion.h4
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="explanation-heading"
              >
                {headingText}
              </motion.h4>
            )
          }
          
          // Check if it's a proper bullet point list (bullets at start of lines)
          const lines = trimmedSection.split('\n').map(line => line.trim()).filter(line => line.length > 0)
          const isBulletList = lines.length > 1 && lines.every(line => 
            line.match(/^[•\-\*]\s+/) || line.match(/^\d+\.\s+/)
          )
          
          if (isBulletList) {
            const items = lines.map(line => 
              line.replace(/^[•\-\*]\s+/, '').replace(/^\d+\.\s+/, '').trim()
            ).filter(item => item.length > 0)
            
            return (
              <motion.ul
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="explanation-list"
              >
                {items.map((item, itemIndex) => (
                  <li key={itemIndex}>{item}</li>
                ))}
              </motion.ul>
            )
          }
          
          // Regular paragraph
          return (
            <motion.p
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="explanation-paragraph"
            >
              {trimmedSection}
            </motion.p>
          )
        })}
      </div>
    )
  }

  const renderEnhancedProjections = (projections) => {
    if (!projections || typeof projections !== 'object') {
      return <div className="empty-section"><p>No projections data available</p></div>
    }

    return (
      <div className="enhanced-projections">
        {/* Methodology Section */}
        {projections.methodology && (
          <div className="projection-subsection">
            <h5 className="subsection-title">
              <Target size={16} />
              Methodology
            </h5>
            <p className="methodology-text">{projections.methodology}</p>
          </div>
        )}

        {/* Yearly Projections */}
        {projections.yearly_projections && (
          <div className="projection-subsection">
            <div className="subsection-header">
              <h5 className="subsection-title">
                <TrendingUp size={16} />
                Yearly Projections
              </h5>
              <div className="confidence-legend">
                <div 
                  className="confidence-info"
                  onMouseEnter={() => setShowConfidenceTooltip(true)}
                  onMouseLeave={() => setShowConfidenceTooltip(false)}
                >
                  <HelpCircle size={16} />
                  <span>Confidence Levels</span>
                  {showConfidenceTooltip && (
                    <div className="confidence-tooltip">
                      <div className="tooltip-item">
                        <span className="confidence-badge high">High</span>
                        <span>&gt;80% - Strong data foundation</span>
                      </div>
                      <div className="tooltip-item">
                        <span className="confidence-badge medium">Medium</span>
                        <span>60-80% - Good data, some uncertainty</span>
                      </div>
                      <div className="tooltip-item">
                        <span className="confidence-badge low">Low</span>
                        <span>&lt;60% - Limited data or high uncertainty</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="yearly-projections-grid">
              {Object.entries(projections.yearly_projections).map(([year, data]) => (
                <div key={year} className="year-projection-card">
                  <h6 className="year-title">{year}</h6>
                  {data.revenue && (
                    <div className="projection-metric">
                      <span className="metric-label">Revenue:</span>
                      <div className="metric-value-container">
                        <span className="metric-value">
                          ${typeof data.revenue.value === 'number' ? data.revenue.value.toLocaleString() : data.revenue.value}
                        </span>
                        {data.revenue.confidence && (
                          <span 
                            className={`confidence-badge ${data.revenue.confidence}`}
                            title={getConfidenceExplanation(data.revenue.confidence)}
                          >
                            {data.revenue.confidence} confidence
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  {data.net_profit && (
                    <div className="projection-metric">
                      <span className="metric-label">Net Profit:</span>
                      <div className="metric-value-container">
                        <span className="metric-value">
                          ${typeof data.net_profit.value === 'number' ? data.net_profit.value.toLocaleString() : data.net_profit.value}
                        </span>
                        {data.net_profit.confidence && (
                          <span 
                            className={`confidence-badge ${data.net_profit.confidence}`}
                            title={getConfidenceExplanation(data.net_profit.confidence)}
                          >
                            {data.net_profit.confidence} confidence
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Assumptions */}
        {projections.assumptions && projections.assumptions.length > 0 && (
          <div className="projection-subsection">
            <h5 className="subsection-title">
              <Lightbulb size={16} />
              Key Assumptions
            </h5>
            <ul className="assumptions-list">
              {projections.assumptions.map((assumption, index) => (
                <li key={index} className="assumption-item">
                  <div className="assumption-content">{assumption}</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risk Factors */}
        {results.risk_factors && results.risk_factors.length > 0 && (
          <div className="projection-subsection">
            <h5 className="subsection-title">
              <AlertTriangle size={16} />
              Risk Factors
            </h5>
            <div className="risk-factors-grid">
              {results.risk_factors.map((risk, index) => (
                <div key={index} className="risk-factor-card">
                  <div className="risk-header">
                    <AlertTriangle size={18} className="risk-icon" />
                    <span className="risk-severity">Risk #{index + 1}</span>
                  </div>
                  <div className="risk-content">{risk}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scenarios */}
        {projections.scenarios && (
          <div className="projection-subsection">
            <h5 className="subsection-title">
              <Shield size={16} />
              Scenarios
            </h5>
            <div className="scenarios-grid">
              {Object.entries(projections.scenarios).map(([scenarioName, scenario]) => (
                <div key={scenarioName} className="scenario-card">
                  <h6 className="scenario-title">{scenarioName.charAt(0).toUpperCase() + scenarioName.slice(1)}</h6>
                  {scenario.description && (
                    <p className="scenario-description">{scenario.description}</p>
                  )}
                  {scenario.revenue_multiplier && (
                    <div className="scenario-metric">
                      <span className="metric-label">Revenue Impact:</span>
                      <span className={`multiplier-value ${scenario.revenue_multiplier > 1 ? 'positive' : 'negative'}`}>
                        {((scenario.revenue_multiplier - 1) * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Raw JSON for detailed view */}
        <details className="raw-json-details">
          <summary className="raw-json-summary">View Raw JSON Data</summary>
          <pre 
            className="json-content enhanced"
            dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(projections) }}
          />
        </details>
      </div>
    )
  }

  const renderJsonSection = (data, title, icon, sectionKey) => {
    const isExpanded = expandedSections[sectionKey]
    const isEmpty = !data || (Array.isArray(data) && data.length === 0) || (typeof data === 'object' && Object.keys(data).length === 0)
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection(sectionKey)}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            {icon}
            <h3>{title}</h3>
            {!isEmpty && <span className="section-count">({Array.isArray(data) ? data.length : Object.keys(data).length} items)</span>}
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight size={20} />
          </motion.div>
        </motion.div>
        
        <motion.div
          initial={false}
          animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
          transition={{ duration: 0.3 }}
          className="section-content"
        >
          {isEmpty ? (
            <div className="empty-section">
              <p>No data available for this section</p>
            </div>
          ) : sectionKey === 'projections' ? (
            <div className="json-container">
              {renderEnhancedProjections(data)}
            </div>
          ) : (
            <div className="json-container">
              <pre 
                className="json-content enhanced"
                dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(data) }}
              />
            </div>
          )}
        </motion.div>
      </motion.div>
    )
  }

  const renderExplanationSection = () => {
    const isExpanded = expandedSections.explanation
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section explanation-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('explanation')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Lightbulb size={20} className="section-icon" />
            <h3>Analysis Methodology & Summary</h3>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight size={20} />
          </motion.div>
        </motion.div>
        
        <motion.div
          initial={false}
          animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
          transition={{ duration: 0.3 }}
          className="section-content"
        >
          <div className="explanation-content enhanced">
            {renderFormattedExplanation(results.explanation)}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  const getModelDisplayName = (modelId) => {
    const modelNames = {
      'gemini-2.5-pro': 'Gemini 2.5 Pro',
      'gemini-2.5-flash': 'Gemini 2.5 Flash',
      'gemini-2.0-flash': 'Gemini 2.0 Flash',
      'gemini-1.5-flash': 'Gemini 1.5 Flash',
      'gemini-1.5-pro': 'Gemini 1.5 Pro'
    }
    return modelNames[modelId] || modelId
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="results-container multi-pdf-results"
    >
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="results-header"
      >
        <div className="success-badge">
          <CheckCircle className="success-icon" />
          <span>Multi-PDF Analysis Complete!</span>
        </div>
        
        <div className="analysis-overview">
          <div className="overview-item">
            <Files size={20} className="overview-icon" />
            <div className="overview-details">
              <h4>Documents Analyzed</h4>
              <span>{fileNames?.length || 0} PDF files</span>
            </div>
          </div>
          
          <div className="overview-item">
            <BarChart3 size={20} className="overview-icon" />
            <div className="overview-details">
              <h4>AI Model</h4>
              <span>{getModelDisplayName(selectedModel)}</span>
            </div>
          </div>
          
          <div className="overview-item">
            <Database size={20} className="overview-icon" />
            <div className="overview-details">
              <h4>Data Quality</h4>
              <span>{results.data_quality_score ? `${(results.data_quality_score * 100).toFixed(1)}%` : 'Analyzed'}</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="results-actions"
      >
        <motion.button
          onClick={handleCopy}
          className={`action-button copy-button ${copied ? 'copied' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={copied}
        >
          {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
          {copied ? 'Copied!' : 'Copy Analysis'}
        </motion.button>
        
        <motion.button
          onClick={handleDownload}
          className="action-button download-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Download size={18} />
          Download JSON
        </motion.button>
        
        <motion.button
          onClick={onReset}
          className="action-button reset-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <RefreshCw size={18} />
          New Analysis
        </motion.button>
      </motion.div>

      {/* Results Sections */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="analysis-results"
      >
        {/* Explanation */}
        {renderExplanationSection()}

        {/* Projections */}
        {renderJsonSection(
          results.projections,
          'Projections & Insights',
          <TrendingUp size={20} className="section-icon" />,
          'projections'
        )}

        {/* Normalized Data */}
        {renderJsonSection(
          results.normalized_data,
          'Normalized Data',
          <Database size={20} className="section-icon" />,
          'normalized'
        )}

        {/* Extracted Data */}
        {renderJsonSection(
          results.extracted_data,
          'Extracted Data',
          <FileText size={20} className="section-icon" />,
          'extracted'
        )}
      </motion.div>

      {/* File List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="processed-files-section"
      >
        <h4>Processed Files</h4>
        <div className="processed-files">
          {fileNames?.map((fileName, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + index * 0.1 }}
              className="processed-file"
            >
              <FileText size={16} />
              <span>{fileName}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default MultiPDFResults 