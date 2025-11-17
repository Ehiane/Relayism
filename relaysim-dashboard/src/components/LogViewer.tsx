/**
 * LogViewer component
 *
 * Displays test execution logs with timestamps and step details.
 */

import React from 'react';
import type { RunResult } from '../types';
import './LogViewer.css';

interface LogViewerProps {
  runResult: RunResult | null;
}

const LogViewer: React.FC<LogViewerProps> = ({ runResult }) => {
  if (!runResult) {
    return (
      <div className="log-viewer">
        <h2>Execution Log</h2>
        <div className="log-empty">
          <p>No logs available. Run a scenario to see execution details.</p>
        </div>
      </div>
    );
  }

  const formatTimestamp = (datetime: string): string => {
    try {
      const date = new Date(datetime);
      return date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3,
      });
    } catch {
      return datetime;
    }
  };

  const getLogLevel = (step: any): string => {
    if (step.status === 'pass') return 'INFO';
    if (step.status === 'fail') return 'ERROR';
    return 'WARN';
  };

  const getLogClass = (step: any): string => {
    if (step.status === 'pass') return 'log-entry log-info';
    if (step.status === 'fail') return 'log-entry log-error';
    return 'log-entry log-warn';
  };

  return (
    <div className="log-viewer">
      <h2>Execution Log</h2>

      <div className="log-header">
        <div className="log-metadata">
          <span>
            <strong>Scenario:</strong> {runResult.scenario_name}
          </span>
          <span>
            <strong>Started:</strong> {formatTimestamp(runResult.start_datetime)}
          </span>
          <span>
            <strong>Duration:</strong> {runResult.duration_seconds.toFixed(3)}s
          </span>
          <span>
            <strong>Status:</strong>{' '}
            <span className={`status-badge status-${runResult.overall_status}`}>
              {runResult.overall_status.toUpperCase()}
            </span>
          </span>
        </div>
      </div>

      <div className="log-container">
        {runResult.step_results.map((step, index) => {
          // Calculate approximate timestamp for each step
          const stepTime = new Date(
            new Date(runResult.start_datetime).getTime() +
              runResult.step_results
                .slice(0, index)
                .reduce((sum, s) => sum + s.duration_ms, 0)
          );

          return (
            <div key={step.step_number} className={getLogClass(step)}>
              <div className="log-timestamp">
                {stepTime.toLocaleTimeString('en-US', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                  fractionalSecondDigits: 3,
                })}
              </div>
              <div className="log-level">{getLogLevel(step)}</div>
              <div className="log-message">
                <div className="log-main">
                  Step {step.step_number}: {step.step_type.toUpperCase()} -{' '}
                  {step.message}
                </div>
                {step.status !== 'pass' && step.details && (
                  <div className="log-details">
                    {JSON.stringify(step.details, null, 2)}
                  </div>
                )}
                <div className="log-duration">{step.duration_ms.toFixed(1)}ms</div>
              </div>
            </div>
          );
        })}

        <div className="log-entry log-summary">
          <div className="log-timestamp">
            {runResult.end_datetime && formatTimestamp(runResult.end_datetime)}
          </div>
          <div className="log-level">INFO</div>
          <div className="log-message">
            <strong>
              Scenario completed: {runResult.overall_status.toUpperCase()}
            </strong>{' '}
            ({runResult.passed_steps}/{runResult.total_steps} steps passed)
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogViewer;
