import { useState, useRef } from 'react'
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
  HelpCircle,
  Clock,
  Calendar,
  TrendingUpIcon,
  Activity,
  Award,
  Search,
  Zap,
  DollarSign,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  Gauge,
  AlertOctagon,
  CheckSquare,
  XSquare,
  MinusSquare,
  Building,
  GitBranch,
  Filter
} from 'lucide-react'
import FinancialChart from './FinancialChart'
import ExportUtils from './ExportUtils'
import SearchFilter from './SearchFilter'
import { ErrorDisplay } from './ErrorBoundary'

const MultiPDFResults = ({ results, fileNames, selectedModel, onReset }) => {
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    analysis_summary: true,
    methodology: true,
    data_quality: true,
    extracted: true,
    normalized: true,
    projections: true,
    accuracy: true,
    qa_checks: false,
    explanation: true,
    architecture_overview: false // Added for new section
  })
  const [showConfidenceTooltip, setShowConfidenceTooltip] = useState(false)
  const [filteredData, setFilteredData] = useState(results)
  const [searchTerm, setSearchTerm] = useState('')
  const [showCharts, setShowCharts] = useState(false)
  const [error, setError] = useState(null)
  
  // Refs for export functionality
  const contentRef = useRef(null)
  const chartRefs = useRef([])

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(results, null, 2))
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
      results: results
    }
    
    const element = document.createElement('a')
    const file = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' })
    element.href = URL.createObjectURL(file)
    element.download = `multi-pdf-analysis-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // Enhanced filter and search handlers
  const handleFilter = (filters) => {
    let filtered = results
    
    // Apply filters based on confidence level
    if (filters.confidenceLevel !== 'all') {
      filtered = { ...filtered }
      if (filtered.projections?.base_case_projections) {
        Object.keys(filtered.projections.base_case_projections).forEach(period => {
          const periodData = filtered.projections.base_case_projections[period]
          Object.keys(periodData).forEach(metric => {
            if (Array.isArray(periodData[metric])) {
              periodData[metric] = periodData[metric].filter(item => 
                item.confidence === filters.confidenceLevel
              )
            }
          })
        })
      }
    }
    
    setFilteredData(filtered)
  }

  const handleSearch = (term) => {
    setSearchTerm(term)
    
    if (!term) {
      setFilteredData(results)
      return
    }
    
    // Search through explanations, summaries, and other text content
    const searchResults = { ...results }
    
    // Filter projections based on search term
    if (searchResults.projections?.base_case_projections) {
      Object.keys(searchResults.projections.base_case_projections).forEach(period => {
        if (period.toLowerCase().includes(term.toLowerCase())) {
          // Keep this period
          return
        }
        // Filter metrics within the period
        const periodData = searchResults.projections.base_case_projections[period]
        Object.keys(periodData).forEach(metric => {
          if (!metric.toLowerCase().includes(term.toLowerCase())) {
            delete periodData[metric]
          }
        })
      })
    }
    
    setFilteredData(searchResults)
  }

  const handleSort = (field, order) => {
    const sorted = { ...filteredData }
    
    // Sort projections by date or value
    if (sorted.projections?.base_case_projections) {
      Object.keys(sorted.projections.base_case_projections).forEach(period => {
        const periodData = sorted.projections.base_case_projections[period]
        Object.keys(periodData).forEach(metric => {
          if (Array.isArray(periodData[metric])) {
            periodData[metric].sort((a, b) => {
              if (field === 'date') {
                return order === 'asc' ? 
                  new Date(a.period) - new Date(b.period) :
                  new Date(b.period) - new Date(a.period)
              } else if (field === 'value') {
                return order === 'asc' ? a.value - b.value : b.value - a.value
              }
              return 0
            })
          }
        })
      })
    }
    
    setFilteredData(sorted)
  }

  // Generate chart data for multi-PDF analysis
  const generateChartData = (data) => {
    const chartData = []
    
    // Revenue trend chart
    if (data.projections?.base_case_projections) {
      const periods = Object.keys(data.projections.base_case_projections)
      const revenueData = {
        labels: periods,
        datasets: [{
          label: 'Revenue Projections',
          data: periods.map(period => {
            const periodData = data.projections.base_case_projections[period]
            if (Array.isArray(periodData.revenue) && periodData.revenue.length > 0) {
              return periodData.revenue[0].value
            }
            return periodData.revenue?.value || 0
          })
        }]
      }
      chartData.push({
        type: 'line',
        title: 'Revenue Projections Trend',
        data: revenueData
      })
    }
    
    // Confidence distribution chart
    if (data.projections?.base_case_projections) {
      const confidenceLevels = { high: 0, medium: 0, low: 0, very_low: 0 }
      
      Object.values(data.projections.base_case_projections).forEach(period => {
        Object.values(period).forEach(metric => {
          if (Array.isArray(metric)) {
            metric.forEach(item => {
              if (item.confidence) {
                confidenceLevels[item.confidence] = (confidenceLevels[item.confidence] || 0) + 1
              }
            })
          }
        })
      })
      
      const confidenceData = {
        labels: Object.keys(confidenceLevels),
        datasets: [{
          label: 'Confidence Distribution',
          data: Object.values(confidenceLevels)
        }]
      }
      
      chartData.push({
        type: 'doughnut',
        title: 'Projection Confidence Distribution',
        data: confidenceData
      })
    }
    
    return chartData
  }

  const chartData = generateChartData(filteredData)

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const formatJsonWithSyntaxHighlighting = (obj) => {
    const jsonString = JSON.stringify(obj, null, 2)
    
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
      low: 'Low Confidence (<60%): Limited data or high uncertainty in projections',
      very_low: 'Very Low Confidence (<40%): Highly uncertain, long-term extrapolation'
    }
    return explanations[level] || 'Confidence level indicates reliability of the projection'
  }

  const formatCurrency = (value) => {
    if (typeof value === 'number') {
      return new Intl.NumberFormat('en-AU', { 
        style: 'currency', 
        currency: 'AUD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    }
    return value
  }

  const formatPercentage = (value) => {
    if (typeof value === 'number') {
      return `${(value * 100).toFixed(2)}%`
    }
    return value
  }

  // Render Summary Section
  const renderSummarySection = () => {
    if (!results.summary) return null

    const isExpanded = expandedSections.summary

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('summary')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Lightbulb size={20} className="section-icon" />
            <h3>Executive Summary</h3>
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
            <p className="explanation-paragraph">{results.summary}</p>
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Render Methodology Section
  const renderMethodologySection = () => {
    if (!results.methodology) return null

    // Handle both string and object formats for backward compatibility
    const methodology = typeof results.methodology === 'string' 
      ? { description: results.methodology }
      : results.methodology

    // Extract data quality score from methodology or root level
    const dataQualityScore = methodology.data_quality_score || results.data_quality_score
    
    // Extract assumptions from methodology or root level
    const assumptions = methodology.key_assumptions || results.assumptions
    
    const isExpanded = expandedSections.methodology

    // Detect model type from description if it's a string
    const detectModelFromDescription = (description) => {
      if (typeof description !== 'string') return null
      const desc = description.toLowerCase()
      if (desc.includes('sarima') || desc.includes('seasonal autoregressive')) return 'SARIMA'
      if (desc.includes('arima')) return 'ARIMA'
      if (desc.includes('prophet')) return 'Prophet'
      if (desc.includes('linear regression')) return 'Linear Regression'
      if (desc.includes('exponential smoothing')) return 'Exponential Smoothing'
      return 'Time Series Model'
    }

    const modelChosen = methodology.model_chosen || detectModelFromDescription(methodology.description)

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('methodology')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Zap size={20} className="section-icon" />
            <h3>Methodology & Model Transparency</h3>
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
          <div className="methodology-content">
            {/* Model Description (when methodology is a string) */}
            {methodology.description && (
              <div className="methodology-subsection">
                <h5>Methodology Description</h5>
                <div className="model-info-card">
                  <div className="model-justification">
                    {methodology.description}
                  </div>
                </div>
              </div>
            )}

            {/* Model Selection */}
            {modelChosen && (
              <div className="methodology-subsection">
                <h5>Model Selection</h5>
                <div className="model-info-card">
                  <div className="model-chosen">
                    <strong>Selected Model:</strong> <span className="model-name">{modelChosen}</span>
                  </div>
                  {methodology.model_justification && (
                    <div className="model-justification">
                      <strong>Justification:</strong> {methodology.model_justification}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Data Quality Score */}
            {dataQualityScore !== undefined && (
              <div className="methodology-subsection">
                <h5>Data Quality Assessment</h5>
                <div className="quality-score-card">
                  <div className="score-value">{(dataQualityScore * 100).toFixed(1)}%</div>
                  <div className="score-label">Overall Data Quality Score</div>
                </div>
              </div>
            )}

            {/* Preprocessing Steps */}
            {methodology.preprocessing_steps && methodology.preprocessing_steps.length > 0 && (
              <div className="methodology-subsection">
                <h5>Data Preprocessing Steps</h5>
                <ul className="preprocessing-list">
                  {methodology.preprocessing_steps.map((step, index) => (
                    <li key={index} className="preprocessing-item">
                      <CheckCircle size={16} className="step-icon" />
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Feature Engineering */}
            {methodology.feature_engineering && methodology.feature_engineering.length > 0 && (
              <div className="methodology-subsection">
                <h5>Feature Engineering</h5>
                <ul className="feature-engineering-list">
                  {methodology.feature_engineering.map((feature, index) => (
                    <li key={index} className="feature-item">
                      <Award size={16} className="feature-icon" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Train/Test Split */}
            {methodology.train_test_split && (
              <div className="methodology-subsection">
                <h5>Model Validation</h5>
                <div className="validation-info">
                  <div className="split-info">
                    <strong>Train/Test Split:</strong> {methodology.train_test_split}
                  </div>
                  {methodology.confidence_intervals && (
                    <div className="confidence-info">
                      <strong>Confidence Intervals:</strong> {methodology.confidence_intervals}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Validation Metrics */}
            {methodology.validation_metrics && (
              <div className="methodology-subsection">
                <h5>Model Performance Metrics</h5>
                <div className="validation-metrics-grid">
                  {Object.entries(methodology.validation_metrics).map(([metric, value]) => (
                    <div key={metric} className="metric-card">
                      <div className="metric-label">{metric.toUpperCase()}</div>
                      <div className="metric-value">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sensitivity Analysis */}
            {methodology.sensitivity_analysis && (
              <div className="methodology-subsection">
                <h5>Sensitivity Analysis</h5>
                <div className="sensitivity-info">
                  <AlertTriangle size={16} className="sensitivity-icon" />
                  <p>{methodology.sensitivity_analysis}</p>
                </div>
              </div>
            )}

            {/* Key Assumptions */}
            {assumptions && assumptions.length > 0 && (
              <div className="methodology-subsection">
                <h5>Key Assumptions</h5>
                <ul className="assumptions-list">
                  {assumptions.map((assumption, index) => (
                    <li key={index} className="assumption-item">
                      <div className="assumption-content">{assumption}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Risk Factors (if available at root level) */}
            {results.risk_factors && results.risk_factors.length > 0 && (
              <div className="methodology-subsection">
                <h5>Risk Factors</h5>
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
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Business Context Analysis - Stage 2 insights
  const renderBusinessContextAnalysis = () => {
    if (!results.normalized_data || !results.normalized_data.business_context) return null

    const businessContext = results.normalized_data.business_context
    const contextualAnalysis = results.normalized_data.contextual_analysis
    const patternAnalysis = results.normalized_data.pattern_analysis
    const isExpanded = expandedSections.business_context

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('business_context')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Building size={20} className="section-icon" />
            <h3>Business Context Analysis</h3>
            <span className="section-count">Stage 2 Intelligence</span>
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
          <div className="business-context-content">
            {/* Industry & Business Stage */}
            <div className="context-subsection">
              <h5>Business Classification</h5>
              <div className="context-grid">
                <div className="context-item">
                  <span className="context-label">Industry:</span>
                  <span className="context-value">{businessContext.industry_classification || 'Not specified'}</span>
                </div>
                <div className="context-item">
                  <span className="context-label">Business Stage:</span>
                  <span className={`context-value stage-${businessContext.business_stage}`}>{businessContext.business_stage || 'Unknown'}</span>
                </div>
                <div className="context-item">
                  <span className="context-label">Market Geography:</span>
                  <span className="context-value">{businessContext.market_geography || 'Not specified'}</span>
                </div>
                <div className="context-item">
                  <span className="context-label">Competitive Position:</span>
                  <span className={`context-value position-${businessContext.competitive_position}`}>{businessContext.competitive_position || 'Unknown'}</span>
                </div>
                {businessContext.business_model_type && (
                  <div className="context-item">
                    <span className="context-label">Business Model:</span>
                    <span className="context-value">{businessContext.business_model_type}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Seasonality Patterns */}
            {contextualAnalysis && contextualAnalysis.seasonality_patterns && (
              <div className="context-subsection">
                <h5>Seasonality Analysis</h5>
                <div className="seasonality-analysis">
                  <div className="seasonality-overview">
                    <span className={`seasonality-status ${contextualAnalysis.seasonality_patterns.seasonal_detected ? 'detected' : 'not-detected'}`}>
                      {contextualAnalysis.seasonality_patterns.seasonal_detected ? '✅ Seasonal patterns detected' : '❌ No clear seasonal patterns'}
                    </span>
                  </div>
                  {contextualAnalysis.seasonality_patterns.seasonal_detected && (
                    <>
                      {contextualAnalysis.seasonality_patterns.peak_periods && (
                        <div className="seasonal-periods">
                          <strong>Peak Periods:</strong> {contextualAnalysis.seasonality_patterns.peak_periods.join(', ')}
                        </div>
                      )}
                      {contextualAnalysis.seasonality_patterns.trough_periods && (
                        <div className="seasonal-periods">
                          <strong>Low Periods:</strong> {contextualAnalysis.seasonality_patterns.trough_periods.join(', ')}
                        </div>
                      )}
                      {contextualAnalysis.seasonality_patterns.seasonal_amplitude && (
                        <div className="seasonal-periods">
                          <strong>Seasonal Amplitude:</strong> {formatPercentage(contextualAnalysis.seasonality_patterns.seasonal_amplitude)}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Financial Health & Growth Patterns */}
            {patternAnalysis && (
              <div className="context-subsection">
                <h5>Financial Pattern Analysis</h5>
                <div className="pattern-grid">
                  {patternAnalysis.growth_rates && (
                    <div className="pattern-card">
                      <h6>Growth Trends</h6>
                      {patternAnalysis.growth_rates.revenue_cagr && (
                        <div className="pattern-metric">
                          <span>Revenue CAGR:</span>
                          <span className="metric-value">{formatPercentage(patternAnalysis.growth_rates.revenue_cagr)}</span>
                        </div>
                      )}
                      {patternAnalysis.growth_rates.profit_cagr && (
                        <div className="pattern-metric">
                          <span>Profit CAGR:</span>
                          <span className="metric-value">{formatPercentage(patternAnalysis.growth_rates.profit_cagr)}</span>
                        </div>
                      )}
                      {patternAnalysis.growth_rates.recent_growth_trend && (
                        <div className="pattern-metric">
                          <span>Recent Trend:</span>
                          <span className={`trend-indicator ${patternAnalysis.growth_rates.recent_growth_trend}`}>
                            {patternAnalysis.growth_rates.recent_growth_trend}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {patternAnalysis.volatility_assessment && (
                    <div className="pattern-card">
                      <h6>Volatility Assessment</h6>
                      <div className="pattern-metric">
                        <span>Revenue Volatility:</span>
                        <span className={`volatility-level ${patternAnalysis.volatility_assessment.revenue_volatility}`}>
                          {patternAnalysis.volatility_assessment.revenue_volatility}
                        </span>
                      </div>
                      <div className="pattern-metric">
                        <span>Profit Volatility:</span>
                        <span className={`volatility-level ${patternAnalysis.volatility_assessment.profit_volatility}`}>
                          {patternAnalysis.volatility_assessment.profit_volatility}
                        </span>
                      </div>
                      <div className="pattern-metric">
                        <span>Overall Stability:</span>
                        <span className={`stability-level ${patternAnalysis.volatility_assessment.overall_stability}`}>
                          {patternAnalysis.volatility_assessment.overall_stability}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Methodology Evaluation - Stage 2 method selection
  const renderMethodologyEvaluation = () => {
    if (!results.normalized_data || !results.normalized_data.methodology_evaluation) return null

    const methodology = results.normalized_data.methodology_evaluation
    const isExpanded = expandedSections.methodology_evaluation

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('methodology_evaluation')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Target size={20} className="section-icon" />
            <h3>Forecasting Methodology</h3>
            <span className="section-count">AI-Selected Method</span>
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
          <div className="methodology-content">
            {/* Selected Method */}
            {methodology.selected_method && (
              <div className="methodology-subsection">
                <h5>Selected Forecasting Method</h5>
                <div className="method-selection">
                  <div className="selected-method-card">
                    <div className="method-header">
                      <span className="method-badge">{methodology.selected_method.primary_method}</span>
                      <span className={`confidence-badge ${methodology.selected_method.confidence_level}`}>
                        {methodology.selected_method.confidence_level} confidence
                      </span>
                    </div>
                    <div className="method-rationale">
                      <strong>Rationale:</strong> {methodology.selected_method.rationale}
                    </div>
                    {methodology.selected_method.fallback_method && (
                      <div className="fallback-method">
                        <strong>Fallback Method:</strong> {methodology.selected_method.fallback_method}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Methods Tested */}
            {methodology.methods_tested && methodology.methods_tested.length > 0 && (
              <div className="methodology-subsection">
                <h5>Methods Evaluation</h5>
                <div className="methods-comparison">
                  {methodology.methods_tested.map((method, index) => (
                    <div key={index} className="method-card">
                      <div className="method-name">
                        <span className="method-label">{method.method}</span>
                        <span className="suitability-score">
                          Score: {method.suitability_score ? (method.suitability_score * 100).toFixed(1) : 'N/A'}%
                        </span>
                      </div>
                      {method.evaluation_metrics && (
                        <div className="evaluation-metrics">
                          {method.evaluation_metrics.mape && (
                            <span className="metric">MAPE: {method.evaluation_metrics.mape.toFixed(2)}%</span>
                          )}
                          {method.evaluation_metrics.r_squared && (
                            <span className="metric">R²: {method.evaluation_metrics.r_squared.toFixed(3)}</span>
                          )}
                        </div>
                      )}
                      {method.strengths && method.strengths.length > 0 && (
                        <div className="method-strengths">
                          <strong>Strengths:</strong> {method.strengths.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Scenario Analysis - Optimistic and Conservative scenarios
  const renderScenarioAnalysis = () => {
    if (!results.projections || !results.projections.scenario_projections) return null

    const scenarios = results.projections.scenario_projections
    const isExpanded = expandedSections.scenario_analysis

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('scenario_analysis')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <GitBranch size={20} className="section-icon" />
            <h3>Scenario Planning</h3>
            <span className="section-count">{Object.keys(scenarios).length} scenarios</span>
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
          <div className="scenario-analysis-content">
            <div className="scenarios-grid">
              {Object.entries(scenarios).map(([scenarioName, scenarioData]) => (
                <div key={scenarioName} className="scenario-card">
                  <div className="scenario-header">
                    <h5 className={`scenario-title ${scenarioName}`}>
                      {scenarioName.charAt(0).toUpperCase() + scenarioName.slice(1)} Scenario
                    </h5>
                    {scenarioData.probability_assessment && (
                      <span className="probability-badge">
                        {scenarioData.probability_assessment}
                      </span>
                    )}
                  </div>
                  
                  {scenarioData.description && (
                    <div className="scenario-description">
                      {scenarioData.description}
                    </div>
                  )}

                  {scenarioData.key_drivers && scenarioData.key_drivers.length > 0 && (
                    <div className="scenario-drivers">
                      <strong>Key Drivers:</strong>
                      <ul>
                        {scenarioData.key_drivers.map((driver, index) => (
                          <li key={index}>{driver}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {scenarioData.growth_multipliers && (
                    <div className="growth-multipliers">
                      <strong>Growth Multipliers:</strong>
                      <div className="multipliers-grid">
                        {Object.entries(scenarioData.growth_multipliers).map(([period, multiplier]) => (
                          <div key={period} className="multiplier-item">
                            <span className="period-label">{period.replace(/_/g, ' ')}</span>
                            <span className={`multiplier-value ${multiplier > 1 ? 'positive' : 'negative'}`}>
                              {multiplier}x
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Render Data Analysis Summary Section
  const renderDataAnalysisSummary = () => {
    if (!results.data_analysis_summary) return null

    const summary = results.data_analysis_summary
    const isExpanded = expandedSections.analysis_summary

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('analysis_summary')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Activity size={20} className="section-icon" />
            <h3>Data Analysis Summary</h3>
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
          <div className="period-detection-summary">
            <div className="period-detection-details">
              {summary.period_granularity_detected && (
                <div className="period-detail-item">
                  <Calendar size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Granularity:</span>
                    <span className={`period-value granularity-${summary.period_granularity_detected}`}>
                      {summary.period_granularity_detected.charAt(0).toUpperCase() + summary.period_granularity_detected.slice(1)}
                    </span>
                  </div>
                </div>
              )}
              
              {summary.total_data_points && (
                <div className="period-detail-item">
                  <BarChart3 size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Data Points:</span>
                    <span className="period-value">{summary.total_data_points}</span>
                  </div>
                </div>
              )}
              
              {summary.time_span && (
                <div className="period-detail-item">
                  <Clock size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Time Span:</span>
                    <span className="period-value">{summary.time_span}</span>
                  </div>
                </div>
              )}
              
              {summary.data_completeness && (
                <div className="period-detail-item">
                  <CheckCircle size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Completeness:</span>
                    <span className="period-value">{summary.data_completeness}</span>
                  </div>
                </div>
              )}

              {summary.optimal_forecast_horizon && (
                <div className="period-detail-item">
                  <Target size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Forecast Horizon:</span>
                    <span className="period-value">{summary.optimal_forecast_horizon}</span>
                  </div>
                </div>
              )}

              {summary.seasonality_detected !== undefined && (
                <div className="period-detail-item">
                  <TrendingUp size={16} />
                  <div className="period-detail-content">
                    <span className="period-label">Seasonality:</span>
                    <span className={`period-value seasonality-${summary.seasonality_detected}`}>
                      {summary.seasonality_detected ? '✅ Detected' : '❌ Not Found'}
                    </span>
                  </div>
                </div>
              )}
            </div>
            
            {summary.rationale && (
              <div className="period-rationale">
                <Info size={16} />
                <p>{summary.rationale}</p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Render Data Quality Assessment Section
  const renderDataQualityAssessment = () => {
    if (!results.data_quality_assessment) return null

    const quality = results.data_quality_assessment
    const isExpanded = expandedSections.data_quality

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('data_quality')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Award size={20} className="section-icon" />
            <h3>Data Quality Assessment</h3>
            {quality.completeness_score && (
              <span className="section-count">Score: {(quality.completeness_score * 100).toFixed(1)}%</span>
            )}
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
          <div className="data-quality-content">
            {/* Quality Metrics */}
            <div className="quality-metrics-grid">
              {quality.completeness_score !== undefined && (
                <div className="quality-metric">
                  <div className="metric-header">
                    <Gauge size={16} />
                    <span>Completeness Score</span>
                  </div>
                  <div className="metric-value">
                    {(quality.completeness_score * 100).toFixed(1)}%
                  </div>
                </div>
              )}

              {quality.period_coverage && (
                <div className="quality-metric">
                  <div className="metric-header">
                    <Calendar size={16} />
                    <span>Period Coverage</span>
                  </div>
                  <div className="metric-value">{quality.period_coverage}</div>
                </div>
              )}
            </div>

            {/* Outliers Detected */}
            {quality.outliers_detected && quality.outliers_detected.length > 0 && (
              <div className="quality-subsection">
                <h5>Outliers Detected</h5>
                <div className="outliers-grid">
                  {quality.outliers_detected.map((outlier, index) => (
                    <div key={index} className="outlier-card">
                      <div className="outlier-header">
                        <AlertTriangle size={16} />
                        <span className="outlier-item">{outlier.item}</span>
                      </div>
                      <div className="outlier-details">
                        <div><strong>Deviation:</strong> {outlier.deviation}</div>
                        <div><strong>Impact:</strong> {outlier.impact}</div>
                        {outlier.likely_cause && (
                          <div><strong>Likely Cause:</strong> {outlier.likely_cause}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Data Gaps */}
            {quality.data_gaps && quality.data_gaps.length > 0 && (
              <div className="quality-subsection">
                <h5>Data Gaps</h5>
                <div className="data-gaps">
                  {quality.data_gaps.map((gap, index) => (
                    <div key={index} className="data-gap-item">
                      <AlertOctagon size={16} />
                      <span>{gap}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Consistency Issues */}
            {quality.consistency_issues && quality.consistency_issues.length > 0 && (
              <div className="quality-subsection">
                <h5>Consistency Issues</h5>
                <div className="consistency-issues">
                  {quality.consistency_issues.map((issue, index) => (
                    <div key={index} className="consistency-issue-item">
                      <AlertTriangle size={16} />
                      <span>{issue}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Reliability Flags */}
            {quality.reliability_flags && quality.reliability_flags.length > 0 && (
              <div className="quality-subsection">
                <h5>Reliability Flags</h5>
                <div className="reliability-flags">
                  {quality.reliability_flags.map((flag, index) => (
                    <div key={index} className={`reliability-flag ${flag.status}`}>
                      <div className="flag-header">
                        {flag.status === 'passed' && <CheckSquare size={16} />}
                        {flag.status === 'warning' && <AlertTriangle size={16} />}
                        {flag.status === 'failed' && <XSquare size={16} />}
                        <span>{flag.flag.replace(/_/g, ' ').toUpperCase()}</span>
                      </div>
                      <div className="flag-details">
                        <span className={`flag-status ${flag.status}`}>{flag.status}</span>
                        <span className={`flag-impact ${flag.impact}`}>Impact: {flag.impact}</span>
                      </div>
                      {flag.items && (
                        <div className="flag-items">
                          {flag.items.map((item, i) => (
                            <span key={i} className="flag-item">{item}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Render Accuracy Considerations Section
  const renderAccuracyConsiderations = () => {
    if (!results.accuracy_considerations) return null

    const accuracy = results.accuracy_considerations
    const isExpanded = expandedSections.accuracy

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('accuracy')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Shield size={20} className="section-icon" />
            <h3>Accuracy Considerations</h3>
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
          <div className="accuracy-content">
            {/* Projection Confidence */}
            {accuracy.projection_confidence && (
              <div className="accuracy-subsection">
                <h5>Projection Confidence Levels</h5>
                <div className="confidence-levels-grid">
                  {Object.entries(accuracy.projection_confidence).map(([timeframe, confidence]) => (
                    <div key={timeframe} className="confidence-level-item">
                      <span className="timeframe">{timeframe.replace(/_/g, ' ')}</span>
                      <span className={`confidence-badge ${confidence.toLowerCase().replace(' ', '_')}`}>
                        {confidence}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Factors */}
            {accuracy.risk_factors && accuracy.risk_factors.length > 0 && (
              <div className="accuracy-subsection">
                <h5>Risk Factors</h5>
                <div className="risk-factors-grid">
                  {accuracy.risk_factors.map((risk, index) => (
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

            {/* Improvement Recommendations */}
            {accuracy.improvement_recommendations && accuracy.improvement_recommendations.length > 0 && (
              <div className="accuracy-subsection">
                <h5>Improvement Recommendations</h5>
                <ul className="recommendations-list">
                  {accuracy.improvement_recommendations.map((recommendation, index) => (
                    <li key={index} className="recommendation-item">
                      <Lightbulb size={16} />
                      <span>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Model Limitations */}
            {accuracy.model_limitations && accuracy.model_limitations.length > 0 && (
              <div className="accuracy-subsection">
                <h5>Model Limitations</h5>
                <ul className="limitations-list">
                  {accuracy.model_limitations.map((limitation, index) => (
                    <li key={index} className="limitation-item">
                      <AlertOctagon size={16} />
                      <span>{limitation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Render QA Checks Section
  const renderQAChecks = () => {
    if (!results.qa_checks) return null

    const qaChecks = results.qa_checks
    const isExpanded = expandedSections.qa_checks

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('qa_checks')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <CheckSquare size={20} className="section-icon" />
            <h3>Quality Assurance Checks</h3>
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
          <div className="json-container">
            <pre 
              className="json-content enhanced"
              dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(qaChecks) }}
            />
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Enhanced Normalized Data Rendering
  const renderNormalizedData = () => {
    if (!results.normalized_data) return null

    const normalized = results.normalized_data
    const isExpanded = expandedSections.normalized

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('normalized')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Database size={20} className="section-icon" />
            <h3>Normalized Data Analysis</h3>
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
          <div className="normalized-data-content">
            {/* Period Metadata */}
            {normalized.period_metadata && (
              <div className="normalized-subsection">
                <h5>Period Metadata</h5>
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="metadata-key">Granularity Used:</span>
                    <span className="metadata-value">{normalized.period_metadata.granularity_used}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-key">Period Format:</span>
                    <span className="metadata-value">{normalized.period_metadata.period_format}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-key">Total Periods:</span>
                    <span className="metadata-value">{normalized.period_metadata.total_periods}</span>
                  </div>
                  {normalized.period_metadata.date_range && (
                    <>
                      <div className="metadata-item">
                        <span className="metadata-key">Start Period:</span>
                        <span className="metadata-value">{normalized.period_metadata.date_range.start}</span>
                      </div>
                      <div className="metadata-item">
                        <span className="metadata-key">End Period:</span>
                        <span className="metadata-value">{normalized.period_metadata.date_range.end}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Seasonality Analysis */}
            {normalized.seasonality_analysis && (
              <div className="normalized-subsection">
                <h5>Seasonality Analysis</h5>
                <div className="seasonality-content">
                  {normalized.seasonality_analysis.seasonal_patterns_detected !== undefined && (
                    <div className="seasonality-item">
                      <strong>Patterns Detected:</strong> 
                      {normalized.seasonality_analysis.seasonal_patterns_detected ? ' ✅ Yes' : ' ❌ No'}
                    </div>
                  )}
                  {normalized.seasonality_analysis.peak_months && (
                    <div className="seasonality-item">
                      <strong>Peak Months:</strong> {normalized.seasonality_analysis.peak_months.join(', ')}
                    </div>
                  )}
                  {normalized.seasonality_analysis.trough_months && (
                    <div className="seasonality-item">
                      <strong>Trough Months:</strong> {normalized.seasonality_analysis.trough_months.join(', ')}
                    </div>
                  )}
                  {normalized.seasonality_analysis.seasonal_amplitude && (
                    <div className="seasonality-item">
                      <strong>Seasonal Amplitude:</strong> {formatPercentage(normalized.seasonality_analysis.seasonal_amplitude)}
                    </div>
                  )}
                  {normalized.seasonality_analysis.deseasonalized_trend && (
                    <div className="seasonality-item">
                      <strong>Deseasonalized Trend:</strong> {normalized.seasonality_analysis.deseasonalized_trend}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Growth Rates */}
            {normalized.growth_rates && (
              <div className="normalized-subsection">
                <h5>Growth Rates Analysis</h5>
                <div className="growth-rates-grid">
                  {Object.entries(normalized.growth_rates).map(([key, value]) => (
                    <div key={key} className="growth-rate-item">
                      <span className="growth-rate-label">{key.replace(/_/g, ' ').toUpperCase()}</span>
                      <span className="growth-rate-value">
                        {typeof value === 'object' ? JSON.stringify(value) : 
                         typeof value === 'number' ? formatPercentage(value) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Enhanced Business Intelligence from Stage 2 */}
            {normalized.business_context && (
              <div className="normalized-subsection">
                <h5>Business Intelligence Summary</h5>
                <div className="business-intelligence-grid">
                  <div className="intelligence-item">
                    <span className="intelligence-label">Industry Classification:</span>
                    <span className="intelligence-value">{normalized.business_context.industry_classification || 'Not detected'}</span>
                  </div>
                  <div className="intelligence-item">
                    <span className="intelligence-label">Business Stage:</span>
                    <span className={`intelligence-value stage-${normalized.business_context.business_stage}`}>
                      {normalized.business_context.business_stage || 'Unknown'}
                    </span>
                  </div>
                  <div className="intelligence-item">
                    <span className="intelligence-label">Market Position:</span>
                    <span className="intelligence-value">{normalized.business_context.competitive_position || 'Unknown'}</span>
                  </div>
                  <div className="intelligence-item">
                    <span className="intelligence-label">Market Geography:</span>
                    <span className="intelligence-value">{normalized.business_context.market_geography || 'Not specified'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Pattern Analysis Results */}
            {normalized.pattern_analysis && (
              <div className="normalized-subsection">
                <h5>Financial Pattern Analysis</h5>
                {normalized.pattern_analysis.growth_rates && (
                  <div className="pattern-analysis-summary">
                    <div className="pattern-summary-item">
                      <strong>Revenue CAGR:</strong> 
                      <span className="growth-value">
                        {normalized.pattern_analysis.growth_rates.revenue_cagr ? 
                          formatPercentage(normalized.pattern_analysis.growth_rates.revenue_cagr) : 'N/A'}
                      </span>
                    </div>
                    <div className="pattern-summary-item">
                      <strong>Profit CAGR:</strong> 
                      <span className="growth-value">
                        {normalized.pattern_analysis.growth_rates.profit_cagr ? 
                          formatPercentage(normalized.pattern_analysis.growth_rates.profit_cagr) : 'N/A'}
                      </span>
                    </div>
                    <div className="pattern-summary-item">
                      <strong>Growth Trend:</strong> 
                      <span className={`trend-indicator ${normalized.pattern_analysis.growth_rates.recent_growth_trend}`}>
                        {normalized.pattern_analysis.growth_rates.recent_growth_trend || 'Unknown'}
                      </span>
                    </div>
                  </div>
                )}
                
                {normalized.pattern_analysis.volatility_assessment && (
                  <div className="volatility-summary">
                    <h6>Volatility Assessment</h6>
                    <div className="volatility-grid">
                      <div className="volatility-item">
                        <span>Revenue Volatility:</span>
                        <span className={`volatility-level ${normalized.pattern_analysis.volatility_assessment.revenue_volatility}`}>
                          {normalized.pattern_analysis.volatility_assessment.revenue_volatility}
                        </span>
                      </div>
                      <div className="volatility-item">
                        <span>Overall Stability:</span>
                        <span className={`stability-level ${normalized.pattern_analysis.volatility_assessment.overall_stability}`}>
                          {normalized.pattern_analysis.volatility_assessment.overall_stability}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Key Assumptions from Analysis */}
            {normalized.key_assumptions && normalized.key_assumptions.length > 0 && (
              <div className="normalized-subsection">
                <h5>Key Analysis Assumptions</h5>
                <div className="assumptions-list">
                  {normalized.key_assumptions.map((assumption, index) => (
                    <div key={index} className="assumption-item">
                      <div className="assumption-content">{assumption}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Time Series Data Sample */}
            {normalized.time_series && (
              <div className="normalized-subsection">
                <h5>Time Series Data (Sample)</h5>
                <div className="time-series-sample">
                  {Object.entries(normalized.time_series).map(([seriesName, seriesData]) => (
                    <div key={seriesName} className="series-item">
                      <h6>{seriesName.replace(/_/g, ' ').toUpperCase()}</h6>
                      <div className="series-preview">
                        {Array.isArray(seriesData) && seriesData.slice(0, 3).map((point, index) => (
                          <div key={index} className="data-point">
                            <span className="period">{point.period}</span>
                            <span className="value">{formatCurrency(point.value)}</span>
                            <span className="source">{point.data_source}</span>
                          </div>
                        ))}
                        {Array.isArray(seriesData) && seriesData.length > 3 && (
                          <div className="data-point-more">...and {seriesData.length - 3} more periods</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Financial Ratios */}
            {normalized.financial_ratios && (
              <div className="normalized-subsection">
                <h5>Financial Ratios (Latest)</h5>
                <div className="financial-ratios-grid">
                  {Object.entries(normalized.financial_ratios).map(([ratioName, ratioData]) => {
                    const latestRatio = Array.isArray(ratioData) && ratioData.length > 0 ? ratioData[ratioData.length - 1] : null
                    return (
                      <div key={ratioName} className="ratio-item">
                        <span className="ratio-label">{ratioName.replace(/_/g, ' ').toUpperCase()}</span>
                        {latestRatio && (
                          <>
                            <span className="ratio-value">{typeof latestRatio.value === 'number' ? latestRatio.value.toFixed(3) : latestRatio.value}</span>
                            <span className="ratio-period">{latestRatio.period}</span>
                          </>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Enhanced Projections Rendering with Australian FY and New Array Format
  const renderEnhancedProjections = () => {
    if (!results.projections) return null

    const projections = results.projections
    const isExpanded = expandedSections.projections

    // Helper function to render metric data points
    const renderMetricDataPoints = (metricData, metricName, granularity) => {
      if (!Array.isArray(metricData) || metricData.length === 0) {
        return <div className="empty-metric">No {metricName} data available</div>
      }

      const maxDisplay = granularity === 'monthly' ? 6 : granularity === 'quarterly' ? 6 : 4
      const displayData = metricData.slice(0, maxDisplay)
      const hasMore = metricData.length > maxDisplay

      return (
        <div className="metric-data-points">
          <div className="metric-header">
            <span className="metric-name">{metricName.charAt(0).toUpperCase() + metricName.slice(1).replace(/_/g, ' ')}</span>
            <span className="data-count">({metricData.length} {granularity} points)</span>
          </div>
          <div className={`projections-grid ${granularity}-grid`}>
            {displayData.map((point, index) => (
              <div key={index} className={`period-projection-card ${granularity}-card`}>
                <div className="period-title">{point.period}</div>
                <div className="projection-metrics">
                  <div className="projection-metric">
                    <div className="metric-value-container">
                      <span className="metric-value">{formatCurrency(point.value)}</span>
                      {point.confidence && (
                        <span className={`confidence-badge ${point.confidence}`}>
                          {point.confidence}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {hasMore && (
            <details className="additional-months">
              <summary>Show remaining {metricData.length - maxDisplay} {granularity} data points</summary>
              <div className={`projections-grid ${granularity}-grid`}>
                {metricData.slice(maxDisplay).map((point, index) => (
                  <div key={index + maxDisplay} className={`period-projection-card ${granularity}-card`}>
                    <div className="period-title">{point.period}</div>
                    <div className="projection-metrics">
                      <div className="projection-metric">
                        <div className="metric-value-container">
                          <span className="metric-value">{formatCurrency(point.value)}</span>
                          {point.confidence && (
                            <span className={`confidence-badge ${point.confidence}`}>
                              {point.confidence}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )
    }

    // Helper function to render legacy single-value format
    const renderLegacyProjections = (data) => {
      return (
        <div className="projection-metrics">
          {data.revenue && (
            <div className="projection-metric">
              <span className="metric-label">Revenue:</span>
              <div className="metric-value-container">
                <span className="metric-value">{formatCurrency(data.revenue.value)}</span>
                {data.revenue.confidence && (
                  <span className={`confidence-badge ${data.revenue.confidence}`}>
                    {data.revenue.confidence}
                  </span>
                )}
              </div>
              {data.revenue.growth_rate && (
                <div className="growth-rate">Growth: {formatPercentage(data.revenue.growth_rate)}</div>
              )}
            </div>
          )}

          {data.expenses && (
            <div className="projection-metric">
              <span className="metric-label">Expenses:</span>
              <div className="metric-value-container">
                <span className="metric-value">{formatCurrency(data.expenses.value)}</span>
                {data.expenses.confidence && (
                  <span className={`confidence-badge ${data.expenses.confidence}`}>
                    {data.expenses.confidence}
                  </span>
                )}
              </div>
            </div>
          )}

          {data.net_profit && (
            <div className="projection-metric">
              <span className="metric-label">Net Profit:</span>
              <div className="metric-value-container">
                <span className="metric-value">{formatCurrency(data.net_profit.value)}</span>
                {data.net_profit.confidence && (
                  <span className={`confidence-badge ${data.net_profit.confidence}`}>
                    {data.net_profit.confidence}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Support both new gross_profit and legacy assets */}
          {(data.gross_profit || data.assets) && (
            <div className="projection-metric">
              <span className="metric-label">{data.gross_profit ? 'Gross Profit:' : 'Assets:'}</span>
              <div className="metric-value-container">
                <span className="metric-value">{formatCurrency((data.gross_profit || data.assets).value)}</span>
                {(data.gross_profit || data.assets).confidence && (
                  <span className={`confidence-badge ${(data.gross_profit || data.assets).confidence}`}>
                    {(data.gross_profit || data.assets).confidence}
                  </span>
                )}
              </div>
            </div>
          )}

          {data.key_ratios && (
            <div className="key-ratios">
              <h6>Key Ratios:</h6>
              {Object.entries(data.key_ratios).map(([ratio, value]) => (
                <div key={ratio} className="ratio-item-small">
                  <span>{ratio.replace(/_/g, ' ')}:</span>
                  <span>{typeof value === 'number' ? value.toFixed(3) : value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('projections')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <TrendingUp size={20} className="section-icon" />
            <h3>Australian FY Projections</h3>
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
          <div className="enhanced-projections">
            {/* Australian FY Note */}
            {projections.australian_fy_note && (
              <div className="fy-note">
                <Info size={16} />
                <p>{projections.australian_fy_note}</p>
              </div>
            )}

            {/* Methodology */}
            {projections.methodology && (
              <div className="projection-subsection">
                <h5 className="subsection-title">
                  <Target size={16} />
                  Methodology
                </h5>
                <p className="methodology-text">{projections.methodology}</p>
                {projections.base_period && (
                  <p className="base-period-text"><strong>Base Period:</strong> {projections.base_period}</p>
                )}
              </div>
            )}

            {/* Enhanced Projections Display - Handle both new and legacy formats */}
            {(projections.base_case_projections || projections.specific_projections) && (
              <div className="projection-subsection">
                <div className="subsection-header">
                  <h5 className="subsection-title">
                    <DollarSign size={16} />
                    Financial Projections
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
                          <div className="tooltip-item">
                            <span className="confidence-badge very_low">Very Low</span>
                            <span>&lt;40% - Highly uncertain projection</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {Object.entries(projections.base_case_projections || projections.specific_projections || {}).map(([interval, data]) => {
                  // Check if this is the new array format
                  const isNewFormat = data.granularity && data.data_points && (
                    Array.isArray(data.revenue) || Array.isArray(data.gross_profit) || 
                    Array.isArray(data.expenses) || Array.isArray(data.net_profit)
                  )
                  
                  return (
                    <div key={interval} className="projection-interval-section">
                      <h6 className="projection-interval-title">
                        {interval.replace(/_/g, ' ').toUpperCase()}
                        {data.granularity && (
                          <span className="granularity-badge">{data.granularity}</span>
                        )}
                      </h6>
                      {(data.period_label || data.period) && (
                        <div className="projection-period">{data.period_label || data.period}</div>
                      )}

                      {isNewFormat ? (
                        <div className="new-format-projections">
                          {/* Revenue Data Points */}
                          {data.revenue && renderMetricDataPoints(data.revenue, 'revenue', data.granularity)}
                          
                          {/* Gross Profit Data Points */}
                          {data.gross_profit && renderMetricDataPoints(data.gross_profit, 'gross_profit', data.granularity)}
                          
                          {/* Expenses Data Points */}
                          {data.expenses && renderMetricDataPoints(data.expenses, 'expenses', data.granularity)}
                          
                          {/* Net Profit Data Points */}
                          {data.net_profit && renderMetricDataPoints(data.net_profit, 'net_profit', data.granularity)}
                        </div>
                      ) : (
                        <div className="legacy-format-projections">
                          {renderLegacyProjections(data)}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}

            {/* Trend Analysis */}
            {projections.trend_analysis && (
              <div className="projection-subsection">
                <h5 className="subsection-title">
                  <TrendingUp size={16} />
                  Trend Analysis
                </h5>
                <div className="trend-analysis-content">
                  {Object.entries(projections.trend_analysis).map(([key, value]) => (
                    <div key={key} className="trend-item">
                      <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
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

            {/* Scenarios */}
            {projections.scenarios && (
              <div className="projection-subsection">
                <h5 className="subsection-title">
                  <Shield size={16} />
                  Alternative Scenarios
                </h5>
                <div className="scenarios-grid">
                  {Object.entries(projections.scenarios).map(([scenarioName, scenario]) => (
                    <div key={scenarioName} className="scenario-card">
                      <h6 className="scenario-title">{scenarioName.charAt(0).toUpperCase() + scenarioName.slice(1)}</h6>
                      {scenario.description && (
                        <p className="scenario-description">{scenario.description}</p>
                      )}
                      
                      {/* Scenario Multipliers */}
                      <div className="scenario-multipliers">
                        {Object.entries(scenario).filter(([key]) => key.includes('multiplier')).map(([key, value]) => (
                          <div key={key} className="scenario-metric">
                            <span className="metric-label">{key.replace(/_/g, ' ')}:</span>
                            <span className={`multiplier-value ${value > 1 ? 'positive' : 'negative'}`}>
                              {((value - 1) * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>

                      {/* Key Drivers */}
                      {scenario.key_drivers && (
                        <div className="key-drivers">
                          <h6>Key Drivers:</h6>
                          <ul>
                            {scenario.key_drivers.map((driver, index) => (
                              <li key={index}>{driver}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
  }

  // Add a new section to showcase the 3-stage architecture
  const renderArchitectureOverview = () => {
    const architectureData = results.data_analysis_summary
    if (!architectureData || !architectureData.architecture_type) return null

    const isExpanded = expandedSections.architecture_overview || false

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="results-section"
      >
        <motion.div
          className="section-header"
          onClick={() => toggleSection('architecture_overview')}
          whileHover={{ backgroundColor: 'var(--surface-2)' }}
          transition={{ duration: 0.2 }}
        >
          <div className="section-title">
            <Zap size={20} className="section-icon" />
            <h3>Enhanced 3-Stage Architecture</h3>
            {architectureData.api_calls_utilized && (
              <span className="section-count">({architectureData.api_calls_utilized} API calls)</span>
            )}
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
          <div className="processing-details-section">
            <h4>
              <Activity size={16} />
              Processing Performance
            </h4>
            <div className="processing-details-grid">
              <div className="detail-item">
                <span className="detail-key">Architecture Type</span>
                <span className="detail-value">{architectureData.architecture_type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-key">Stages Completed</span>
                <span className="detail-value">{architectureData.processing_stages_completed || 3}/3</span>
              </div>
              <div className="detail-item">
                <span className="detail-key">Total Processing Time</span>
                <span className="detail-value">{architectureData.total_processing_time?.toFixed(2)}s</span>
              </div>
              <div className="detail-item">
                <span className="detail-key">API Calls Used</span>
                <span className="detail-value">{architectureData.api_calls_utilized}</span>
              </div>
              <div className="detail-item">
                <span className="detail-key">Success Rate</span>
                <span className="detail-value">{(architectureData.extraction_success_rate * 100).toFixed(1)}%</span>
              </div>
            </div>

            {architectureData.stage_timings && (
              <>
                <h4 style={{ marginTop: 'var(--space-lg)' }}>
                  <Clock size={16} />
                  Stage Performance Breakdown
                </h4>
                <div className="processing-details-grid">
                  <div className="detail-item">
                    <span className="detail-key">Stage 1: Extraction</span>
                    <span className="detail-value">{architectureData.stage_timings.extraction_normalization?.toFixed(2)}s</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-key">Stage 2: Analysis</span>
                    <span className="detail-value">{architectureData.stage_timings.business_analysis?.toFixed(2)}s</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-key">Stage 3: Projections</span>
                    <span className="detail-value">{architectureData.stage_timings.projection_engine?.toFixed(2)}s</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-key">Local Validation</span>
                    <span className="detail-value">{architectureData.stage_timings.local_validation?.toFixed(2)}s</span>
                  </div>
                </div>
              </>
            )}

            {architectureData.enhancement_features && (
              <>
                <h4 style={{ marginTop: 'var(--space-lg)' }}>
                  <Award size={16} />
                  Enhanced Features Applied
                </h4>
                <div className="enhancement-features">
                  {architectureData.enhancement_features.map((feature, index) => (
                    <span key={index} className="feature-badge">
                      ✨ {feature.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    )
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
            {renderFormattedExplanation(results.explanation || results.executive_summary)}
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
              <span>
                {results.data_quality_assessment?.completeness_score 
                  ? `${(results.data_quality_assessment.completeness_score * 100).toFixed(1)}%` 
                  : results.data_quality_score 
                    ? `${(results.data_quality_score * 100).toFixed(1)}%` 
                    : 'Analyzed'}
              </span>
            </div>
          </div>
          
          <div className="overview-item">
            <TrendingUp size={20} className="overview-icon" />
            <div className="overview-details">
              <h4>Projections</h4>
              <span>
                {results.projections?.specific_projections 
                  ? `${Object.keys(results.projections.specific_projections).length} intervals`
                  : results.projections?.yearly_projections
                    ? `${Object.keys(results.projections.yearly_projections).length} years`
                    : 'Generated'}
              </span>
            </div>
          </div>
          
          {results.data_analysis_summary?.period_granularity_detected && (
            <div className="overview-item">
              <Clock size={20} className="overview-icon" />
              <div className="overview-details">
                <h4>Time Granularity</h4>
                <span>{results.data_analysis_summary.period_granularity_detected.charAt(0).toUpperCase() + results.data_analysis_summary.period_granularity_detected.slice(1)}</span>
              </div>
            </div>
          )}
          
          {results.accuracy_considerations?.projection_confidence && (
            <div className="overview-item">
              <Shield size={20} className="overview-icon" />
              <div className="overview-details">
                <h4>Confidence Level</h4>
                <span>
                  {Object.values(results.accuracy_considerations.projection_confidence)[0] || 'Assessed'}
                </span>
              </div>
            </div>
          )}
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

        {/* Toggle Charts Button */}
        {chartData.length > 0 && (
          <motion.button
            onClick={() => setShowCharts(!showCharts)}
            className={`action-button chart-button ${showCharts ? 'active' : ''}`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <BarChart3 size={18} />
            {showCharts ? 'Hide Charts' : 'Show Charts'}
          </motion.button>
        )}
        
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

      {/* Enhanced Export Options */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="enhanced-export-section"
      >
        <ExportUtils
          data={filteredData}
          fileName={`multi-pdf-analysis-${new Date().toISOString().split('T')[0]}`}
          contentRef={contentRef}
          chartRefs={chartRefs.current}
        />
      </motion.div>

      {/* Search and Filter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="search-filter-section"
      >
        <SearchFilter
          data={results}
          onFilter={handleFilter}
          onSort={handleSort}
          onSearch={handleSearch}
        />
      </motion.div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="error-section"
        >
          <ErrorDisplay
            error={error}
            onRetry={() => setError(null)}
            onDismiss={() => setError(null)}
          />
        </motion.div>
      )}

      {/* Charts Section */}
      {showCharts && chartData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="charts-section"
        >
          <div className="charts-header">
            <h3>
              <BarChart3 size={20} />
              Analysis Visualization
            </h3>
            <span className="charts-count">{chartData.length} charts</span>
          </div>
          
          <div className="charts-grid">
            {chartData.map((chart, index) => (
              <div
                key={index}
                ref={el => chartRefs.current[index] = el}
                className="chart-wrapper"
              >
                <FinancialChart
                  data={chart.data}
                  type={chart.type}
                  title={chart.title}
                  subtitle={chart.subtitle}
                  height={350}
                />
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Results Sections */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="analysis-results"
        ref={contentRef}
      >
        {/* Executive Summary - Show first if available */}
        {results.summary && renderSummarySection()}

        {/* Executive Summary / Explanation - Show if available */}
        {(results.explanation || results.executive_summary) && renderExplanationSection()}

        {/* Business Context Analysis - Stage 2 business intelligence */}
        {results.normalized_data && results.normalized_data.business_context && renderBusinessContextAnalysis()}

        {/* Methodology Evaluation - Stage 2 method selection */}
        {results.normalized_data && results.normalized_data.methodology_evaluation && renderMethodologyEvaluation()}

        {/* Data Analysis Summary - Show period detection and overview */}
        {results.data_analysis_summary && renderDataAnalysisSummary()}

        {/* Methodology - Show model transparency information */}
        {results.methodology && renderMethodologySection()}

        {/* Projections - Main feature */}
        {results.projections && renderEnhancedProjections()}

        {/* Scenario Analysis - Optimistic and Conservative scenarios */}
        {results.projections && results.projections.scenario_projections && renderScenarioAnalysis()}

        {/* Normalized Data - Processed data insights */}
        {results.normalized_data && renderNormalizedData()}

        {/* Data Quality Assessment - Quality metrics */}
        {results.data_quality_assessment && renderDataQualityAssessment()}

        {/* Accuracy Considerations - Confidence and limitations */}
        {results.accuracy_considerations && renderAccuracyConsiderations()}

        {/* QA Checks - Technical validation */}
        {results.qa_checks && renderQAChecks()}

        {/* Extracted Data - Raw source data */}
        {results.extracted_data && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="results-section"
          >
            <motion.div
              className="section-header"
              onClick={() => toggleSection('extracted')}
              whileHover={{ backgroundColor: 'var(--surface-2)' }}
              transition={{ duration: 0.2 }}
            >
              <div className="section-title">
                <FileText size={20} className="section-icon" />
                <h3>Extracted Data</h3>
                <span className="section-count">
                  ({Array.isArray(results.extracted_data) ? results.extracted_data.length : Object.keys(results.extracted_data || {}).length} items)
                </span>
              </div>
              <motion.div
                animate={{ rotate: expandedSections.extracted ? 90 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronRight size={20} />
              </motion.div>
            </motion.div>
            
            <motion.div
              initial={false}
              animate={{ height: expandedSections.extracted ? 'auto' : 0, opacity: expandedSections.extracted ? 1 : 0 }}
              transition={{ duration: 0.3 }}
              className="section-content"
            >
              <div className="json-container">
                <pre 
                  className="json-content enhanced"
                  dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(results.extracted_data) }}
                />
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Enhanced 3-Stage Architecture Overview */}
        {results.data_analysis_summary && renderArchitectureOverview()}

        {/* Show a message if no major sections are available */}
        {!results.summary && !results.explanation && !results.executive_summary && !results.projections && !results.normalized_data && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="results-section"
          >
            <div className="empty-section">
              <p>Analysis results are processing or incomplete. Please check the raw data sections above.</p>
            </div>
          </motion.div>
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