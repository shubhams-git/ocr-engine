import { useState } from 'react'
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
  ChevronRight
} from 'lucide-react'

const ResultsDisplay = ({ results, fileName, selectedModel, onReset }) => {
  const [copied, setCopied] = useState(false)
  const [viewMode, setViewMode] = useState('formatted') // 'formatted' or 'raw'
  const [expandedSections, setExpandedSections] = useState({})

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

      {/* Enhanced Content Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="extracted-content-container"
      >
        {renderFormattedContent()}
      </motion.div>
    </motion.div>
  )
}

export default ResultsDisplay 