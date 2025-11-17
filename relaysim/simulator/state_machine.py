"""
State machine for device simulator.

Manages valid state transitions for a safety-critical relay device.
"""

from enum import Enum
from typing import Optional


class DeviceState(Enum):
    """Valid states for the device."""
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    FAULT = "FAULT"


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachine:
    """
    Manages device state transitions with strict validation rules.

    Transition rules:
    - IDLE -> ACTIVE (via activate command)
    - ACTIVE -> IDLE (via reset command)
    - Any state -> FAULT (via fault injection)
    - FAULT -> IDLE (via reset command, only after fault is cleared)
    """

    # Valid transitions: (from_state, to_state) -> required_condition
    VALID_TRANSITIONS = {
        (DeviceState.IDLE, DeviceState.ACTIVE): "activation_requested",
        (DeviceState.ACTIVE, DeviceState.IDLE): "reset_requested",
        (DeviceState.IDLE, DeviceState.FAULT): "fault_injected",
        (DeviceState.ACTIVE, DeviceState.FAULT): "fault_injected",
        (DeviceState.FAULT, DeviceState.IDLE): "reset_after_fault",
    }

    def __init__(self, initial_state: DeviceState = DeviceState.IDLE):
        """Initialize the state machine."""
        self._current_state = initial_state
        self._fault_active = False

    @property
    def current_state(self) -> DeviceState:
        """Get the current state."""
        return self._current_state

    @property
    def fault_active(self) -> bool:
        """Check if a fault is currently active."""
        return self._fault_active

    def can_transition(self, new_state: DeviceState, condition: Optional[str] = None) -> bool:
        """
        Check if a transition to the new state is valid.

        Args:
            new_state: Target state
            condition: Condition that enables this transition

        Returns:
            True if transition is valid, False otherwise
        """
        if self._current_state == new_state:
            return True  # Already in target state

        transition = (self._current_state, new_state)
        if transition not in self.VALID_TRANSITIONS:
            return False

        required_condition = self.VALID_TRANSITIONS[transition]
        if condition is None:
            return False

        return condition == required_condition

    def transition(self, new_state: DeviceState, condition: str) -> DeviceState:
        """
        Attempt to transition to a new state.

        Args:
            new_state: Target state
            condition: Condition that triggers this transition

        Returns:
            The new state after transition

        Raises:
            InvalidStateTransitionError: If transition is not valid
        """
        if self._current_state == new_state:
            return self._current_state  # Already in target state

        if not self.can_transition(new_state, condition):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self._current_state.value} to {new_state.value} "
                f"with condition '{condition}'"
            )

        old_state = self._current_state
        self._current_state = new_state

        # Update fault status
        if condition == "fault_injected":
            self._fault_active = True
        elif condition == "reset_after_fault" and old_state == DeviceState.FAULT:
            self._fault_active = False

        return self._current_state

    def activate(self) -> DeviceState:
        """Activate the device (IDLE -> ACTIVE)."""
        return self.transition(DeviceState.ACTIVE, "activation_requested")

    def reset(self) -> DeviceState:
        """Reset the device to IDLE state."""
        if self._current_state == DeviceState.FAULT:
            return self.transition(DeviceState.IDLE, "reset_after_fault")
        else:
            return self.transition(DeviceState.IDLE, "reset_requested")

    def inject_fault(self) -> DeviceState:
        """Inject a fault (any state -> FAULT)."""
        return self.transition(DeviceState.FAULT, "fault_injected")
