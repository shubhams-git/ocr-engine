import React from 'react';
import KeyMetrics from './KeyMetrics';
import PatternAnalysis from './PatternAnalysis';

const AnalysisInsights = ({ normalizedData }) => {
  if (!normalizedData) {
    return <div>Loading analysis insights...</div>;
  }

  return (
    <div className="analysis-insights card">
      <h2>Analysis Insights</h2>
      <KeyMetrics workingCapital={normalizedData.cash_flow_integration_analysis.working_capital_analysis} />
      <PatternAnalysis patternAnalysis={normalizedData.pattern_analysis} />
    </div>
  );
};

export default AnalysisInsights;