import React, { useState } from 'react';
import StatementTable from './StatementTable';
import TimeSeriesChart from './TimeSeriesChart';

const FinancialStatements = ({ statements }) => {
  const [activeTab, setActiveTab] = useState('profit_and_loss_standards');

  const statementData = statements[activeTab];

  return (
    <div className="financial-statements card">
      <h2>Financial Statements</h2>
      <div className="tabs">
        <button onClick={() => setActiveTab('profit_and_loss_standards')}>P&L</button>
        <button onClick={() => setActiveTab('balance_sheet_standards')}>Balance Sheet</button>
      </div>
      <div className="statement-content">
        <StatementTable data={statementData} />
        <TimeSeriesChart data={statementData} />
      </div>
    </div>
  );
};

export default FinancialStatements;