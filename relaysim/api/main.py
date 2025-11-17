"""
FastAPI backend for Relaysim test harness.

Provides REST API for running scenarios and viewing results.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..runner import ScenarioResult, TestRunner, YAMLScenarioLoader
from ..simulator import DeviceSimulator
from ..reports import ReportGenerator
from ..utils import setup_logger

# Setup logging
logger = setup_logger("relaysim.api", level="INFO")

# Create FastAPI app
app = FastAPI(
    title="Relaysim API",
    description="Automated Firmware Test Harness API",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite and CRA defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for run results
run_results: Dict[str, ScenarioResult] = {}


# Request/Response Models
class RunScenarioRequest(BaseModel):
    """Request model for running a scenario."""
    scenario: str


class ScenarioInfo(BaseModel):
    """Information about a scenario."""
    name: str
    description: str
    filename: str


class StepResultResponse(BaseModel):
    """Response model for a step result."""
    step_number: int
    step_type: str
    status: str
    message: str
    details: dict
    duration_ms: float


class RunResultResponse(BaseModel):
    """Response model for a scenario run result."""
    run_id: str
    scenario_name: str
    description: str
    start_time: float
    start_datetime: str
    end_time: Optional[float]
    end_datetime: Optional[str]
    duration_seconds: float
    overall_status: str
    error_message: Optional[str]
    total_steps: int
    passed_steps: int
    failed_steps: int
    step_results: List[StepResultResponse]


class DeviceStatusResponse(BaseModel):
    """Response model for device status."""
    state: str
    registers: dict
    fault_active: bool
    fault_type: Optional[str]
    log_count: int


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Relaysim API",
        "version": "1.0.0",
        "description": "Automated Firmware Test Harness",
        "endpoints": {
            "scenarios": "/api/scenarios",
            "run": "/api/run",
            "runs": "/api/runs",
            "device_status": "/api/device/status",
        }
    }


@app.get("/api/scenarios", response_model=List[ScenarioInfo])
async def list_scenarios():
    """
    Get list of available test scenarios.

    Returns:
        List of scenario information
    """
    try:
        loader = YAMLScenarioLoader()
        scenarios = loader.list_scenarios()

        return [
            ScenarioInfo(
                name=s["name"],
                description=s["description"],
                filename=s["filename"]
            )
            for s in scenarios
        ]
    except Exception as e:
        logger.exception("Failed to list scenarios")
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")


@app.post("/api/run", response_model=RunResultResponse)
async def run_scenario(request: RunScenarioRequest):
    """
    Run a test scenario.

    Args:
        request: Run request with scenario name

    Returns:
        Scenario run result
    """
    scenario_name = request.scenario
    logger.info(f"Running scenario: {scenario_name}")

    try:
        # Create fresh device and runner for this execution
        device = DeviceSimulator()
        runner = TestRunner(device)

        # Run the scenario
        result = runner.run_scenario(scenario_name)

        # Store result
        run_results[result.run_id] = result

        # Generate report
        report_gen = ReportGenerator()
        report_gen.generate_json_report(result)

        # Log summary
        logger.info(f"Scenario '{scenario_name}' completed with status: {result.overall_status}")

        # Convert to response model
        return _convert_to_response(result)

    except Exception as e:
        logger.exception(f"Failed to run scenario '{scenario_name}'")
        raise HTTPException(status_code=500, detail=f"Failed to run scenario: {str(e)}")


@app.get("/api/runs", response_model=List[RunResultResponse])
async def list_runs():
    """
    Get list of all scenario runs.

    Returns:
        List of all run results
    """
    return [_convert_to_response(result) for result in run_results.values()]


@app.get("/api/runs/{run_id}", response_model=RunResultResponse)
async def get_run(run_id: str):
    """
    Get details of a specific run.

    Args:
        run_id: Run identifier

    Returns:
        Run result details
    """
    if run_id not in run_results:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    return _convert_to_response(run_results[run_id])


@app.delete("/api/runs/{run_id}")
async def delete_run(run_id: str):
    """
    Delete a specific run from memory.

    Args:
        run_id: Run identifier

    Returns:
        Success message
    """
    if run_id not in run_results:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    del run_results[run_id]
    logger.info(f"Deleted run: {run_id}")

    return {"message": f"Run '{run_id}' deleted successfully"}


@app.delete("/api/runs")
async def clear_runs():
    """
    Clear all runs from memory.

    Returns:
        Success message with count
    """
    count = len(run_results)
    run_results.clear()
    logger.info(f"Cleared {count} runs")

    return {"message": f"Cleared {count} runs"}


@app.get("/api/device/status", response_model=DeviceStatusResponse)
async def get_device_status():
    """
    Get current device status.

    Note: This creates a fresh device instance for status checking.

    Returns:
        Device status
    """
    device = DeviceSimulator()
    status = device.get_status()

    return DeviceStatusResponse(
        state=status["state"],
        registers=status["registers"],
        fault_active=status["fault_active"],
        fault_type=status.get("fault_type"),
        log_count=status["log_count"]
    )


# Helper Functions

def _convert_to_response(result: ScenarioResult) -> RunResultResponse:
    """Convert ScenarioResult to API response model."""
    result_dict = result.to_dict()

    return RunResultResponse(
        run_id=result_dict["run_id"],
        scenario_name=result_dict["scenario_name"],
        description=result_dict["description"],
        start_time=result_dict["start_time"],
        start_datetime=result_dict["start_datetime"],
        end_time=result_dict["end_time"],
        end_datetime=result_dict["end_datetime"],
        duration_seconds=result_dict["duration_seconds"],
        overall_status=result_dict["overall_status"],
        error_message=result_dict["error_message"],
        total_steps=result_dict["total_steps"],
        passed_steps=result_dict["passed_steps"],
        failed_steps=result_dict["failed_steps"],
        step_results=[
            StepResultResponse(**step) for step in result_dict["step_results"]
        ]
    )


# Startup/Shutdown Events

@app.on_event("startup")
async def startup_event():
    """Log startup message."""
    logger.info("Relaysim API started")
    logger.info("Available at http://localhost:8000")
    logger.info("API docs at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown message."""
    logger.info("Relaysim API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
