/**
 * RunStatusPanel component
 *
 * Displays the current run status with visual indicators.
 */

import React from 'react';
import type { RunResult } from '../types';
import './RunStatusPanel.css';

interface RunStatusPanelProps {
  runResult: RunResult | null;
  isRunning: boolean;
}

const RunStatusPanel: React.FC<RunStatusPanelProps> = ({ runResult, isRunning }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'passed':
        return 'status-passed';
      case 'failed':
        return 'status-failed';
      case 'error':
        return 'status-error';
      case 'running':
        return 'status-running';
      default:
        return 'status-idle';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'passed':
        return '✓';
      case 'failed':
        return '✗';
      case 'error':
        return '⚠';
      case 'running':
        return '⋯';
      default:
        return '○';
    }
  };

  const currentStatus = isRunning
    ? 'running'
    : runResult?.overall_status || 'idle';

  return (
    <div className="run-status-panel">
      <h2>Run Status</h2>
      <div className={`status-indicator ${getStatusColor(currentStatus)}`}>
        <div className="status-icon">{getStatusIcon(currentStatus)}</div>
        <div className="status-text">{currentStatus.toUpperCase()}</div>
      </div>

      {runResult && (
        <div className="run-details">
          <div className="run-detail-row">
            <span className="label">Scenario:</span>
            <span className="value">{runResult.scenario_name}</span>
          </div>

          {runResult.description && (
            <div className="run-detail-row">
              <span className="label">Description:</span>
              <span className="value">{runResult.description}</span>
            </div>
          )}

          <div className="run-detail-row">
            <span className="label">Duration:</span>
            <span className="value">{runResult.duration_seconds.toFixed(3)}s</span>
          </div>

          <div className="run-detail-row">
            <span className="label">Steps:</span>
            <span className="value">
              {runResult.passed_steps} / {runResult.total_steps} passed
            </span>
          </div>

          {runResult.failed_steps > 0 && (
            <div className="run-detail-row">
              <span className="label">Failed:</span>
              <span className="value error-text">{runResult.failed_steps}</span>
            </div>
          )}

          {runResult.error_message && (
            <div className="error-message">
              <strong>Error:</strong> {runResult.error_message}
            </div>
          )}

          <div className="step-summary">
            {runResult.step_results.map((step) => (
              <div
                key={step.step_number}
                className={`step-indicator step-${step.status}`}
                title={`Step ${step.step_number}: ${step.step_type} - ${step.status}`}
              />
            ))}
          </div>
        </div>
      )}

      {!runResult && !isRunning && (
        <div className="no-run-message">
          <p>No scenario has been run yet.</p>
          <p>Select a scenario from the list to begin.</p>
        </div>
      )}
    </div>
  );
};

export default RunStatusPanel;
