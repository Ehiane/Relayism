/**
 * ScenarioList component
 *
 * Displays available test scenarios in a grid layout.
 * Each scenario can be triggered via a "Run" button.
 */

import React from 'react';
import type { ScenarioInfo } from '../types';
import './ScenarioList.css';

interface ScenarioListProps {
  scenarios: ScenarioInfo[];
  onRunScenario: (scenarioName: string) => void;
  isRunning: boolean;
}

const ScenarioList: React.FC<ScenarioListProps> = ({
  scenarios,
  onRunScenario,
  isRunning,
}) => {
  if (scenarios.length === 0) {
    return (
      <div className="scenario-list-empty">
        <p>No scenarios available</p>
      </div>
    );
  }

  return (
    <div className="scenario-list">
      <h2>Available Test Scenarios</h2>
      <div className="scenario-grid">
        {scenarios.map((scenario) => (
          <div key={scenario.filename} className="scenario-card">
            <div className="scenario-card-header">
              <h3>{scenario.name}</h3>
            </div>
            <div className="scenario-card-body">
              <p className="scenario-description">
                {scenario.description || 'No description available'}
              </p>
              <p className="scenario-filename">{scenario.filename}</p>
            </div>
            <div className="scenario-card-footer">
              <button
                className="run-button"
                onClick={() => onRunScenario(scenario.filename.replace('.yaml', ''))}
                disabled={isRunning}
              >
                {isRunning ? 'Running...' : 'Run'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScenarioList;
