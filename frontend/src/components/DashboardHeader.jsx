import React from 'react';

const DashboardHeader = ({ fileInfo }) => {
  return (
    <div className="dashboard-header">
      <h1>Financial Analysis for {fileInfo.filename}</h1>
      <p>Document Type: {fileInfo.data.document_type}</p>
    </div>
  );
};

export default DashboardHeader;