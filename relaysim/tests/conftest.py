"""
Pytest fixtures for Relaysim tests.
"""

import pytest
from pathlib import Path

from simulator import DeviceSimulator
from runner import YAMLScenarioLoader, TestRunner


@pytest.fixture
def device():
    """Create a fresh device simulator for each test."""
    return DeviceSimulator()


@pytest.fixture
def runner(device):
    """Create a test runner with a fresh device."""
    return TestRunner(device)


@pytest.fixture
def scenario_loader():
    """Create a YAML scenario loader."""
    return YAMLScenarioLoader()


@pytest.fixture
def scenarios_dir():
    """Get the path to the example scenarios directory."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "config" / "examples"
