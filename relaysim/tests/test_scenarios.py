"""
Tests for YAML scenario loading and execution.
"""

import pytest
from pathlib import Path

from runner import (
    YAMLScenarioLoader,
    ScenarioLoadError,
    ScenarioValidationError,
    TestRunner,
)
from simulator import DeviceSimulator


class TestYAMLScenarioLoader:
    """Tests for YAML scenario loading."""

    def test_load_activate_scenario(self, scenario_loader):
        """Should successfully load activate scenario."""
        scenario = scenario_loader.load_scenario("activate")
        assert scenario["name"] == "Basic Activation Test"
        assert len(scenario["steps"]) > 0

    def test_load_fault_injection_scenario(self, scenario_loader):
        """Should successfully load fault injection scenario."""
        scenario = scenario_loader.load_scenario("fault_injection")
        assert scenario["name"] == "Fault Injection Test"
        assert "fault" in scenario["description"].lower()

    def test_load_nonexistent_scenario(self, scenario_loader):
        """Should raise error for non-existent scenario."""
        with pytest.raises(ScenarioLoadError):
            scenario_loader.load_scenario("nonexistent")

    def test_list_scenarios(self, scenario_loader):
        """Should list all available scenarios."""
        scenarios = scenario_loader.list_scenarios()
        assert len(scenarios) > 0
        assert all("name" in s for s in scenarios)
        assert all("description" in s for s in scenarios)
        assert all("filename" in s for s in scenarios)

    def test_scenario_has_required_fields(self, scenario_loader):
        """Loaded scenario should have required fields."""
        scenario = scenario_loader.load_scenario("activate")
        assert "name" in scenario
        assert "description" in scenario
        assert "steps" in scenario
        assert isinstance(scenario["steps"], list)

    def test_validate_scenario_file(self, scenario_loader):
        """Should validate scenario file structure."""
        assert scenario_loader.validate_scenario_file("activate") is True

    def test_scenario_steps_structure(self, scenario_loader):
        """Steps should have valid structure."""
        scenario = scenario_loader.load_scenario("activate")
        for step in scenario["steps"]:
            assert "step" in step
            assert step["step"] in ["write", "command", "wait", "assert"]


class TestScenarioExecution:
    """Tests for scenario execution."""

    def test_run_activate_scenario(self, runner):
        """Should successfully run activate scenario."""
        result = runner.run_scenario("activate")
        assert result.overall_status == "passed"
        assert result.failed_steps == 0

    def test_run_fault_injection_scenario(self, runner):
        """Should successfully run fault injection scenario."""
        result = runner.run_scenario("fault_injection")
        assert result.overall_status == "passed"
        assert result.failed_steps == 0

    def test_run_overvoltage_scenario(self, runner):
        """Should successfully run overvoltage scenario."""
        result = runner.run_scenario("overvoltage")
        assert result.overall_status == "passed"
        assert result.failed_steps == 0

    def test_run_timing_validation_scenario(self, runner):
        """Should successfully run timing validation scenario."""
        result = runner.run_scenario("timing_validation")
        assert result.overall_status == "passed"
        assert result.failed_steps == 0

    def test_run_temperature_fault_scenario(self, runner):
        """Should successfully run temperature fault scenario."""
        result = runner.run_scenario("temperature_fault")
        assert result.overall_status == "passed"
        assert result.failed_steps == 0

    def test_scenario_result_has_metadata(self, runner):
        """Result should contain scenario metadata."""
        result = runner.run_scenario("activate")
        assert result.scenario_name
        assert result.run_id
        assert result.start_time is not None
        assert result.end_time is not None

    def test_scenario_result_has_step_results(self, runner):
        """Result should contain individual step results."""
        result = runner.run_scenario("activate")
        assert len(result.step_results) > 0
        for step_result in result.step_results:
            assert step_result.step_number > 0
            assert step_result.step_type
            assert step_result.status in ["pass", "fail", "error"]

    def test_passed_scenario_all_steps_pass(self, runner):
        """In a passed scenario, all steps should pass."""
        result = runner.run_scenario("activate")
        assert result.overall_status == "passed"
        assert all(sr.status == "pass" for sr in result.step_results)

    def test_scenario_duration_recorded(self, runner):
        """Scenario duration should be recorded."""
        result = runner.run_scenario("activate")
        assert result.duration_seconds > 0
        # Should complete in reasonable time (< 5 seconds)
        assert result.duration_seconds < 5.0

    def test_step_duration_recorded(self, runner):
        """Individual step durations should be recorded."""
        result = runner.run_scenario("activate")
        for step_result in result.step_results:
            assert step_result.duration_ms >= 0


class TestWriteSteps:
    """Tests for write step execution."""

    def test_write_step_updates_register(self, runner):
        """Write step should update register value."""
        # Create a minimal scenario programmatically
        device = DeviceSimulator()
        device.write_register("voltage", 0.0)
        assert device.get_register("voltage") == 0.0

        device.write_register("voltage", 120.0)
        assert device.get_register("voltage") == 120.0

    def test_write_multiple_registers(self, runner):
        """Should handle writing multiple registers."""
        result = runner.run_scenario("activate")
        # activate.yaml writes voltage and current
        assert result.overall_status == "passed"


class TestCommandSteps:
    """Tests for command step execution."""

    def test_activate_command_step(self, runner):
        """Activate command should change state."""
        device = DeviceSimulator()
        runner_instance = TestRunner(device)

        # Execute step
        step = {"step": "command", "action": "activate"}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"
        assert device.state.value == "ACTIVE"

    def test_reset_command_step(self, runner):
        """Reset command should change state to IDLE."""
        device = DeviceSimulator()
        device.activate()
        runner_instance = TestRunner(device)

        step = {"step": "command", "action": "reset"}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"
        assert device.state.value == "IDLE"

    def test_inject_fault_command_step(self, runner):
        """Inject fault command should change state to FAULT."""
        device = DeviceSimulator()
        device.activate()
        runner_instance = TestRunner(device)

        step = {"step": "command", "action": "inject_fault", "fault_type": "overcurrent"}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"
        assert device.state.value == "FAULT"


class TestWaitSteps:
    """Tests for wait step execution."""

    def test_wait_step_delays(self, runner):
        """Wait step should introduce delay."""
        import time
        device = DeviceSimulator()
        runner_instance = TestRunner(device)

        step = {"step": "wait", "ms": 100}

        start = time.time()
        step_result = runner_instance._execute_step(1, step)
        duration = time.time() - start

        assert step_result.status == "pass"
        assert duration >= 0.1  # At least 100ms


class TestAssertSteps:
    """Tests for assert step execution."""

    def test_assert_equals_pass(self, runner):
        """Assert equals should pass when values match."""
        device = DeviceSimulator()
        device.write_register("voltage", 120.0)
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "voltage", "equals": 120.0}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"

    def test_assert_equals_fail(self, runner):
        """Assert equals should fail when values don't match."""
        device = DeviceSimulator()
        device.write_register("voltage", 100.0)
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "voltage", "equals": 120.0}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "fail"

    def test_assert_state(self, runner):
        """Should be able to assert device state."""
        device = DeviceSimulator()
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "state", "equals": "IDLE"}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"

    def test_assert_greater_than(self, runner):
        """Assert greater_than should work correctly."""
        device = DeviceSimulator()
        device.write_register("voltage", 150.0)
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "voltage", "greater_than": 100.0}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"

    def test_assert_less_than(self, runner):
        """Assert less_than should work correctly."""
        device = DeviceSimulator()
        device.write_register("voltage", 50.0)
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "voltage", "less_than": 100.0}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"

    def test_assert_boolean(self, runner):
        """Should be able to assert boolean registers."""
        device = DeviceSimulator()
        device.write_register("trip_flag", False)
        runner_instance = TestRunner(device)

        step = {"step": "assert", "register": "trip_flag", "equals": False}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "pass"


class TestFailureScenarios:
    """Tests for scenario failure conditions."""

    def test_failed_assertion_stops_scenario(self, runner):
        """Failed assertion should stop scenario execution."""
        # We'll test this by checking that a failed scenario has status "failed"
        device = DeviceSimulator()
        runner_instance = TestRunner(device)

        # Manually create a scenario that will fail
        device.write_register("voltage", 100.0)

        step = {"step": "assert", "register": "voltage", "equals": 200.0}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "fail"

    def test_invalid_command_causes_error(self, runner):
        """Invalid command should cause error status."""
        device = DeviceSimulator()
        runner_instance = TestRunner(device)

        step = {"step": "command", "action": "invalid_action"}
        step_result = runner_instance._execute_step(1, step)

        assert step_result.status == "error"


class TestBatchExecution:
    """Tests for batch scenario execution."""

    def test_run_batch_scenarios(self, runner):
        """Should successfully run multiple scenarios."""
        scenarios = ["activate", "fault_injection"]
        results = runner.run_batch(scenarios)

        assert len(results) == 2
        assert all(r.overall_status == "passed" for r in results)

    def test_batch_results_have_unique_ids(self, runner):
        """Each scenario in batch should have unique run ID."""
        scenarios = ["activate", "fault_injection"]
        results = runner.run_batch(scenarios)

        run_ids = [r.run_id for r in results]
        assert len(run_ids) == len(set(run_ids))  # All unique


class TestScenarioResultConversion:
    """Tests for scenario result data conversion."""

    def test_result_to_dict(self, runner):
        """Should convert result to dictionary."""
        result = runner.run_scenario("activate")
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "run_id" in result_dict
        assert "scenario_name" in result_dict
        assert "overall_status" in result_dict
        assert "step_results" in result_dict

    def test_step_result_to_dict(self, runner):
        """Step results should convert to dictionaries."""
        result = runner.run_scenario("activate")
        result_dict = result.to_dict()

        for step_dict in result_dict["step_results"]:
            assert "step_number" in step_dict
            assert "step_type" in step_dict
            assert "status" in step_dict
            assert "duration_ms" in step_dict
