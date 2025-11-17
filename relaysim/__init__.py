"""
Relaysim - Automated Firmware Test Harness

A production-quality test infrastructure system for simulating and testing
firmware-controlled devices.
"""

__version__ = "1.0.0"
__author__ = "Relaysim Team"

from .simulator import DeviceSimulator, DeviceState, StateMachine
from .runner import TestRunner, YAMLScenarioLoader
from .reports import ReportGenerator

__all__ = [
    "DeviceSimulator",
    "DeviceState",
    "StateMachine",
    "TestRunner",
    "YAMLScenarioLoader",
    "ReportGenerator",
]
