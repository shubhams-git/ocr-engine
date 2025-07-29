import React, { useState } from 'react';
import ProjectionChart from './ProjectionChart';
import ScenarioTabs from './ScenarioTabs';

const ProjectionsView = ({ projections }) => {
  const [activeScenario, setActiveScenario] = useState('base_case_projections');

  if (!projections) {
    return <div>Loading projections...</div>;
  }

  const scenarioData = projections[activeScenario];

  return (
    <div className="projections-view card">
      <h2>Projections</h2>
      <ScenarioTabs 
        scenarios={Object.keys(projections).filter(k => k.includes('_projections'))} 
        activeScenario={activeScenario}
        setActiveScenario={setActiveScenario}
      />
      <ProjectionChart data={scenarioData} />
    </div>
  );
};

export default ProjectionsView;