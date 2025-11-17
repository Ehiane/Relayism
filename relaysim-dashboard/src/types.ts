/**
 * TypeScript types for Relaysim API
 */

export interface ScenarioInfo {
  name: string;
  description: string;
  filename: string;
}

export interface StepResult {
  step_number: number;
  step_type: string;
  status: 'pass' | 'fail' | 'error';
  message: string;
  details: Record<string, any>;
  duration_ms: number;
}

export interface RunResult {
  run_id: string;
  scenario_name: string;
  description: string;
  start_time: number;
  start_datetime: string;
  end_time: number | null;
  end_datetime: string | null;
  duration_seconds: number;
  overall_status: 'running' | 'passed' | 'failed' | 'error';
  error_message: string | null;
  total_steps: number;
  passed_steps: number;
  failed_steps: number;
  step_results: StepResult[];
}

export interface DeviceStatus {
  state: 'IDLE' | 'ACTIVE' | 'FAULT';
  registers: Record<string, any>;
  fault_active: boolean;
  fault_type: string | null;
  log_count: number;
}

export type DeviceState = 'IDLE' | 'ACTIVE' | 'FAULT';
