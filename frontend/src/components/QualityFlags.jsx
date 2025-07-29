import React from 'react';

const QualityFlags = ({ flags }) => {
  return (
    <div className="quality-flags">
      <h3>Quality Flags</h3>
      <div className="flags-container">
        {flags.map((flag, index) => (
          <span key={index} className="flag">
            {flag}
          </span>
        ))}
      </div>
    </div>
  );
};

export default QualityFlags;