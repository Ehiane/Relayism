# Relaysim: Automated Firmware Test Harness

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)

A production-quality test infrastructure system for simulating and testing firmware-controlled devices, designed with principles from safety-critical embedded systems engineering.

## Overview

**Relaysim** is a comprehensive automated test harness that:

- Simulates a firmware-controlled relay/protection device with realistic state machine behavior
- Executes YAML-based test scenarios with deterministic, reproducible results
- Provides detailed reporting and logging for test analysis
- Exposes a REST API for programmatic access and integration
- Includes a browser-based dashboard for interactive testing and visualization

This project demonstrates best practices in:
- **Test infrastructure design** for embedded/firmware systems
- **Automation** with declarative test scenarios
- **Safety-critical system thinking** with strict state validation
- **Full-stack integration** between test backend and visualization frontend

## Project Structure

```
Relayism/
├── relaysim/                  # Python backend
│   ├── simulator/             # Device simulator & state machine
│   │   ├── device.py
│   │   └── state_machine.py
│   ├── runner/                # Test scenario execution
│   │   ├── yaml_loader.py
│   │   └── test_runner.py
│   ├── api/                   # FastAPI REST endpoints
│   │   └── main.py
│   ├── reports/               # Report generation
│   │   └── generator.py
│   ├── config/                # Configuration & scenarios
│   │   └── examples/          # Example test scenarios
│   │       ├── activate.yaml
│   │       ├── fault_injection.yaml
│   │       ├── overvoltage.yaml
│   │       ├── timing_validation.yaml
│   │       └── temperature_fault.yaml
│   ├── tests/                 # PyTest test suite
│   │   ├── test_device.py
│   │   └── test_scenarios.py
│   ├── utils/                 # Utilities
│   │   └── logger.py
│   ├── pyproject.toml
│   └── requirements.txt
│
├── relaysim-dashboard/        # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ScenarioList.tsx
│   │   │   ├── RunStatusPanel.tsx
│   │   │   ├── DeviceStateVisualizer.tsx
│   │   │   └── LogViewer.tsx
│   │   ├── pages/
│   │   │   └── HomePage.tsx
│   │   ├── api/
│   │   │   └── client.ts      # API client wrapper
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## Features

### Device Simulator
- **State Machine**: Strict IDLE → ACTIVE → FAULT state transitions
- **Registers**: Voltage, current, frequency, temperature, trip flags, status word
- **Commands**: activate, reset, inject_fault (with types: overcurrent, overvoltage, temperature)
- **Timing Simulation**: Realistic delays for state transitions
- **Comprehensive Logging**: Timestamped logs for all actions and state changes

### YAML Test Scenarios
- **Declarative Syntax**: Easy-to-write, human-readable test definitions
- **Step Types**:
  - `write`: Set register values
  - `command`: Execute device commands
  - `wait`: Insert timing delays
  - `assert`: Validate register values and states
- **Assertion Types**: equals, not_equals, greater_than, less_than, contains, in_range

### Test Runner
- **Sequential Execution**: Steps run in order with detailed result capture
- **Failure Handling**: Stops on first failure with clear error messages
- **Batch Execution**: Run multiple scenarios in sequence
- **Rich Results**: Per-step status, timing, and overall summary

### Reporting
- **JSON Reports**: Structured data for integration and archival
- **Text Summaries**: Human-readable console output
- **Batch Summaries**: Aggregate results across multiple scenarios

### REST API
- **Scenario Management**: List available scenarios
- **Execution**: Run scenarios and retrieve results
- **Run History**: Access past run results
- **Device Status**: Query current device state

### Dashboard
- **Scenario Browser**: Visual card layout of available tests
- **Run Status Panel**: Real-time status with color-coded indicators
- **State Visualizer**: Animated state machine diagram
- **Log Viewer**: Detailed execution logs with timestamps
- **Responsive Design**: Works on desktop and tablet devices

---

## Getting Started

### Prerequisites

**Backend:**
- Python 3.9 or higher
- pip (Python package manager)

**Frontend:**
- Node.js 16+ and npm

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd relaysim
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server:**
   ```bash
   python -m uvicorn api.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

   API documentation (Swagger UI): `http://localhost:8000/docs`

4. **Run tests:**
   ```bash
   pytest
   ```

   For coverage report:
   ```bash
   pytest --cov=. --cov-report=html
   ```

### Frontend Setup

1. **Navigate to the dashboard directory:**
   ```bash
   cd relaysim-dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The dashboard will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```

---

## Usage

### Running Test Scenarios

#### Via Command Line (Python)

```python
from simulator import DeviceSimulator
from runner import TestRunner

# Create device and runner
device = DeviceSimulator()
runner = TestRunner(device)

# Run a single scenario
result = runner.run_scenario("activate")

print(f"Status: {result.overall_status}")
print(f"Steps: {result.passed_steps}/{result.total_steps} passed")
```

#### Via REST API

```bash
# List available scenarios
curl http://localhost:8000/api/scenarios

# Run a scenario
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"scenario": "activate"}'

# Get run results
curl http://localhost:8000/api/runs/{run_id}
```

#### Via Dashboard

1. Open `http://localhost:5173` in your browser
2. Click on any scenario card
3. Click the "Run" button
4. Watch the real-time status updates and visualizations
5. Review logs in the log viewer

### Creating Custom Scenarios

Create a YAML file in `relaysim/config/examples/`:

```yaml
name: "My Custom Test"
description: "Tests custom behavior"

steps:
  - step: write
    register: voltage
    value: 120.0

  - step: command
    action: activate

  - step: assert
    register: state
    equals: "ACTIVE"

  - step: wait
    ms: 100

  - step: command
    action: inject_fault
    fault_type: overcurrent

  - step: assert
    register: state
    equals: "FAULT"

  - step: assert
    register: trip_flag
    equals: true

  - step: command
    action: reset

  - step: assert
    register: state
    equals: "IDLE"
```

---

## Example Scenario Run

### Scenario: `activate.yaml`

This scenario tests basic device activation and reset:

```yaml
name: "Basic Activation Test"
description: "Tests basic device activation sequence with nominal voltage and current"

steps:
  - step: write
    register: voltage
    value: 120.0

  - step: write
    register: current
    value: 5.0

  - step: assert
    register: state
    equals: "IDLE"

  - step: command
    action: activate

  - step: assert
    register: state
    equals: "ACTIVE"

  - step: command
    action: reset

  - step: assert
    register: state
    equals: "IDLE"
```

### Expected Output

**Console Summary:**
```
======================================================================
SCENARIO: Basic Activation Test
======================================================================

Status: ✓ PASSED
Duration: 0.267s
Started: 2024-01-15 10:30:45

Steps: 7/7 passed

----------------------------------------------------------------------
STEP DETAILS:
----------------------------------------------------------------------
  [✓] Step 1: write (2.1ms)
  [✓] Step 2: write (1.8ms)
  [✓] Step 3: assert (1.2ms)
  [✓] Step 4: command (152.3ms)
  [✓] Step 5: assert (0.9ms)
  [✓] Step 6: command (103.5ms)
  [✓] Step 7: assert (1.1ms)

======================================================================
```

**Dashboard View:**
- Status panel shows green "PASSED" indicator
- State visualizer highlights IDLE → ACTIVE → IDLE transitions
- Log viewer displays timestamped step execution
- All step indicators show green (passed)

---

## API Reference

### GET `/api/scenarios`
Returns list of available test scenarios.

**Response:**
```json
[
  {
    "name": "Basic Activation Test",
    "description": "Tests basic device activation...",
    "filename": "activate.yaml"
  }
]
```

### POST `/api/run`
Execute a test scenario.

**Request:**
```json
{
  "scenario": "activate"
}
```

**Response:**
```json
{
  "run_id": "activate_20240115_103045",
  "scenario_name": "Basic Activation Test",
  "overall_status": "passed",
  "duration_seconds": 0.267,
  "total_steps": 7,
  "passed_steps": 7,
  "failed_steps": 0,
  "step_results": [...]
}
```

### GET `/api/runs`
Get all scenario run results.

### GET `/api/runs/{run_id}`
Get specific run result by ID.

### GET `/api/device/status`
Get current device simulator status.

---

## Architecture & Design

### Safety-Critical System Principles

This project reflects real-world test infrastructure for safety-critical embedded systems:

1. **Deterministic Behavior**: All state transitions are predictable and reproducible
2. **Strict Validation**: Invalid operations raise exceptions immediately
3. **Comprehensive Logging**: Every action is logged with timestamps
4. **Fault Injection**: Built-in fault simulation for robustness testing
5. **Timing Accuracy**: Realistic timing delays for state transitions
6. **Traceable Results**: Complete audit trail from scenario to final report

### State Machine Design

The device simulator implements a strict state machine:

```
    ┌──────┐  activate   ┌────────┐
    │ IDLE ├────────────→│ ACTIVE │
    └───┬──┘             └───┬────┘
        │                    │
        │ reset        reset │
        │ ←──────────────────┘
        │
        │ inject_fault
        ↓
    ┌───────┐
    │ FAULT │
    └───┬───┘
        │
        │ reset (after fault cleared)
        ↓
    ┌──────┐
    │ IDLE │
    └──────┘
```

Invalid transitions (e.g., ACTIVE → ACTIVE) raise `InvalidStateTransitionError`.

### Test Scenario Philosophy

YAML scenarios provide:
- **Readability**: Non-programmers can understand and write tests
- **Maintainability**: Easy to modify without code changes
- **Version Control**: Scenarios are text files, perfect for Git
- **Declarative**: Describes *what* to test, not *how* to test it

---

## Testing

The project includes comprehensive PyTest coverage:

### Test Categories

**Unit Tests** (`test_device.py`):
- Device initialization
- Register operations (read/write/validation)
- State transitions (valid and invalid)
- Command execution
- Fault injection
- Status reporting

**Integration Tests** (`test_scenarios.py`):
- YAML loading and validation
- Scenario execution (all example scenarios)
- Step execution (write, command, wait, assert)
- Batch execution
- Result conversion and reporting

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_device.py

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## Skills Demonstrated

This project showcases expertise in:

### Software Test Infrastructure
- Automated test framework design
- YAML-based declarative testing
- Test result reporting and analysis
- Continuous integration readiness

### Embedded/Firmware Testing
- Device simulation with realistic timing
- State machine validation
- Fault injection testing
- Register-level testing patterns

### Safety-Critical System Thinking
- Deterministic behavior
- Strict error handling
- Comprehensive logging and traceability
- Invalid operation detection

### Full-Stack Development
- **Backend**: Python, FastAPI, async programming
- **Frontend**: React, TypeScript, responsive design
- **API Design**: RESTful endpoints, CORS, error handling
- **DevOps**: Project structure, dependency management

### Software Engineering Best Practices
- Clean architecture (separation of concerns)
- Type safety (Python type hints, TypeScript)
- Comprehensive testing (unit + integration)
- Documentation (inline docs, README, API docs)

---

## Future Enhancements

Potential extensions to demonstrate additional skills:

- **Database Integration**: Persist run results in PostgreSQL
- **Real-Time Updates**: WebSocket support for live status updates
- **Parallel Execution**: Run multiple scenarios concurrently
- **CI/CD Pipeline**: GitHub Actions for automated testing
- **Docker Containers**: Containerized deployment
- **Metrics Dashboard**: Historical test analytics and trends
- **Hardware-in-Loop**: Integration with actual embedded devices
- **Report Export**: PDF report generation

---

## License

This is a demonstration project for portfolio purposes.

## Contact

For questions or collaboration opportunities, please reach out via GitHub.

---

**Built to demonstrate production-quality test infrastructure for safety-critical embedded systems.**
