import React from 'react';

const ScenarioTabs = ({ scenarios, activeScenario, setActiveScenario }) => {
  return (
    <div className="scenario-tabs">
      {scenarios.map(scenario => (
        <button 
          key={scenario}
          className={activeScenario === scenario ? 'active' : ''}
          onClick={() => setActiveScenario(scenario)}
        >
          {scenario.replace('_projections', '').replace('_', ' ').toUpperCase()}
        </button>
      ))}
    </div>
  );
};

export default ScenarioTabs;