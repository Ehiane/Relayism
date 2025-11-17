"""
Device simulator for safety-critical relay/protection device.

Simulates firmware-controlled device with registers, states, and timing.
"""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from .state_machine import DeviceState, StateMachine, InvalidStateTransitionError


class DeviceSimulationError(Exception):
    """Base exception for device simulation errors."""
    pass


class RegisterWriteError(DeviceSimulationError):
    """Raised when a register write operation fails."""
    pass


class CommandExecutionError(DeviceSimulationError):
    """Raised when a command execution fails."""
    pass


class LogEntry:
    """Represents a single log entry."""

    def __init__(self, timestamp: float, level: str, message: str, data: Optional[Dict] = None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level,
            "message": self.message,
            "data": self.data,
        }

    def __str__(self) -> str:
        """String representation."""
        dt = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"[{dt}] {self.level}: {self.message}"


class DeviceSimulator:
    """
    Simulates a firmware-controlled relay protection device.

    Features:
    - Internal registers (voltage, current, trip_flag, etc.)
    - State machine (IDLE, ACTIVE, FAULT)
    - Commands (activate, reset, inject_fault)
    - Timing simulation for state transitions
    - Comprehensive logging
    """

    # Timing constants (in seconds)
    ACTIVATION_DELAY = 0.15  # Time from activate command to ACTIVE state
    RESET_DELAY = 0.1  # Time for reset operation
    FAULT_DETECTION_DELAY = 0.05  # Time to detect and transition to FAULT

    # Default register values
    DEFAULT_REGISTERS = {
        "voltage": 0.0,
        "current": 0.0,
        "frequency": 60.0,
        "trip_flag": False,
        "trip_count": 0,
        "temperature": 25.0,
        "status_word": 0x0000,
    }

    def __init__(self):
        """Initialize the device simulator."""
        self._state_machine = StateMachine(DeviceState.IDLE)
        self._registers: Dict[str, Any] = self.DEFAULT_REGISTERS.copy()
        self._logs: List[LogEntry] = []
        self._activation_start_time: Optional[float] = None
        self._fault_type: Optional[str] = None

        self._log("INFO", "Device simulator initialized", {"state": self.state.value})

    @property
    def state(self) -> DeviceState:
        """Get current device state."""
        return self._state_machine.current_state

    @property
    def registers(self) -> Dict[str, Any]:
        """Get a copy of all registers."""
        return self._registers.copy()

    @property
    def logs(self) -> List[LogEntry]:
        """Get all log entries."""
        return self._logs.copy()

    def _log(self, level: str, message: str, data: Optional[Dict] = None) -> None:
        """Add a log entry."""
        entry = LogEntry(time.time(), level, message, data)
        self._logs.append(entry)

    def get_register(self, name: str) -> Any:
        """
        Read a register value.

        Args:
            name: Register name

        Returns:
            Register value

        Raises:
            RegisterWriteError: If register doesn't exist
        """
        if name not in self._registers:
            raise RegisterWriteError(f"Register '{name}' does not exist")
        return self._registers[name]

    def write_register(self, name: str, value: Any) -> None:
        """
        Write a value to a register.

        Args:
            name: Register name
            value: Value to write

        Raises:
            RegisterWriteError: If register doesn't exist or value is invalid
        """
        if name not in self._registers:
            raise RegisterWriteError(f"Register '{name}' does not exist")

        old_value = self._registers[name]

        # Type validation based on default register types
        expected_type = type(self.DEFAULT_REGISTERS[name])
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except (ValueError, TypeError):
                raise RegisterWriteError(
                    f"Invalid value type for register '{name}'. "
                    f"Expected {expected_type.__name__}, got {type(value).__name__}"
                )

        self._registers[name] = value
        self._log(
            "DEBUG",
            f"Register write: {name}",
            {"old_value": old_value, "new_value": value}
        )

    def activate(self) -> None:
        """
        Activate the device.

        Transitions from IDLE to ACTIVE with a simulated delay.

        Raises:
            CommandExecutionError: If activation fails
        """
        if self.state != DeviceState.IDLE:
            raise CommandExecutionError(
                f"Cannot activate from state {self.state.value}. Must be in IDLE state."
            )

        self._log("INFO", "Activation command received", {"current_state": self.state.value})

        # Start activation process
        self._activation_start_time = time.time()

        # Simulate the activation delay
        time.sleep(self.ACTIVATION_DELAY)

        # Perform state transition
        try:
            old_state = self.state
            self._state_machine.activate()
            self._log(
                "INFO",
                "Device activated",
                {"previous_state": old_state.value, "new_state": self.state.value}
            )
            # Update status word
            self._registers["status_word"] |= 0x0001  # Set bit 0 for ACTIVE
        except InvalidStateTransitionError as e:
            self._log("ERROR", f"Activation failed: {e}")
            raise CommandExecutionError(str(e))

    def reset(self) -> None:
        """
        Reset the device to IDLE state.

        Clears fault conditions and returns to idle.

        Raises:
            CommandExecutionError: If reset fails
        """
        self._log("INFO", "Reset command received", {"current_state": self.state.value})

        # Simulate reset delay
        time.sleep(self.RESET_DELAY)

        try:
            old_state = self.state
            self._state_machine.reset()

            # Clear fault-related state
            self._fault_type = None
            self._activation_start_time = None
            self._registers["trip_flag"] = False
            self._registers["status_word"] &= 0xFFFE  # Clear bit 0

            self._log(
                "INFO",
                "Device reset complete",
                {"previous_state": old_state.value, "new_state": self.state.value}
            )
        except InvalidStateTransitionError as e:
            self._log("ERROR", f"Reset failed: {e}")
            raise CommandExecutionError(str(e))

    def inject_fault(self, fault_type: str = "overcurrent") -> None:
        """
        Inject a fault into the device.

        Args:
            fault_type: Type of fault (overcurrent, overvoltage, temperature, etc.)

        Raises:
            CommandExecutionError: If fault injection fails
        """
        self._log(
            "WARNING",
            f"Fault injection: {fault_type}",
            {"current_state": self.state.value}
        )

        # Simulate fault detection delay
        time.sleep(self.FAULT_DETECTION_DELAY)

        try:
            old_state = self.state
            self._state_machine.inject_fault()
            self._fault_type = fault_type

            # Update registers based on fault type
            self._registers["trip_flag"] = True
            self._registers["trip_count"] += 1
            self._registers["status_word"] |= 0x0080  # Set bit 7 for FAULT

            if fault_type == "overcurrent":
                self._registers["current"] = 999.9  # Abnormally high
            elif fault_type == "overvoltage":
                self._registers["voltage"] = 500.0  # Abnormally high
            elif fault_type == "temperature":
                self._registers["temperature"] = 95.0  # Critical temperature

            self._log(
                "ERROR",
                f"Fault condition detected: {fault_type}",
                {
                    "previous_state": old_state.value,
                    "new_state": self.state.value,
                    "fault_type": fault_type
                }
            )
        except InvalidStateTransitionError as e:
            self._log("ERROR", f"Fault injection failed: {e}")
            raise CommandExecutionError(str(e))

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive device status.

        Returns:
            Dictionary with state, registers, and fault info
        """
        return {
            "state": self.state.value,
            "registers": self.registers,
            "fault_active": self._state_machine.fault_active,
            "fault_type": self._fault_type,
            "log_count": len(self._logs),
        }

    def clear_logs(self) -> None:
        """Clear all log entries."""
        self._logs.clear()
        self._log("INFO", "Logs cleared")
