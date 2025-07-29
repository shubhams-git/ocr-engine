import React from 'react';

const PatternAnalysis = ({ patternAnalysis }) => {
  return (
    <div className="pattern-analysis">
      <h3>Pattern Analysis</h3>
      <p>Revenue CAGR: {patternAnalysis.growth_rates.revenue_cagr}%</p>
      <p>Profit CAGR: {patternAnalysis.growth_rates.profit_cagr}%</p>
      <p>Recent Growth Trend: {patternAnalysis.growth_rates.recent_growth_trend}</p>
      <h4>Correlations</h4>
      <ul>
        {patternAnalysis.correlation_insights.map((insight, index) => (
          <li key={index}>
            <strong>{insight.metrics.join(' & ')}:</strong> {insight.business_meaning} (Correlation: {insight.correlation})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PatternAnalysis;