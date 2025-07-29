import React, { useState, useMemo } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Calendar,
  BarChart3,
  AlertCircle,
  CheckCircle,
  FileText,
  Database,
  Target,
  Activity,
  Eye,
  Download,
  Filter,
  Search,
  ChevronRight,
  ChevronDown,
  Info,
  TrendingDown,
  Minus
} from 'lucide-react';

const EnhancedResultsDashboard = ({ data }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSections, setExpandedSections] = useState({
    businessIntelligence: true,
    cashFlow: true,
    projections: true,
    analysis: true
  });

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading analysis results...</div>
      </div>
    );
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Extract key data from the response
  const businessContext = data.normalized_data?.business_context || {};
  const cashFlowData = data.normalized_data?.cash_flow_generation_results || {};
  const analysis = data.normalized_data?.contextual_analysis || {};
  const projections = data.projections || {};
  const methodology = data.normalized_data?.methodology_evaluation || {};
  
  // Format currency
  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value) => {
    if (!value && value !== 0) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  // Calculate trend icon and color
  const getTrendInfo = (value) => {
    if (!value || value === 0) return { icon: Minus, color: 'text-gray-500' };
    if (value > 0) return { icon: TrendingUp, color: 'text-green-600' };
    return { icon: TrendingDown, color: 'text-red-600' };
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Business Stage"
          value={businessContext.business_stage || 'Growth'}
          icon={Activity}
          color="bg-blue-500"
        />
        <MetricCard
          title="Industry"
          value={businessContext.industry || 'Construction - Plumbing'}
          icon={Database}
          color="bg-purple-500"
        />
        <MetricCard
          title="Forecast Method"
          value={methodology.selected_method || 'Driver-Based'}
          icon={Target}
          color="bg-green-500"
        />
        <MetricCard
          title="Confidence Score"
          value={formatPercentage(methodology.confidence_score || 0.85)}
          icon={CheckCircle}
          color="bg-orange-500"
        />
      </div>

      {/* Business Intelligence Section */}
      <CollapsibleSection
        title="Business Intelligence & Context"
        icon={Activity}
        expanded={expandedSections.businessIntelligence}
        onToggle={() => toggleSection('businessIntelligence')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Key Characteristics</h4>
            <ul className="space-y-2">
              {businessContext.key_characteristics?.map((char, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-600">{char}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Critical Success Factors</h4>
            <ul className="space-y-2">
              {businessContext.critical_factors?.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-600">{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CollapsibleSection>

      {/* Cash Flow Analysis Section */}
      <CollapsibleSection
        title="Cash Flow Analysis"
        icon={DollarSign}
        expanded={expandedSections.cashFlow}
        onToggle={() => toggleSection('cashFlow')}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CashFlowMetric
              label="Operating Cash Flow Trend"
              value={analysis.cash_flow_trends?.operating_trend || 'Improving'}
              trend={0.12}
            />
            <CashFlowMetric
              label="Working Capital Efficiency"
              value={analysis.working_capital_efficiency || 'Moderate'}
              trend={-0.05}
            />
            <CashFlowMetric
              label="Cash Conversion Cycle"
              value={`${analysis.cash_conversion_cycle || 45} days`}
              trend={-0.08}
            />
          </div>
          
          {/* Pattern Recognition */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-semibold text-gray-700 mb-2">Identified Patterns</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysis.pattern_insights?.map((pattern, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-600">{pattern}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );

  const renderProjectionsTab = () => (
    <div className="space-y-6">
      <CollapsibleSection
        title="Financial Projections"
        icon={TrendingUp}
        expanded={expandedSections.projections}
        onToggle={() => toggleSection('projections')}
      >
        <div className="space-y-6">
          {/* Projection Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(projections).map(([period, metrics]) => (
              <ProjectionCard
                key={period}
                period={period}
                metrics={metrics}
                formatCurrency={formatCurrency}
              />
            ))}
          </div>

          {/* Scenario Analysis */}
          {projections.scenarios && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-700 mb-4">Scenario Analysis</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(projections.scenarios).map(([scenario, data]) => (
                  <ScenarioCard
                    key={scenario}
                    scenario={scenario}
                    data={data}
                    formatCurrency={formatCurrency}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </CollapsibleSection>
    </div>
  );

  const renderAnalysisTab = () => (
    <div className="space-y-6">
      <CollapsibleSection
        title="Comprehensive Analysis"
        icon={BarChart3}
        expanded={expandedSections.analysis}
        onToggle={() => toggleSection('analysis')}
      >
        <div className="space-y-6">
          {/* Risk Assessment */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-4">Risk Assessment</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.risk_factors?.map((risk, idx) => (
                <RiskCard key={idx} risk={risk} index={idx} />
              ))}
            </div>
          </div>

          {/* Key Insights */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-4">Key Insights</h4>
            <div className="space-y-3">
              {data.normalized_data?.key_insights_summary?.map((insight, idx) => (
                <InsightCard key={idx} insight={insight} index={idx} />
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-4">Strategic Recommendations</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.recommendations?.map((rec, idx) => (
                <RecommendationCard key={idx} recommendation={rec} index={idx} />
              ))}
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Financial Analysis Results
        </h2>
        <p className="text-gray-600">
          Comprehensive analysis for {businessContext.company_name || 'MJV Plumbing Services'}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          <TabButton
            active={activeTab === 'overview'}
            onClick={() => setActiveTab('overview')}
            icon={Eye}
            label="Overview"
          />
          <TabButton
            active={activeTab === 'projections'}
            onClick={() => setActiveTab('projections')}
            icon={TrendingUp}
            label="Projections"
          />
          <TabButton
            active={activeTab === 'analysis'}
            onClick={() => setActiveTab('analysis')}
            icon={BarChart3}
            label="Analysis"
          />
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'projections' && renderProjectionsTab()}
          {activeTab === 'analysis' && renderAnalysisTab()}
        </div>
      </div>

      {/* Export Actions */}
      <div className="mt-6 flex justify-end space-x-4">
        <button className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
        <button className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Export Excel
        </button>
      </div>
    </div>
  );
};

// Component Parts
const TabButton = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`
      pb-4 px-1 border-b-2 font-medium text-sm transition-colors
      flex items-center gap-2
      ${active 
        ? 'border-blue-500 text-blue-600' 
        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      }
    `}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
);

const MetricCard = ({ title, value, icon: Icon, color }) => (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-lg font-semibold text-gray-800 mt-1">{value}</p>
      </div>
      <div className={`${color} bg-opacity-10 p-2 rounded-lg`}>
        <Icon className={`w-5 h-5 ${color.replace('bg-', 'text-')}`} />
      </div>
    </div>
  </div>
);

const CollapsibleSection = ({ title, icon: Icon, expanded, onToggle, children }) => (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200">
    <button
      onClick={onToggle}
      className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5 text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      </div>
      {expanded ? (
        <ChevronDown className="w-5 h-5 text-gray-400" />
      ) : (
        <ChevronRight className="w-5 h-5 text-gray-400" />
      )}
    </button>
    {expanded && (
      <div className="px-6 pb-6 border-t border-gray-100">
        <div className="pt-4">
          {children}
        </div>
      </div>
    )}
  </div>
);

const CashFlowMetric = ({ label, value, trend }) => {
  const { icon: TrendIcon, color } = getTrendInfo(trend);
  
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <div className="flex items-center justify-between">
        <p className="font-semibold text-gray-800">{value}</p>
        <div className={`flex items-center gap-1 ${color}`}>
          <TrendIcon className="w-4 h-4" />
          <span className="text-sm font-medium">{Math.abs(trend * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};

const ProjectionCard = ({ period, metrics, formatCurrency }) => {
  const periodLabel = period.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
  
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h5 className="font-semibold text-gray-700 mb-3 capitalize">{periodLabel}</h5>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Revenue</span>
          <span className="text-sm font-medium">{formatCurrency(metrics.revenue)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Expenses</span>
          <span className="text-sm font-medium">{formatCurrency(metrics.expenses)}</span>
        </div>
        <div className="flex justify-between pt-2 border-t border-gray-200">
          <span className="text-sm font-medium text-gray-700">Net Profit</span>
          <span className="text-sm font-semibold text-green-600">
            {formatCurrency(metrics.net_profit)}
          </span>
        </div>
      </div>
    </div>
  );
};

const ScenarioCard = ({ scenario, data, formatCurrency }) => {
  const scenarioColors = {
    base: 'blue',
    optimistic: 'green',
    pessimistic: 'red'
  };
  const color = scenarioColors[scenario] || 'gray';
  
  return (
    <div className={`bg-${color}-50 rounded-lg p-4 border border-${color}-200`}>
      <h5 className={`font-semibold text-${color}-700 mb-3 capitalize`}>{scenario} Case</h5>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Revenue Growth</span>
          <span className={`text-sm font-medium text-${color}-600`}>
            {data.revenue_growth}%
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Profit Margin</span>
          <span className={`text-sm font-medium text-${color}-600`}>
            {data.profit_margin}%
          </span>
        </div>
      </div>
    </div>
  );
};

const RiskCard = ({ risk, index }) => (
  <div className="bg-red-50 rounded-lg p-4 border border-red-200">
    <div className="flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
      <div>
        <h5 className="font-medium text-red-700 mb-1">Risk #{index + 1}</h5>
        <p className="text-sm text-gray-600">{risk}</p>
      </div>
    </div>
  </div>
);

const InsightCard = ({ insight, index }) => (
  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
    <div className="flex items-start gap-3">
      <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
      <p className="text-sm text-gray-700">{insight}</p>
    </div>
  </div>
);

const RecommendationCard = ({ recommendation, index }) => (
  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
    <div className="flex items-start gap-3">
      <Target className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
      <div>
        <h5 className="font-medium text-green-700 mb-1">Action #{index + 1}</h5>
        <p className="text-sm text-gray-600">{recommendation}</p>
      </div>
    </div>
  </div>
);

export default EnhancedResultsDashboard;