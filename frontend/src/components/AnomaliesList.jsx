import React from 'react';

const AnomaliesList = ({ anomalies }) => {
  return (
    <div className="anomalies-list">
      <h3>Anomalies Detected</h3>
      <ul>
        {anomalies.map((anomaly, index) => (
          <li key={index}>
            <strong>{anomaly.type} on {anomaly.field}:</strong> {anomaly.description}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AnomaliesList;