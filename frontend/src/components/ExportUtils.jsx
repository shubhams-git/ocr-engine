import { useState } from 'react'
import { motion } from 'framer-motion'
import { Download, FileText, FileSpreadsheet, FileDown, Printer, Share2 } from 'lucide-react'
import jsPDF from 'jspdf'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'

const ExportUtils = ({ data, fileName, contentRef, chartRefs = [] }) => {
  const [isExporting, setIsExporting] = useState(false)
  const [exportType, setExportType] = useState(null)

  // Format currency for exports
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

  // Export to PDF with charts
  const exportToPDF = async () => {
    setIsExporting(true)
    setExportType('pdf')

    try {
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      let yPosition = 20

      // Add title
      pdf.setFontSize(20)
      pdf.setFont('helvetica', 'bold')
      pdf.text(fileName || 'Financial Analysis Report', pageWidth / 2, yPosition, { align: 'center' })
      yPosition += 20

      // Add timestamp
      pdf.setFontSize(10)
      pdf.setFont('helvetica', 'normal')
      pdf.text(`Generated on: ${new Date().toLocaleString()}`, pageWidth / 2, yPosition, { align: 'center' })
      yPosition += 20

      // Capture main content
      if (contentRef?.current) {
        const canvas = await html2canvas(contentRef.current, {
          scale: 2,
          useCORS: true,
          allowTaint: true
        })
        
        const imgData = canvas.toDataURL('image/png')
        const imgWidth = pageWidth - 20
        const imgHeight = (canvas.height * imgWidth) / canvas.width
        
        // Add content with page breaks if needed
        let remainingHeight = imgHeight
        let sourceY = 0
        
        while (remainingHeight > 0) {
          const pageSpace = pageHeight - yPosition - 20
          const sliceHeight = Math.min(remainingHeight, pageSpace)
          
          if (sliceHeight > 0) {
            pdf.addImage(
              imgData,
              'PNG',
              10,
              yPosition,
              imgWidth,
              sliceHeight,
              undefined,
              'FAST',
              0,
              sourceY
            )
          }
          
          remainingHeight -= sliceHeight
          sourceY += sliceHeight
          
          if (remainingHeight > 0) {
            pdf.addPage()
            yPosition = 20
          }
        }
      }

      // Add charts if available
      for (let i = 0; i < chartRefs.length; i++) {
        const chartRef = chartRefs[i]
        if (chartRef?.current) {
          pdf.addPage()
          yPosition = 20
          
          const chartCanvas = await html2canvas(chartRef.current, {
            scale: 2,
            backgroundColor: 'white'
          })
          
          const chartImgData = chartCanvas.toDataURL('image/png')
          const chartImgWidth = pageWidth - 20
          const chartImgHeight = (chartCanvas.height * chartImgWidth) / chartCanvas.width
          
          pdf.addImage(chartImgData, 'PNG', 10, yPosition, chartImgWidth, chartImgHeight)
        }
      }

      pdf.save(`${fileName || 'financial_analysis'}.pdf`)
    } catch (error) {
      console.error('PDF export failed:', error)
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setIsExporting(false)
      setExportType(null)
    }
  }

  // Export to Excel
  const exportToExcel = () => {
    setIsExporting(true)
    setExportType('excel')

    try {
      const wb = XLSX.utils.book_new()
      
      // Process different data types
      if (data.projections) {
        // Financial projections sheet
        const projectionsData = []
        Object.entries(data.projections.base_case_projections || data.projections.specific_projections || {}).forEach(([period, periodData]) => {
          if (Array.isArray(periodData.revenue)) {
            periodData.revenue.forEach(item => {
              projectionsData.push({
                Period: period,
                Date: item.period,
                Metric: 'Revenue',
                Value: item.value,
                Confidence: item.confidence || 'N/A'
              })
            })
          }
          if (Array.isArray(periodData.net_profit)) {
            periodData.net_profit.forEach(item => {
              projectionsData.push({
                Period: period,
                Date: item.period,
                Metric: 'Net Profit',
                Value: item.value,
                Confidence: item.confidence || 'N/A'
              })
            })
          }
        })
        
        if (projectionsData.length > 0) {
          const ws = XLSX.utils.json_to_sheet(projectionsData)
          XLSX.utils.book_append_sheet(wb, ws, 'Projections')
        }
      }

      // Normalized data sheet
      if (data.normalized_data?.time_series) {
        const timeSeriesData = []
        Object.entries(data.normalized_data.time_series).forEach(([metric, series]) => {
          if (Array.isArray(series)) {
            series.forEach(point => {
              timeSeriesData.push({
                Metric: metric,
                Period: point.period,
                Value: point.value,
                Source: point.data_source || 'N/A'
              })
            })
          }
        })
        
        if (timeSeriesData.length > 0) {
          const ws = XLSX.utils.json_to_sheet(timeSeriesData)
          XLSX.utils.book_append_sheet(wb, ws, 'Time Series')
        }
      }

      // Summary sheet
      const summaryData = [
        { Item: 'Analysis Date', Value: new Date().toLocaleDateString() },
        { Item: 'Files Analyzed', Value: data.files_analyzed?.length || 1 },
        { Item: 'Data Quality Score', Value: data.data_quality_score ? `${(data.data_quality_score * 100).toFixed(1)}%` : 'N/A' },
        { Item: 'Architecture Type', Value: data.data_analysis_summary?.architecture_type || 'Standard' }
      ]
      
      const summaryWs = XLSX.utils.json_to_sheet(summaryData)
      XLSX.utils.book_append_sheet(wb, summaryWs, 'Summary')

      XLSX.writeFile(wb, `${fileName || 'financial_analysis'}.xlsx`)
    } catch (error) {
      console.error('Excel export failed:', error)
      alert('Failed to generate Excel file. Please try again.')
    } finally {
      setIsExporting(false)
      setExportType(null)
    }
  }

  // Export to CSV
  const exportToCSV = () => {
    setIsExporting(true)
    setExportType('csv')

    try {
      let csvContent = 'data:text/csv;charset=utf-8,'
      
      // Add header
      csvContent += `Financial Analysis Report\n`
      csvContent += `Generated: ${new Date().toLocaleString()}\n\n`
      
      // Add projections data
      if (data.projections) {
        csvContent += 'Financial Projections\n'
        csvContent += 'Period,Date,Metric,Value,Confidence\n'
        
        Object.entries(data.projections.base_case_projections || data.projections.specific_projections || {}).forEach(([period, periodData]) => {
          if (Array.isArray(periodData.revenue)) {
            periodData.revenue.forEach(item => {
              csvContent += `${period},${item.period},Revenue,${item.value},${item.confidence || 'N/A'}\n`
            })
          }
          if (Array.isArray(periodData.net_profit)) {
            periodData.net_profit.forEach(item => {
              csvContent += `${period},${item.period},Net Profit,${item.value},${item.confidence || 'N/A'}\n`
            })
          }
        })
      }

      const encodedUri = encodeURI(csvContent)
      const link = document.createElement('a')
      link.setAttribute('href', encodedUri)
      link.setAttribute('download', `${fileName || 'financial_analysis'}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('CSV export failed:', error)
      alert('Failed to generate CSV file. Please try again.')
    } finally {
      setIsExporting(false)
      setExportType(null)
    }
  }

  // Print functionality
  const handlePrint = () => {
    window.print()
  }

  // Share functionality
  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Financial Analysis Report',
          text: 'Check out this financial analysis report',
          url: window.location.href
        })
      } catch (error) {
        console.error('Sharing failed:', error)
      }
    } else {
      // Fallback to copying URL
      await navigator.clipboard.writeText(window.location.href)
      alert('Report URL copied to clipboard!')
    }
  }

  return (
    <div className="export-utils">
      <div className="export-buttons">
        <motion.button
          onClick={exportToPDF}
          disabled={isExporting}
          className={`export-button pdf-button ${isExporting && exportType === 'pdf' ? 'exporting' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FileText size={18} />
          {isExporting && exportType === 'pdf' ? 'Generating PDF...' : 'Export PDF'}
        </motion.button>

        <motion.button
          onClick={exportToExcel}
          disabled={isExporting}
          className={`export-button excel-button ${isExporting && exportType === 'excel' ? 'exporting' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FileSpreadsheet size={18} />
          {isExporting && exportType === 'excel' ? 'Generating Excel...' : 'Export Excel'}
        </motion.button>

        <motion.button
          onClick={exportToCSV}
          disabled={isExporting}
          className={`export-button csv-button ${isExporting && exportType === 'csv' ? 'exporting' : ''}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FileDown size={18} />
          {isExporting && exportType === 'csv' ? 'Generating CSV...' : 'Export CSV'}
        </motion.button>

        <motion.button
          onClick={handlePrint}
          className="export-button print-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Printer size={18} />
          Print Report
        </motion.button>

        <motion.button
          onClick={handleShare}
          className="export-button share-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Share2 size={18} />
          Share Report
        </motion.button>
      </div>

      {isExporting && (
        <div className="export-status">
          <div className="export-spinner"></div>
          <span>Preparing {exportType} export...</span>
        </div>
      )}
    </div>
  )
}

export default ExportUtils 