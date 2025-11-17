"""
Test runner for executing YAML scenarios against device simulator.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..simulator import DeviceSimulator, DeviceState
from ..utils import get_logger
from .yaml_loader import YAMLScenarioLoader

logger = get_logger()


class TestStepError(Exception):
    """Raised when a test step fails."""
    pass


class StepResult:
    """Result of a single test step."""

    def __init__(
        self,
        step_number: int,
        step_type: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
    ):
        self.step_number = step_number
        self.step_type = step_type
        self.status = status  # "pass", "fail", "error"
        self.message = message
        self.details = details or {}
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_number": self.step_number,
            "step_type": self.step_type,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "duration_ms": round(self.duration_ms, 2),
        }


class ScenarioResult:
    """Result of a complete scenario run."""

    def __init__(
        self,
        scenario_name: str,
        description: str = "",
        run_id: Optional[str] = None,
    ):
        self.scenario_name = scenario_name
        self.description = description
        self.run_id = run_id or self._generate_run_id()
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.step_results: List[StepResult] = []
        self.overall_status = "running"  # running, passed, failed, error
        self.error_message: Optional[str] = None

    def _generate_run_id(self) -> str:
        """Generate a unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.scenario_name}_{timestamp}"

    def add_step_result(self, result: StepResult) -> None:
        """Add a step result."""
        self.step_results.append(result)

    def finalize(self, status: str, error_message: Optional[str] = None) -> None:
        """Finalize the scenario result."""
        self.end_time = time.time()
        self.overall_status = status
        self.error_message = error_message

    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def passed_steps(self) -> int:
        """Count of passed steps."""
        return sum(1 for r in self.step_results if r.status == "pass")

    @property
    def failed_steps(self) -> int:
        """Count of failed steps."""
        return sum(1 for r in self.step_results if r.status in ("fail", "error"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "scenario_name": self.scenario_name,
            "description": self.description,
            "start_time": self.start_time,
            "start_datetime": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": self.end_time,
            "end_datetime": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_seconds": round(self.duration_seconds, 3),
            "overall_status": self.overall_status,
            "error_message": self.error_message,
            "total_steps": len(self.step_results),
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "step_results": [r.to_dict() for r in self.step_results],
        }


class TestRunner:
    """Executes test scenarios against device simulator."""

    def __init__(self, device: Optional[DeviceSimulator] = None):
        """
        Initialize the test runner.

        Args:
            device: Device simulator instance (creates new one if not provided)
        """
        self.device = device or DeviceSimulator()
        self.loader = YAMLScenarioLoader()

    def run_scenario(self, scenario_name: str) -> ScenarioResult:
        """
        Run a single scenario.

        Args:
            scenario_name: Name of the scenario to run

        Returns:
            ScenarioResult with all step results
        """
        logger.info(f"Starting scenario: {scenario_name}")

        # Load scenario
        scenario = self.loader.load_scenario(scenario_name)

        result = ScenarioResult(
            scenario_name=scenario["name"],
            description=scenario["description"]
        )

        try:
            # Execute each step
            for i, step in enumerate(scenario["steps"], start=1):
                step_result = self._execute_step(i, step)
                result.add_step_result(step_result)

                # Stop on first failure
                if step_result.status in ("fail", "error"):
                    result.finalize("failed", step_result.message)
                    logger.error(f"Scenario failed at step {i}: {step_result.message}")
                    return result

            # All steps passed
            result.finalize("passed")
            logger.info(f"Scenario '{scenario_name}' completed successfully")

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            result.finalize("error", error_msg)
            logger.exception(f"Scenario '{scenario_name}' encountered error")

        return result

    def _execute_step(self, step_number: int, step: Dict[str, Any]) -> StepResult:
        """
        Execute a single test step.

        Args:
            step_number: Step number (1-indexed)
            step: Step dictionary from scenario

        Returns:
            StepResult
        """
        step_type = step["step"]
        start_time = time.time()

        logger.debug(f"Executing step {step_number}: {step_type}")

        try:
            if step_type == "write":
                self._execute_write(step)
            elif step_type == "command":
                self._execute_command(step)
            elif step_type == "wait":
                self._execute_wait(step)
            elif step_type == "assert":
                self._execute_assert(step)
            else:
                raise TestStepError(f"Unknown step type: {step_type}")

            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step_number=step_number,
                step_type=step_type,
                status="pass",
                message=f"{step_type.capitalize()} step completed",
                details=step,
                duration_ms=duration_ms,
            )

        except AssertionError as e:
            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step_number=step_number,
                step_type=step_type,
                status="fail",
                message=str(e),
                details=step,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return StepResult(
                step_number=step_number,
                step_type=step_type,
                status="error",
                message=f"Error: {str(e)}",
                details=step,
                duration_ms=duration_ms,
            )

    def _execute_write(self, step: Dict[str, Any]) -> None:
        """Execute a write step."""
        register = step["register"]
        value = step["value"]

        # Special handling for state register (read-only, used for assertions)
        if register == "state":
            raise TestStepError("Cannot write to 'state' register (read-only)")

        self.device.write_register(register, value)
        logger.debug(f"Wrote {value} to register '{register}'")

    def _execute_command(self, step: Dict[str, Any]) -> None:
        """Execute a command step."""
        action = step["action"]

        if action == "activate":
            self.device.activate()
        elif action == "reset":
            self.device.reset()
        elif action == "inject_fault":
            fault_type = step.get("fault_type", "overcurrent")
            self.device.inject_fault(fault_type)
        else:
            raise TestStepError(f"Unknown command action: {action}")

        logger.debug(f"Executed command: {action}")

    def _execute_wait(self, step: Dict[str, Any]) -> None:
        """Execute a wait step."""
        wait_ms = step["ms"]
        time.sleep(wait_ms / 1000.0)
        logger.debug(f"Waited {wait_ms}ms")

    def _execute_assert(self, step: Dict[str, Any]) -> None:
        """Execute an assert step."""
        register = step["register"]

        # Special handling for state
        if register == "state":
            actual_value = self.device.state.value
        else:
            actual_value = self.device.get_register(register)

        # Check different assertion types
        if "equals" in step:
            expected = step["equals"]
            if actual_value != expected:
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected {expected}"
                )

        elif "not_equals" in step:
            expected = step["not_equals"]
            if actual_value == expected:
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected not {expected}"
                )

        elif "greater_than" in step:
            threshold = step["greater_than"]
            if not (actual_value > threshold):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected > {threshold}"
                )

        elif "less_than" in step:
            threshold = step["less_than"]
            if not (actual_value < threshold):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected < {threshold}"
                )

        elif "greater_or_equal" in step:
            threshold = step["greater_or_equal"]
            if not (actual_value >= threshold):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected >= {threshold}"
                )

        elif "less_or_equal" in step:
            threshold = step["less_or_equal"]
            if not (actual_value <= threshold):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected <= {threshold}"
                )

        elif "contains" in step:
            substring = step["contains"]
            if substring not in str(actual_value):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected to contain '{substring}'"
                )

        elif "in_range" in step:
            range_spec = step["in_range"]
            min_val, max_val = range_spec["min"], range_spec["max"]
            if not (min_val <= actual_value <= max_val):
                raise AssertionError(
                    f"Assertion failed: {register} = {actual_value}, expected in range [{min_val}, {max_val}]"
                )

        logger.debug(f"Assertion passed for register '{register}'")

    def run_batch(self, scenario_names: List[str]) -> List[ScenarioResult]:
        """
        Run multiple scenarios in sequence.

        Args:
            scenario_names: List of scenario names to run

        Returns:
            List of ScenarioResults
        """
        results = []
        for scenario_name in scenario_names:
            result = self.run_scenario(scenario_name)
            results.append(result)

            # Reset device between scenarios
            try:
                if self.device.state != DeviceState.IDLE:
                    self.device.reset()
            except Exception as e:
                logger.warning(f"Failed to reset device between scenarios: {e}")

        return results
