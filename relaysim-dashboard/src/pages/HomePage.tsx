/**
 * HomePage component
 *
 * Main page that orchestrates all components and handles state.
 */

import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { ScenarioInfo, RunResult } from '../types';
import ScenarioList from '../components/ScenarioList';
import RunStatusPanel from '../components/RunStatusPanel';
import DeviceStateVisualizer from '../components/DeviceStateVisualizer';
import LogViewer from '../components/LogViewer';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [currentRun, setCurrentRun] = useState<RunResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load scenarios on mount
  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      setError(`Failed to load scenarios: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScenario = async (scenarioName: string) => {
    try {
      setIsRunning(true);
      setError(null);

      const result = await api.runScenario(scenarioName);
      setCurrentRun(result);
    } catch (err) {
      setError(`Failed to run scenario: ${(err as Error).message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="home-page">
      <header className="page-header">
        <h1>Relaysim Dashboard</h1>
        <p className="subtitle">Automated Firmware Test Harness</p>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
          <button className="close-button" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading scenarios...</p>
        </div>
      ) : (
        <>
          <div className="dashboard-grid">
            <div className="dashboard-left">
              <ScenarioList
                scenarios={scenarios}
                onRunScenario={handleRunScenario}
                isRunning={isRunning}
              />
            </div>

            <div className="dashboard-right">
              <RunStatusPanel runResult={currentRun} isRunning={isRunning} />
              <DeviceStateVisualizer
                runResult={currentRun}
                isRunning={isRunning}
              />
            </div>
          </div>

          <div className="dashboard-logs">
            <LogViewer runResult={currentRun} />
          </div>
        </>
      )}
    </div>
  );
};

export default HomePage;
