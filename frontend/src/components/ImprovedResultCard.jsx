import React, { useState } from 'react';
import {
  FileText,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  Download,
  Eye,
  Code,
  BarChart3,
  TrendingUp,
  DollarSign,
  Target,
  Activity,
  Database,
  Clock
} from 'lucide-react';

const ImprovedResultCard = ({ result, index }) => {
  const [expanded, setExpanded] = useState(true);
  const [viewMode, setViewMode] = useState('dashboard'); // dashboard, raw, table

  // Extract key information from result
  const filename = result.filename || `Analysis ${index + 1}`;
  const status = result.status || 'success';
  const processingTime = result.processing_time || 0;
  const hasProjections = result.projections && Object.keys(result.projections).length > 0;
  const hasAnalysis = result.normalized_data && Object.keys(result.normalized_data).length > 0;

  // Format processing time
  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  // Render status icon
  const StatusIcon = status === 'success' ? CheckCircle : status === 'error' ? XCircle : AlertCircle;
  const statusColor = status === 'success' ? 'text-green-600' : status === 'error' ? 'text-red-600' : 'text-yellow-600';

  // Calculate metrics
  const metrics = {
    stages: result.stage_results ? Object.keys(result.stage_results).length : 5,
    projections: hasProjections ? Object.keys(result.projections).length * 4 : 0, // 4 metrics per period
    insights: result.normalized_data?.key_insights_summary?.length || 0,
    quality: result.data_quality_score || 1.0
  };

  const renderDashboardView = () => {
    if (!result.normalized_data) {
      return (
        <div className="p-8 text-center text-gray-500">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p>No analysis data available</p>
        </div>
      );
    }

    const businessContext = result.normalized_data.business_context || {};
    const methodology = result.normalized_data.methodology_evaluation || {};
    const projections = result.projections || {};

    return (
      <div className="space-y-6 p-6">
        {/* Quick Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <SummaryCard
            icon={Activity}
            label="Business Stage"
            value={businessContext.business_stage || 'N/A'}
            color="blue"
          />
          <SummaryCard
            icon={Target}
            label="Forecast Method"
            value={methodology.selected_method || 'N/A'}
            color="green"
          />
          <SummaryCard
            icon={TrendingUp}
            label="Projections"
            value={`${metrics.projections} metrics`}
            color="purple"
          />
          <SummaryCard
            icon={BarChart3}
            label="Quality Score"
            value={`${(metrics.quality * 100).toFixed(0)}%`}
            color="orange"
          />
        </div>

        {/* Key Insights */}
        {result.normalized_data.key_insights_summary && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Key Insights
            </h4>
            <ul className="space-y-2">
              {result.normalized_data.key_insights_summary.slice(0, 3).map((insight, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Projections Preview */}
        {hasProjections && (
          <div className="bg-green-50 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Financial Projections
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(projections).slice(0, 3).map(([period, data]) => (
                <div key={period} className="bg-white rounded p-3">
                  <p className="text-xs text-gray-600 mb-1">{period.replace(/_/g, ' ')}</p>
                  <p className="font-semibold text-gray-800">
                    ${(data.revenue / 1000000).toFixed(1)}M
                  </p>
                  <p className="text-xs text-gray-500">Revenue</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <button className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
            <Eye className="w-4 h-4" />
            View Full Analysis
          </button>
          <button className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>
      </div>
    );
  };

  const renderRawView = () => (
    <div className="p-6">
      <pre className="bg-gray-100 rounded-lg p-4 overflow-x-auto text-xs">
        {JSON.stringify(result, null, 2)}
      </pre>
    </div>
  );

  const renderTableView = () => {
    if (!result.extracted_data || !result.extracted_data[0]?.data?.structured_data) {
      return (
        <div className="p-8 text-center text-gray-500">
          <Database className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p>No structured data available</p>
        </div>
      );
    }

    const structuredData = result.extracted_data[0].data.structured_data;
    
    return (
      <div className="p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(structuredData).slice(0, 10).map(([key, value]) => (
                <tr key={key}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {key}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {typeof value === 'object' ? JSON.stringify(value) : value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div
        className="px-6 py-4 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="p-1 hover:bg-gray-200 rounded transition-colors">
              {expanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            </button>
            <FileText className="w-5 h-5 text-gray-600" />
            <div>
              <h3 className="font-semibold text-gray-800">{filename}</h3>
              <div className="flex items-center gap-4 mt-1">
                <span className={`flex items-center gap-1 text-sm ${statusColor}`}>
                  <StatusIcon className="w-4 h-4" />
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
                <span className="text-sm text-gray-500 flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatTime(processingTime)}
                </span>
              </div>
            </div>
          </div>
          
          {/* Metrics */}
          <div className="flex items-center gap-6">
            <MetricBadge label="Stages" value={metrics.stages} />
            <MetricBadge label="Projections" value={metrics.projections} />
            <MetricBadge label="Insights" value={metrics.insights} />
            <MetricBadge label="Quality" value={`${(metrics.quality * 100).toFixed(0)}%`} />
          </div>
        </div>
      </div>

      {/* Content */}
      {expanded && (
        <>
          {/* View Mode Tabs */}
          <div className="border-b border-gray-200 bg-gray-50">
            <div className="flex px-6">
              <ViewTab
                active={viewMode === 'dashboard'}
                onClick={() => setViewMode('dashboard')}
                icon={BarChart3}
                label="Dashboard"
              />
              <ViewTab
                active={viewMode === 'table'}
                onClick={() => setViewMode('table')}
                icon={Database}
                label="Data Table"
              />
              <ViewTab
                active={viewMode === 'raw'}
                onClick={() => setViewMode('raw')}
                icon={Code}
                label="Raw JSON"
              />
            </div>
          </div>

          {/* View Content */}
          <div className="bg-white">
            {viewMode === 'dashboard' && renderDashboardView()}
            {viewMode === 'table' && renderTableView()}
            {viewMode === 'raw' && renderRawView()}
          </div>
        </>
      )}
    </div>
  );
};

// Helper Components
const SummaryCard = ({ icon: Icon, label, value, color }) => (
  <div className="bg-gray-50 rounded-lg p-4">
    <div className="flex items-center gap-3 mb-2">
      <div className={`p-2 bg-${color}-100 rounded-lg`}>
        <Icon className={`w-4 h-4 text-${color}-600`} />
      </div>
      <p className="text-sm text-gray-600">{label}</p>
    </div>
    <p className="text-lg font-semibold text-gray-800">{value}</p>
  </div>
);

const MetricBadge = ({ label, value }) => (
  <div className="text-center">
    <p className="text-xs text-gray-500">{label}</p>
    <p className="text-sm font-semibold text-gray-800">{value}</p>
  </div>
);

const ViewTab = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`
      px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2
      ${active 
        ? 'text-blue-600 border-b-2 border-blue-600 bg-white' 
        : 'text-gray-600 hover:text-gray-800'
      }
    `}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
);

export default ImprovedResultCard;