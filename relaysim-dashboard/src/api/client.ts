/**
 * API client for Relaysim backend
 */

import type { ScenarioInfo, RunResult, DeviceStatus } from '../types';

const API_BASE_URL = 'http://localhost:8000';

class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new APIError(
        `API request failed: ${response.statusText}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${(error as Error).message}`);
  }
}

export const api = {
  /**
   * Get list of available scenarios
   */
  async getScenarios(): Promise<ScenarioInfo[]> {
    return fetchJSON<ScenarioInfo[]>('/api/scenarios');
  },

  /**
   * Run a scenario
   */
  async runScenario(scenarioName: string): Promise<RunResult> {
    return fetchJSON<RunResult>('/api/run', {
      method: 'POST',
      body: JSON.stringify({ scenario: scenarioName }),
    });
  },

  /**
   * Get all run results
   */
  async getAllRuns(): Promise<RunResult[]> {
    return fetchJSON<RunResult[]>('/api/runs');
  },

  /**
   * Get a specific run result by ID
   */
  async getRun(runId: string): Promise<RunResult> {
    return fetchJSON<RunResult>(`/api/runs/${runId}`);
  },

  /**
   * Delete a run result
   */
  async deleteRun(runId: string): Promise<void> {
    await fetchJSON(`/api/runs/${runId}`, { method: 'DELETE' });
  },

  /**
   * Clear all run results
   */
  async clearAllRuns(): Promise<void> {
    await fetchJSON('/api/runs', { method: 'DELETE' });
  },

  /**
   * Get current device status
   */
  async getDeviceStatus(): Promise<DeviceStatus> {
    return fetchJSON<DeviceStatus>('/api/device/status');
  },
};

export { APIError };
