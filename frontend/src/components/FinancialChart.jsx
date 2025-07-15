import { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
} from 'chart.js'
import { Bar, Line, Doughnut } from 'react-chartjs-2'
import { TrendingUp, BarChart3, PieChart } from 'lucide-react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
)

const FinancialChart = ({ data, type = 'line', title, subtitle, height = 300 }) => {
  const chartRef = useRef(null)

  // Format currency for tooltips
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: 20
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`
          }
        }
      }
    },
    scales: type !== 'doughnut' ? {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return formatCurrency(value)
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    } : undefined,
    elements: {
      line: {
        tension: 0.4
      },
      point: {
        radius: 4,
        hoverRadius: 8
      }
    }
  }

  // Color palette
  const colors = {
    primary: '#6366f1',
    secondary: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    purple: '#8b5cf6',
    pink: '#ec4899',
    indigo: '#6366f1'
  }

  // Enhanced data processing
  const processedData = {
    ...data,
    datasets: data.datasets?.map((dataset, index) => ({
      ...dataset,
      backgroundColor: type === 'doughnut' 
        ? Object.values(colors).slice(0, dataset.data.length)
        : type === 'bar' 
          ? `${Object.values(colors)[index % Object.values(colors).length]}80`
          : `${Object.values(colors)[index % Object.values(colors).length]}20`,
      borderColor: Object.values(colors)[index % Object.values(colors).length],
      borderWidth: 2,
      fill: type === 'line' ? 'origin' : false,
      pointBackgroundColor: Object.values(colors)[index % Object.values(colors).length],
      pointBorderColor: '#fff',
      pointBorderWidth: 2
    }))
  }

  const getChartIcon = () => {
    switch (type) {
      case 'bar':
        return <BarChart3 size={16} />
      case 'doughnut':
        return <PieChart size={16} />
      default:
        return <TrendingUp size={16} />
    }
  }

  const ChartComponent = type === 'bar' ? Bar : type === 'doughnut' ? Doughnut : Line

  return (
    <div className="financial-chart">
      <div className="chart-header">
        <div className="chart-title-section">
          {getChartIcon()}
          <h4>{title}</h4>
          {subtitle && <span className="chart-subtitle">{subtitle}</span>}
        </div>
      </div>
      
      <div className="chart-container" style={{ height: `${height}px` }}>
        <ChartComponent
          ref={chartRef}
          data={processedData}
          options={options}
        />
      </div>
    </div>
  )
}

export default FinancialChart 