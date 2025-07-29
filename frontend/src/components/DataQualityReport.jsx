import React from 'react';
import AnomaliesList from './AnomaliesList';
import QualityFlags from './QualityFlags';

const DataQualityReport = ({ qualityAssessment, fieldCoverage }) => {
  return (
    <div className="data-quality-report card">
      <h2>Data Quality Report</h2>
      <p>Completeness Score: {qualityAssessment.completeness_score * 100}%</p>
      <p>Coverage: {fieldCoverage.total_standard_fields_found}</p>
      <div className="coverage-bar">
        <div 
          className="coverage-fill" 
          style={{ width: fieldCoverage.coverage_percentage }}
        ></div>
      </div>
      <AnomaliesList anomalies={qualityAssessment.anomalies_detected} />
      <QualityFlags flags={qualityAssessment.quality_flags} />
    </div>
  );
};

export default DataQualityReport;