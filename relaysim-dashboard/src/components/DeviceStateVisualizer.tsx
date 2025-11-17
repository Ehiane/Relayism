/**
 * DeviceStateVisualizer component
 *
 * Visualizes the device state machine (IDLE, ACTIVE, FAULT) with animations.
 */

import React from 'react';
import type { DeviceState, RunResult } from '../types';
import './DeviceStateVisualizer.css';

interface DeviceStateVisualizerProps {
  runResult: RunResult | null;
  isRunning: boolean;
}

const DeviceStateVisualizer: React.FC<DeviceStateVisualizerProps> = ({
  runResult,
  isRunning,
}) => {
  // Extract state transitions from step results
  const getStateTransitions = (): DeviceState[] => {
    if (!runResult) return ['IDLE'];

    const states: DeviceState[] = ['IDLE'];

    for (const step of runResult.step_results) {
      if (step.step_type === 'command') {
        if (step.details.action === 'activate') {
          states.push('ACTIVE');
        } else if (step.details.action === 'reset') {
          states.push('IDLE');
        } else if (step.details.action === 'inject_fault') {
          states.push('FAULT');
        }
      }
    }

    return states;
  };

  const getCurrentState = (): DeviceState => {
    const transitions = getStateTransitions();
    return transitions[transitions.length - 1];
  };

  const currentState = getCurrentState();

  const getStateClass = (state: DeviceState): string => {
    if (state === currentState) {
      return 'state-box active';
    }
    return 'state-box';
  };

  const getStateColor = (state: DeviceState): string => {
    switch (state) {
      case 'IDLE':
        return 'state-idle';
      case 'ACTIVE':
        return 'state-active';
      case 'FAULT':
        return 'state-fault';
      default:
        return '';
    }
  };

  return (
    <div className="device-state-visualizer">
      <h2>Device State Machine</h2>

      <div className="state-diagram">
        <div className={`${getStateClass('IDLE')} ${getStateColor('IDLE')}`}>
          <div className="state-label">IDLE</div>
          <div className="state-description">Ready</div>
        </div>

        <div className="state-arrow">→</div>

        <div className={`${getStateClass('ACTIVE')} ${getStateColor('ACTIVE')}`}>
          <div className="state-label">ACTIVE</div>
          <div className="state-description">Operating</div>
        </div>

        <div className="state-arrow">→</div>

        <div className={`${getStateClass('FAULT')} ${getStateColor('FAULT')}`}>
          <div className="state-label">FAULT</div>
          <div className="state-description">Error</div>
        </div>
      </div>

      <div className="current-state-info">
        <div className="info-label">Current State:</div>
        <div className={`info-value ${getStateColor(currentState)}`}>
          {currentState}
        </div>
      </div>

      {runResult && (
        <div className="state-timeline">
          <h3>State Transitions</h3>
          <div className="timeline">
            {getStateTransitions().map((state, index) => (
              <div key={index} className="timeline-item">
                <div className={`timeline-dot ${getStateColor(state)}`} />
                <div className="timeline-label">{state}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DeviceStateVisualizer;
