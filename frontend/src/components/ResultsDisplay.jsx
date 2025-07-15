import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Copy, 
  Download, 
  RefreshCw, 
  CheckCircle, 
  FileText, 
  Cpu,
  Database,
  Image,
  Eye,
  Code,
  Table,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Calculator,
  TrendingUp,
  DollarSign,
  PieChart,
  Activity,
  AlertCircle,
  CheckCircle2,
  Info,
  Calendar,
  Target,
  Zap,
  ArrowRight,
  Building,
  CreditCard,
  Banknote,
  Search,
  Filter
} from 'lucide-react'
import FinancialChart from './FinancialChart'
import ExportUtils from './ExportUtils'
import SearchFilter from './SearchFilter'
import { ErrorDisplay } from './ErrorBoundary'

const ResultsDisplay = ({ results, fileName, selectedModel, onReset }) => {
  const [copied, setCopied] = useState(false)
  const [viewMode, setViewMode] = useState('formatted') // 'formatted' or 'raw'
  const [expandedSections, setExpandedSections] = useState({})
  const [expandedStatements, setExpandedStatements] = useState({})
  const [filteredData, setFilteredData] = useState(results)
  const [searchTerm, setSearchTerm] = useState('')
  const [showCharts, setShowCharts] = useState(false)
  const [error, setError] = useState(null)
  
  // Refs for export functionality
  const contentRef = useRef(null)
  const chartRefs = useRef([])

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(results.data || '')
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  const handleDownload = () => {
    const fileExtension = getFileType(fileName) === 'csv' ? 'json' : 'txt'
    const element = document.createElement('a')
    const file = new Blob([results.data || ''], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `${fileName?.split('.')[0] || 'ocr'}_extracted.${fileExtension}`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // Filter and search handlers
  const handleFilter = (filters) => {
    let filtered = results
    
    // Apply filters here based on the filter criteria
    if (filters.metricType !== 'all') {
      // Filter by metric type
      filtered = { ...filtered }
      // Implementation depends on data structure
    }
    
    setFilteredData(filtered)
  }

  const handleSearch = (term) => {
    setSearchTerm(term)
    
    if (!term) {
      setFilteredData(results)
      return
    }
    
    // Search through the data
    const searchResults = { ...results }
    // Implementation depends on data structure
    setFilteredData(searchResults)
  }

  const handleSort = (field, order) => {
    // Sort the filtered data
    const sorted = { ...filteredData }
    // Implementation depends on data structure
    setFilteredData(sorted)
  }

  // Generate chart data from financial statements
  const generateChartData = (data) => {
    const chartData = []
    
    if (data.profit_and_loss_statement) {
      const pnlData = data.profit_and_loss_statement
      
      // Revenue chart
      if (pnlData['1_year'] && pnlData['1_year'].monthly) {
        const revenueData = {
          labels: Object.keys(pnlData['1_year'].monthly),
          datasets: [{
            label: 'Monthly Revenue',
            data: Object.values(pnlData['1_year'].monthly).map(month => month.revenue || 0)
          }]
        }
        chartData.push({
          type: 'line',
          title: 'Monthly Revenue Trend',
          data: revenueData
        })
      }
      
      // Profit margin chart
      if (pnlData['1_year'] && pnlData['1_year'].quarterly) {
        const profitData = {
          labels: Object.keys(pnlData['1_year'].quarterly),
          datasets: [{
            label: 'Quarterly Profit',
            data: Object.values(pnlData['1_year'].quarterly).map(quarter => quarter.net_profit || 0)
          }]
        }
        chartData.push({
          type: 'bar',
          title: 'Quarterly Profit Analysis',
          data: profitData
        })
      }
    }
    
    return chartData
  }

  const chartData = generateChartData(filteredData)

  const getWordsCount = () => {
    return (results.data || '').split(/\s+/).filter(word => word.length > 0).length
  }

  const getCharactersCount = () => {
    return (results.data || '').length
  }

  const getLinesCount = () => {
    return (results.data || '').split('\n').filter(line => line.trim().length > 0).length
  }

  const getFileType = (filename) => {
    if (!filename) return 'unknown'
    const ext = filename.toLowerCase().split('.').pop()
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'].includes(ext)) return 'image'
    if (ext === 'pdf') return 'pdf'
    if (ext === 'csv') return 'csv'
    return 'unknown'
  }

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'image':
        return <Image size={20} />
      case 'pdf':
        return <FileText size={20} />
      case 'csv':
        return <Database size={20} />
      default:
        return <FileText size={20} />
    }
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

  const isValidJSON = (str) => {
    try {
      JSON.parse(str)
      return true
    } catch (e) {
      return false
    }
  }

  const parseJSON = (str) => {
    try {
      return JSON.parse(str)
    } catch (e) {
      return null
    }
  }

  const formatJsonWithSyntaxHighlighting = (obj) => {
    const jsonString = JSON.stringify(obj, null, 2)
    
    return jsonString
      .replace(/("([^"\\]|\\.)*")\s*:/g, '<span class="json-key">$1</span>:')
      .replace(/:\s*("([^"\\]|\\.)*")/g, ': <span class="json-string">$1</span>')
      .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
      .replace(/:\s*(true|false|null)/g, ': <span class="json-boolean">$1</span>')
  }

  const formatPlainText = (text) => {
    if (!text || !text.trim()) return text

    // Clean up excessive whitespace while preserving intentional breaks
    const lines = text.split('\n')
    const formattedLines = []
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      
      // Skip completely empty lines unless they're intentional breaks
      if (line === '' && i > 0 && i < lines.length - 1) {
        const prevLine = lines[i - 1].trim()
        const nextLine = lines[i + 1].trim()
        // Keep empty line if it's between non-empty lines (paragraph break)
        if (prevLine !== '' && nextLine !== '') {
          formattedLines.push('')
        }
      } else if (line !== '') {
        formattedLines.push(line)
      }
    }

    return formattedLines.join('\n')
  }

  const detectTextStructure = (text) => {
    if (!text || !text.trim()) return { type: 'plain', content: text }

    const lines = text.split('\n').filter(line => line.trim())
    
    // Check if it's a list-like structure
    const listPatterns = [
      /^\s*[-•*]\s+/, // Bullet points
      /^\s*\d+\.\s+/, // Numbered lists
      /^\s*[a-zA-Z]\.\s+/, // Lettered lists
    ]
    
    const isListLike = lines.slice(0, Math.min(5, lines.length)).some(line => 
      listPatterns.some(pattern => pattern.test(line))
    )

    // Check if it's table-like data
    const hasDelimiters = lines.slice(0, 3).some(line => 
      line.includes('|') || line.includes('\t') || /\s{2,}/.test(line)
    )

    if (isListLike) {
      return { type: 'list', content: text }
    } else if (hasDelimiters) {
      return { type: 'tabular', content: text }
    } else {
      return { type: 'paragraphs', content: text }
    }
  }

  const renderTextWithStructure = (text, structure) => {
    const formattedText = formatPlainText(text)
    
    switch (structure.type) {
      case 'list':
        return (
          <div className="structured-text list-format">
            <pre className="extracted-text">{formattedText}</pre>
          </div>
        )
      case 'tabular':
        return (
          <div className="structured-text tabular-format">
            <pre className="extracted-text tabular">{formattedText}</pre>
          </div>
        )
      case 'paragraphs':
        // Split into paragraphs for better readability
        const paragraphs = formattedText.split('\n\n').filter(p => p.trim())
        if (paragraphs.length > 1) {
          return (
            <div className="structured-text paragraph-format">
              {paragraphs.map((paragraph, index) => (
                <p key={index} className="text-paragraph">
                  {paragraph.split('\n').map((line, lineIndex) => (
                    <span key={lineIndex}>
                      {line}
                      {lineIndex < paragraph.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </p>
              ))}
            </div>
          )
        }
        // fallback to pre for single paragraph
        return (
          <div className="structured-text">
            <pre className="extracted-text">{formattedText}</pre>
          </div>
        )
      default:
        return (
          <div className="structured-text">
            <pre className="extracted-text">{formattedText}</pre>
          </div>
        )
    }
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const toggleStatement = (statement) => {
    setExpandedStatements(prev => ({
      ...prev,
      [statement]: !prev[statement]
    }))
  }

  // New function to detect financial forecast structure
  const isFinancialForecast = (data) => {
    if (!data || typeof data !== 'object') return false
    
    // Check for three-way forecast structure
    const hasThreeWayForecast = (
      data.profit_and_loss_statement ||
      data.cash_flow_statement ||
      data.balance_sheet ||
      data.financial_statements
    )
    
    // Check for calculation chains
    const hasCalculationChains = (
      data.calculation_chains ||
      (data.profit_and_loss_statement && data.profit_and_loss_statement.calculation_chains)
    )
    
    // Check for projections structure
    const hasProjections = (
      data.projections ||
      data.yearly_projections ||
      data.monthly_projections
    )
    
    return hasThreeWayForecast || hasCalculationChains || hasProjections
  }

  // New function to render financial statements
  const renderFinancialStatements = (data) => {
    if (!data || typeof data !== 'object') return null

    const statements = []
    
    // Check for different statement structures
    if (data.profit_and_loss_statement) {
      statements.push({
        key: 'profit_and_loss_statement',
        title: 'Profit & Loss Statement',
        icon: <TrendingUp size={20} />,
        data: data.profit_and_loss_statement,
        color: 'primary'
      })
    }
    
    if (data.cash_flow_statement) {
      statements.push({
        key: 'cash_flow_statement',
        title: 'Cash Flow Statement',
        icon: <Activity size={20} />,
        data: data.cash_flow_statement,
        color: 'secondary'
      })
    }
    
    if (data.balance_sheet) {
      statements.push({
        key: 'balance_sheet',
        title: 'Balance Sheet',
        icon: <Building size={20} />,
        data: data.balance_sheet,
        color: 'success'
      })
    }
    
    if (data.financial_statements) {
      // Handle nested financial statements
      const nestedStatements = data.financial_statements
      if (nestedStatements.profit_and_loss) {
        statements.push({
          key: 'nested_pnl',
          title: 'Profit & Loss Statement',
          icon: <TrendingUp size={20} />,
          data: nestedStatements.profit_and_loss,
          color: 'primary'
        })
      }
      if (nestedStatements.cash_flow) {
        statements.push({
          key: 'nested_cf',
          title: 'Cash Flow Statement',
          icon: <Activity size={20} />,
          data: nestedStatements.cash_flow,
          color: 'secondary'
        })
      }
      if (nestedStatements.balance_sheet) {
        statements.push({
          key: 'nested_bs',
          title: 'Balance Sheet',
          icon: <Building size={20} />,
          data: nestedStatements.balance_sheet,
          color: 'success'
        })
      }
    }

    return (
      <div className="financial-statements-container">
        <div className="statements-header">
          <h4>
            <PieChart size={20} />
            Financial Statements
          </h4>
          <span className="statements-count">{statements.length} statements</span>
        </div>
        
        <div className="statements-grid">
          {statements.map((statement) => (
            <div key={statement.key} className={`statement-card ${statement.color}`}>
              <div 
                className="statement-header"
                onClick={() => toggleStatement(statement.key)}
              >
                <div className="statement-title">
                  {statement.icon}
                  <h5>{statement.title}</h5>
                </div>
                <div className="statement-toggle">
                  {expandedStatements[statement.key] ? 
                    <ChevronDown size={20} /> : 
                    <ChevronRight size={20} />
                  }
                </div>
              </div>
              
              {expandedStatements[statement.key] && (
                <div className="statement-content">
                  {renderStatementData(statement.data, statement.key)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  // New function to render individual statement data
  const renderStatementData = (statementData, statementKey) => {
    if (!statementData || typeof statementData !== 'object') return null

    const sections = []
    
    // Handle different time periods
    const timePeriods = ['1_year', '3_year', '5_year', '10_year', '15_year', 'monthly', 'quarterly']
    
    timePeriods.forEach(period => {
      if (statementData[period]) {
        sections.push({
          key: period,
          title: period.replace('_', ' ').toUpperCase(),
          data: statementData[period],
          period: period
        })
      }
    })
    
    // Handle calculation chains
    if (statementData.calculation_chains) {
      sections.push({
        key: 'calculation_chains',
        title: 'Calculation Chains',
        data: statementData.calculation_chains,
        isCalculationChains: true
      })
    }

    return (
      <div className="statement-sections">
        {sections.map((section) => (
          <div key={section.key} className="statement-section">
            <div className="section-title">
              <Calendar size={16} />
              <h6>{section.title}</h6>
            </div>
            
            <div className="section-data">
              {section.isCalculationChains ? 
                renderCalculationChains(section.data) :
                renderFinancialMetrics(section.data, section.period)
              }
            </div>
          </div>
        ))}
      </div>
    )
  }

  // New function to render calculation chains
  const renderCalculationChains = (chains) => {
    if (!chains || typeof chains !== 'object') return null

    return (
      <div className="calculation-chains">
        {Object.entries(chains).map(([metric, chain]) => (
          <div key={metric} className="calculation-chain">
            <div className="chain-header">
              <Calculator size={16} />
              <span className="chain-metric">{metric.replace(/_/g, ' ')}</span>
            </div>
            
            <div className="chain-formula">
              {Array.isArray(chain) ? (
                chain.map((step, index) => (
                  <div key={index} className="chain-step">
                    <span className="step-number">{index + 1}.</span>
                    <span className="step-formula">{step}</span>
                  </div>
                ))
              ) : (
                <div className="chain-step">
                  <span className="step-formula">{chain}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  // New function to render financial metrics
  const renderFinancialMetrics = (metrics, period) => {
    if (!metrics || typeof metrics !== 'object') return null

    const formatValue = (value) => {
      if (typeof value === 'number') {
        return value.toLocaleString('en-US', { 
          style: 'currency', 
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })
      }
      return value
    }

    return (
      <div className="financial-metrics">
        {Object.entries(metrics).map(([key, value]) => {
          if (key === 'calculation_chains') return null
          
          return (
            <div key={key} className="metric-row">
              <div className="metric-label">
                <DollarSign size={14} />
                <span>{key.replace(/_/g, ' ')}</span>
              </div>
              <div className="metric-value">
                {typeof value === 'object' ? (
                  <div className="nested-metrics">
                    {Object.entries(value).map(([subKey, subValue]) => (
                      <div key={subKey} className="sub-metric">
                        <span className="sub-metric-label">{subKey.replace(/_/g, ' ')}</span>
                        <span className="sub-metric-value">{formatValue(subValue)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span className="metric-amount">{formatValue(value)}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // New function to render validation results
  const renderValidationResults = (data) => {
    if (!data || typeof data !== 'object') return null

    const validation = data.validation || data.validation_results
    if (!validation) return null

    return (
      <div className="validation-results">
        <div className="validation-header">
          <CheckCircle2 size={20} />
          <h4>Validation Results</h4>
        </div>
        
        <div className="validation-sections">
          {Object.entries(validation).map(([key, value]) => {
            if (key === 'is_valid') return null
            
            return (
              <div key={key} className="validation-section">
                <div className="validation-title">
                  <Target size={16} />
                  <h5>{key.replace(/_/g, ' ')}</h5>
                </div>
                
                <div className="validation-content">
                  {typeof value === 'object' ? (
                    <div className="validation-details">
                      {Object.entries(value).map(([subKey, subValue]) => (
                        <div key={subKey} className="validation-item">
                          <span className="validation-label">{subKey.replace(/_/g, ' ')}</span>
                          <span className={`validation-status ${subValue === true ? 'passed' : 'failed'}`}>
                            {subValue === true ? (
                              <><CheckCircle size={14} /> Passed</>
                            ) : (
                              <><AlertCircle size={14} /> {subValue}</>
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="validation-simple">
                      <span className={`validation-status ${value === true ? 'passed' : 'failed'}`}>
                        {value === true ? (
                          <><CheckCircle size={14} /> Passed</>
                        ) : (
                          <><AlertCircle size={14} /> {value}</>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  // New function to render working capital assumptions
  const renderWorkingCapitalAssumptions = (data) => {
    if (!data || typeof data !== 'object') return null

    const wcAssumptions = data.working_capital_assumptions || data.forecast_drivers?.working_capital_assumptions
    if (!wcAssumptions) return null

    return (
      <div className="working-capital-assumptions">
        <div className="wc-header">
          <CreditCard size={20} />
          <h4>Working Capital Assumptions</h4>
        </div>
        
        <div className="wc-metrics">
          {Object.entries(wcAssumptions).map(([key, value]) => (
            <div key={key} className="wc-metric">
              <div className="wc-metric-label">
                <Banknote size={14} />
                <span>{key.replace(/_/g, ' ')}</span>
              </div>
              <div className="wc-metric-value">
                {typeof value === 'object' ? (
                  Object.entries(value).map(([subKey, subValue]) => (
                    <div key={subKey} className="wc-sub-metric">
                      <span>{subKey}</span>
                      <span>{subValue}</span>
                    </div>
                  ))
                ) : (
                  <span>{value}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderStructuredData = (data) => {
    if (Array.isArray(data)) {
      return renderArray(data)
    } else if (typeof data === 'object' && data !== null) {
      return renderObject(data)
    } else {
      return <span className="primitive-value">{String(data)}</span>
    }
  }

  const renderArray = (arr) => {
    // Check if it's a tabular data structure
    if (arr.length > 0 && typeof arr[0] === 'object' && arr[0] !== null) {
      return renderTable(arr)
    }
    
    return (
      <div className="json-array">
        {arr.map((item, index) => (
          <div key={index} className="array-item">
            <span className="array-index">{index}:</span>
            {renderStructuredData(item)}
          </div>
        ))}
      </div>
    )
  }

  const renderObject = (obj) => {
    return (
      <div className="json-object">
        {Object.entries(obj).map(([key, value]) => (
          <div key={key} className="object-property">
            <span className="property-key">{key}:</span>
            <div className="property-value">
              {renderStructuredData(value)}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderTable = (data) => {
    if (!data || data.length === 0) return null

    const columns = Object.keys(data[0])
    
    return (
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map(column => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 100).map((row, index) => (
              <tr key={index}>
                {columns.map(column => (
                  <td key={column}>
                    {typeof row[column] === 'object' 
                      ? JSON.stringify(row[column]) 
                      : String(row[column] || '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {data.length > 100 && (
          <div className="table-footer">
            Showing first 100 rows of {data.length} total
          </div>
        )}
      </div>
    )
  }

  const renderFormattedContent = () => {
    const fileType = getFileType(fileName)
    const extractedData = results.data || ''
    
    if (!extractedData.trim()) {
      return (
        <div className="empty-content">
          <Eye size={48} />
          <h3>No Data Found</h3>
          <p>No extractable data was found in this document.</p>
        </div>
      )
    }

    // Try to parse as JSON first
    if (isValidJSON(extractedData)) {
      const jsonData = parseJSON(extractedData)
      
      // Check if it's a financial forecast
      if (isFinancialForecast(jsonData)) {
        return (
          <div className="formatted-content financial-forecast">
            <div className="content-header">
              <div className="content-title">
                <BarChart3 size={20} />
                <h4>Financial Forecast Analysis</h4>
                <span className="content-type">Three-Way Forecast</span>
              </div>
              <div className="view-mode-toggle">
                <button
                  onClick={() => setViewMode('formatted')}
                  className={`view-button ${viewMode === 'formatted' ? 'active' : ''}`}
                >
                  <Table size={16} />
                  Financial View
                </button>
                <button
                  onClick={() => setViewMode('raw')}
                  className={`view-button ${viewMode === 'raw' ? 'active' : ''}`}
                >
                  <Code size={16} />
                  Raw JSON
                </button>
              </div>
            </div>
            
            {viewMode === 'formatted' ? (
              <div className="financial-forecast-content">
                {renderFinancialStatements(jsonData)}
                {renderWorkingCapitalAssumptions(jsonData)}
                {renderValidationResults(jsonData)}
                
                {/* Additional sections for other data */}
                {jsonData.forecast_drivers && (
                  <div className="forecast-drivers">
                    <div className="drivers-header">
                      <Zap size={20} />
                      <h4>Forecast Drivers</h4>
                    </div>
                    <div className="drivers-content">
                      {renderStructuredData(jsonData.forecast_drivers)}
                    </div>
                  </div>
                )}
                
                {jsonData.projections && (
                  <div className="projections-section">
                    <div className="projections-header">
                      <TrendingUp size={20} />
                      <h4>Projections</h4>
                    </div>
                    <div className="projections-content">
                      {renderStructuredData(jsonData.projections)}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="json-display">
                <pre
                  className="json-content enhanced readable"
                  dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(jsonData) }}
                />
              </div>
            )}
          </div>
        )
      }
      
      // Regular JSON display for non-financial data
      return (
        <div className="formatted-content">
          <div className="content-header">
            <div className="content-title">
              <Code size={20} />
              <h4>Structured Data</h4>
              <span className="content-type">JSON Format</span>
            </div>
            <div className="view-mode-toggle">
              <button
                onClick={() => setViewMode('formatted')}
                className={`view-button ${viewMode === 'formatted' ? 'active' : ''}`}
              >
                <Table size={16} />
                Structured
              </button>
              <button
                onClick={() => setViewMode('raw')}
                className={`view-button ${viewMode === 'raw' ? 'active' : ''}`}
              >
                <Code size={16} />
                Raw JSON
              </button>
            </div>
          </div>
          
          {viewMode === 'formatted' ? (
            <div className="structured-data">
              {renderStructuredData(jsonData)}
            </div>
          ) : (
            <div className="json-display">
              <pre
                className="json-content enhanced readable"
                dangerouslySetInnerHTML={{ __html: formatJsonWithSyntaxHighlighting(jsonData) }}
              />
            </div>
          )}
        </div>
      )
    }

    // Handle plain text content with improved formatting
    const textStructure = detectTextStructure(extractedData)
    
    return (
      <div className="formatted-content">
        <div className="content-header">
          <div className="content-title">
            <FileText size={20} />
            <h4>Extracted Text</h4>
            <span className="content-type">
              {textStructure.type === 'list' ? 'List Format' : 
               textStructure.type === 'tabular' ? 'Tabular Data' :
               textStructure.type === 'paragraphs' ? 'Text Content' : 'Plain Text'}
            </span>
          </div>
        </div>
        
        <div className="text-content enhanced">
          {renderTextWithStructure(extractedData, textStructure)}
        </div>
      </div>
    )
  }

  const fileType = getFileType(fileName)

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="results-container"
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
          <span>Data Extracted Successfully!</span>
        </div>
        
        <div className="file-info">
          {getFileIcon(fileType)}
          <div className="file-details">
            <h3>{fileName || 'Uploaded File'}</h3>
            <div className="file-meta">
              <span className="meta-item">
                <Cpu size={14} />
                {getModelDisplayName(selectedModel)}
              </span>
              <span className="meta-item">
                <Database size={14} />
                {fileType.toUpperCase()} File
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="results-stats"
      >
        <div className="stat">
          <div className="stat-value">{getWordsCount()}</div>
          <div className="stat-label">Words</div>
        </div>
        <div className="stat">
          <div className="stat-value">{getCharactersCount()}</div>
          <div className="stat-label">Characters</div>
        </div>
        <div className="stat">
          <div className="stat-value">{getLinesCount()}</div>
          <div className="stat-label">Lines</div>
        </div>
        {isValidJSON(results.data) && (
          <div className="stat">
            <div className="stat-value">
              <BarChart3 size={20} />
            </div>
            <div className="stat-label">Structured</div>
          </div>
        )}
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
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
          {copied ? 'Copied!' : 'Copy Data'}
        </motion.button>
        
        <motion.button
          onClick={handleDownload}
          className="action-button download-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Download size={18} />
          Download
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
          Process Another
        </motion.button>
      </motion.div>

      {/* Enhanced Export Options */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="enhanced-export-section"
      >
        <ExportUtils
          data={filteredData}
          fileName={fileName}
          contentRef={contentRef}
          chartRefs={chartRefs.current}
        />
      </motion.div>

      {/* Search and Filter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
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
          transition={{ delay: 0.9 }}
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
          transition={{ delay: 0.9 }}
          className="charts-section"
        >
          <div className="charts-header">
            <h3>
              <BarChart3 size={20} />
              Financial Data Visualization
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

      {/* Enhanced Content Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="extracted-content-container"
        ref={contentRef}
      >
        {renderFormattedContent()}
      </motion.div>
    </motion.div>
  )
}

export default ResultsDisplay 