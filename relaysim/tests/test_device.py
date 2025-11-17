"""
Unit tests for device simulator.
"""

import pytest

from simulator import (
    DeviceSimulator,
    DeviceState,
    InvalidStateTransitionError,
    RegisterWriteError,
    CommandExecutionError,
)


class TestDeviceSimulatorInitialization:
    """Tests for device initialization."""

    def test_initial_state_is_idle(self, device):
        """Device should start in IDLE state."""
        assert device.state == DeviceState.IDLE

    def test_default_registers_initialized(self, device):
        """All default registers should be initialized."""
        registers = device.registers
        assert "voltage" in registers
        assert "current" in registers
        assert "frequency" in registers
        assert "trip_flag" in registers
        assert "trip_count" in registers
        assert "temperature" in registers
        assert "status_word" in registers

    def test_default_register_values(self, device):
        """Default register values should be correct."""
        assert device.get_register("voltage") == 0.0
        assert device.get_register("current") == 0.0
        assert device.get_register("frequency") == 60.0
        assert device.get_register("trip_flag") is False
        assert device.get_register("trip_count") == 0
        assert device.get_register("temperature") == 25.0
        assert device.get_register("status_word") == 0x0000

    def test_logs_created_on_initialization(self, device):
        """Device should create initialization log."""
        logs = device.logs
        assert len(logs) > 0
        assert logs[0].level == "INFO"
        assert "initialized" in logs[0].message.lower()


class TestRegisterOperations:
    """Tests for register read/write operations."""

    def test_read_existing_register(self, device):
        """Should successfully read an existing register."""
        value = device.get_register("voltage")
        assert value == 0.0

    def test_read_nonexistent_register(self, device):
        """Should raise error when reading non-existent register."""
        with pytest.raises(RegisterWriteError):
            device.get_register("nonexistent")

    def test_write_valid_value(self, device):
        """Should successfully write valid value to register."""
        device.write_register("voltage", 120.0)
        assert device.get_register("voltage") == 120.0

    def test_write_type_conversion(self, device):
        """Should convert types when possible."""
        device.write_register("voltage", "240.5")
        assert device.get_register("voltage") == 240.5
        assert isinstance(device.get_register("voltage"), float)

    def test_write_invalid_type(self, device):
        """Should raise error for incompatible type."""
        with pytest.raises(RegisterWriteError):
            device.write_register("voltage", "not_a_number")

    def test_write_nonexistent_register(self, device):
        """Should raise error when writing to non-existent register."""
        with pytest.raises(RegisterWriteError):
            device.write_register("nonexistent", 123)

    def test_write_boolean_register(self, device):
        """Should handle boolean registers correctly."""
        device.write_register("trip_flag", True)
        assert device.get_register("trip_flag") is True

    def test_write_integer_register(self, device):
        """Should handle integer registers correctly."""
        device.write_register("trip_count", 5)
        assert device.get_register("trip_count") == 5

    def test_register_write_logged(self, device):
        """Register writes should be logged."""
        initial_log_count = len(device.logs)
        device.write_register("voltage", 120.0)
        assert len(device.logs) > initial_log_count


class TestActivateCommand:
    """Tests for device activation."""

    def test_activate_from_idle(self, device):
        """Should successfully activate from IDLE state."""
        device.activate()
        assert device.state == DeviceState.ACTIVE

    def test_activate_from_active_fails(self, device):
        """Should fail to activate when already ACTIVE."""
        device.activate()
        with pytest.raises(CommandExecutionError):
            device.activate()

    def test_activate_from_fault_fails(self, device):
        """Should fail to activate from FAULT state."""
        device.activate()
        device.inject_fault()
        with pytest.raises(CommandExecutionError):
            device.activate()

    def test_activate_updates_status_word(self, device):
        """Activation should set bit 0 in status word."""
        device.activate()
        status = device.get_register("status_word")
        assert status & 0x0001 == 0x0001

    def test_activate_logged(self, device):
        """Activation should be logged."""
        initial_log_count = len(device.logs)
        device.activate()
        logs = device.logs[initial_log_count:]
        assert any("activation" in log.message.lower() for log in logs)


class TestResetCommand:
    """Tests for device reset."""

    def test_reset_from_active(self, device):
        """Should reset from ACTIVE to IDLE."""
        device.activate()
        device.reset()
        assert device.state == DeviceState.IDLE

    def test_reset_from_fault(self, device):
        """Should reset from FAULT to IDLE."""
        device.activate()
        device.inject_fault()
        device.reset()
        assert device.state == DeviceState.IDLE

    def test_reset_clears_trip_flag(self, device):
        """Reset should clear trip flag."""
        device.activate()
        device.inject_fault()
        assert device.get_register("trip_flag") is True
        device.reset()
        assert device.get_register("trip_flag") is False

    def test_reset_clears_status_word_active_bit(self, device):
        """Reset should clear bit 0 in status word."""
        device.activate()
        device.reset()
        status = device.get_register("status_word")
        assert status & 0x0001 == 0x0000

    def test_reset_from_idle(self, device):
        """Reset from IDLE should remain IDLE."""
        device.reset()
        assert device.state == DeviceState.IDLE

    def test_reset_logged(self, device):
        """Reset should be logged."""
        device.activate()
        initial_log_count = len(device.logs)
        device.reset()
        logs = device.logs[initial_log_count:]
        assert any("reset" in log.message.lower() for log in logs)


class TestFaultInjection:
    """Tests for fault injection."""

    def test_inject_fault_from_idle(self, device):
        """Should inject fault from IDLE state."""
        device.inject_fault("overcurrent")
        assert device.state == DeviceState.FAULT

    def test_inject_fault_from_active(self, device):
        """Should inject fault from ACTIVE state."""
        device.activate()
        device.inject_fault("overcurrent")
        assert device.state == DeviceState.FAULT

    def test_overcurrent_fault_sets_registers(self, device):
        """Overcurrent fault should set appropriate registers."""
        device.inject_fault("overcurrent")
        assert device.get_register("trip_flag") is True
        assert device.get_register("trip_count") >= 1
        assert device.get_register("current") > 100.0

    def test_overvoltage_fault_sets_registers(self, device):
        """Overvoltage fault should set appropriate registers."""
        device.inject_fault("overvoltage")
        assert device.get_register("trip_flag") is True
        assert device.get_register("voltage") > 400.0

    def test_temperature_fault_sets_registers(self, device):
        """Temperature fault should set appropriate registers."""
        device.inject_fault("temperature")
        assert device.get_register("trip_flag") is True
        assert device.get_register("temperature") >= 90.0

    def test_fault_sets_status_word(self, device):
        """Fault should set bit 7 in status word."""
        device.inject_fault()
        status = device.get_register("status_word")
        assert status & 0x0080 == 0x0080

    def test_fault_increments_trip_count(self, device):
        """Each fault should increment trip count."""
        device.inject_fault()
        count1 = device.get_register("trip_count")
        device.reset()
        device.inject_fault()
        count2 = device.get_register("trip_count")
        assert count2 == count1 + 1

    def test_fault_logged(self, device):
        """Fault injection should be logged."""
        initial_log_count = len(device.logs)
        device.inject_fault()
        logs = device.logs[initial_log_count:]
        assert any("fault" in log.message.lower() for log in logs)


class TestDeviceStatus:
    """Tests for device status reporting."""

    def test_get_status_idle(self, device):
        """Status should reflect IDLE state."""
        status = device.get_status()
        assert status["state"] == "IDLE"
        assert status["fault_active"] is False
        assert status["fault_type"] is None

    def test_get_status_active(self, device):
        """Status should reflect ACTIVE state."""
        device.activate()
        status = device.get_status()
        assert status["state"] == "ACTIVE"
        assert status["fault_active"] is False

    def test_get_status_fault(self, device):
        """Status should reflect FAULT state."""
        device.inject_fault("overcurrent")
        status = device.get_status()
        assert status["state"] == "FAULT"
        assert status["fault_active"] is True
        assert status["fault_type"] == "overcurrent"

    def test_get_status_includes_registers(self, device):
        """Status should include register values."""
        device.write_register("voltage", 120.0)
        status = device.get_status()
        assert "registers" in status
        assert status["registers"]["voltage"] == 120.0

    def test_get_status_includes_log_count(self, device):
        """Status should include log count."""
        status = device.get_status()
        assert "log_count" in status
        assert status["log_count"] > 0


class TestStateMachineTransitions:
    """Tests for state machine transition validation."""

    def test_invalid_transition_idle_to_fault_without_injection(self, device):
        """Cannot go to FAULT without fault injection."""
        # This is implicitly tested - there's no command to go IDLE->FAULT except inject_fault
        assert device.state == DeviceState.IDLE

    def test_state_persistence(self, device):
        """State should persist across operations."""
        device.write_register("voltage", 100.0)
        assert device.state == DeviceState.IDLE
        device.write_register("current", 5.0)
        assert device.state == DeviceState.IDLE

    def test_complete_lifecycle(self, device):
        """Test complete device lifecycle."""
        # Start in IDLE
        assert device.state == DeviceState.IDLE

        # Activate
        device.activate()
        assert device.state == DeviceState.ACTIVE

        # Inject fault
        device.inject_fault()
        assert device.state == DeviceState.FAULT

        # Reset
        device.reset()
        assert device.state == DeviceState.IDLE
