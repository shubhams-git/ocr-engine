import { motion } from 'framer-motion'
import { BookOpen, FileText, Brain, TrendingUp, Layers, CheckCircle, AlertTriangle, Info } from 'lucide-react'

const TestingGuide = ({ isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="testing-guide-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="testing-guide-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="guide-header">
          <BookOpen size={24} />
          <h2>Testing Dashboard Guide</h2>
        </div>

        <div className="guide-content">
          <section className="guide-section">
            <h3>Overview</h3>
            <p>
              The Testing Dashboard allows you to test individual services and monitor the complete 3-stage OCR pipeline. 
              This is perfect for debugging, development, and ensuring each component works correctly.
            </p>
          </section>

          <section className="guide-section">
            <h3>Test Modes</h3>
            
            <div className="test-mode-guide">
              <div className="mode-guide-card">
                <FileText size={20} style={{ color: 'var(--primary)' }} />
                <div>
                  <h4>Stage 1: OCR Service</h4>
                  <p>Tests data extraction and normalization from individual files.</p>
                  <div className="requirements">
                    <strong>Requirements:</strong> Upload a single PDF, CSV, or image file
                  </div>
                </div>
              </div>

              <div className="mode-guide-card">
                <Brain size={20} style={{ color: 'var(--secondary)' }} />
                <div>
                  <h4>Stage 2: Business Analysis</h4>
                  <p>Tests business intelligence analysis and methodology selection.</p>
                  <div className="requirements">
                    <strong>Requirements:</strong> Provide extracted data JSON from Stage 1
                  </div>
                </div>
              </div>

              <div className="mode-guide-card">
                <TrendingUp size={20} style={{ color: 'var(--success)' }} />
                <div>
                  <h4>Stage 3: Projection Engine</h4>
                  <p>Tests financial projection generation and scenario planning.</p>
                  <div className="requirements">
                    <strong>Requirements:</strong> Provide business analysis JSON from Stage 2
                  </div>
                </div>
              </div>

              <div className="mode-guide-card">
                <Layers size={20} style={{ color: 'var(--warning)' }} />
                <div>
                  <h4>Full Process</h4>
                  <p>Tests the complete 3-stage pipeline with detailed timing.</p>
                  <div className="requirements">
                    <strong>Requirements:</strong> Upload 1-10 PDF or CSV files
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="guide-section">
            <h3>How to Use</h3>
            
            <div className="steps-guide">
              <div className="step-guide">
                <div className="step-number">1</div>
                <div>
                  <h4>Configure Settings</h4>
                  <p>Select your AI model and upload test files or provide JSON data as needed.</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">2</div>
                <div>
                  <h4>Run Individual Tests</h4>
                  <p>Click on any test mode to run individual service tests and see detailed results.</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">3</div>
                <div>
                  <h4>Monitor Results</h4>
                  <p>View processing times, success rates, and detailed output for each stage.</p>
                </div>
              </div>

              <div className="step-guide">
                <div className="step-number">4</div>
                <div>
                  <h4>Chain Testing</h4>
                  <p>Use Stage 1 output as Stage 2 input, and Stage 2 output as Stage 3 input for complete testing.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="guide-section">
            <h3>System Health Monitoring</h3>
            <p>
              The dashboard provides real-time health monitoring for all services:
            </p>
            <ul className="health-features">
              <li><CheckCircle size={16} style={{ color: 'var(--success)' }} /> Service availability and response times</li>
              <li><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> Error detection and reporting</li>
              <li><Info size={16} style={{ color: 'var(--primary)' }} /> Performance metrics and timing analysis</li>
            </ul>
          </section>

          <section className="guide-section">
            <h3>Tips for Effective Testing</h3>
            <div className="tips-grid">
              <div className="tip-card">
                <h4>Start with Stage 1</h4>
                <p>Always test OCR extraction first to ensure your input data is properly processed.</p>
              </div>
              <div className="tip-card">
                <h4>Use Real Data</h4>
                <p>Test with actual financial documents (P&L, Balance Sheets) for realistic results.</p>
              </div>
              <div className="tip-card">
                <h4>Check Performance</h4>
                <p>Monitor processing times to identify bottlenecks in your pipeline.</p>
              </div>
              <div className="tip-card">
                <h4>Download Results</h4>
                <p>Save test results for documentation and comparison across different models.</p>
              </div>
            </div>
          </section>
        </div>

        <div className="guide-footer">
          <button onClick={onClose} className="close-guide-btn">
            Got it, let's test!
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default TestingGuide 