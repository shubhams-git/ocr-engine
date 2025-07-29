import React from 'react';

const KeyMetrics = ({ workingCapital }) => {
  return (
    <div className="key-metrics">
      <h3>Key Metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>DSO</h4>
          <p>{workingCapital.calculated_dso.historical_average}</p>
        </div>
        <div className="metric-card">
          <h4>DPO</h4>
          <p>{workingCapital.calculated_dpo.historical_average}</p>
        </div>
        <div className="metric-card">
          <h4>Cash Conversion Cycle</h4>
          <p>{workingCapital.cash_conversion_cycle.historical_average}</p>
        </div>
      </div>
    </div>
  );
};

export default KeyMetrics;