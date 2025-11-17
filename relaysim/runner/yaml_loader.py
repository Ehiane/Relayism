"""
YAML scenario loader for test scenarios.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..utils import get_logger

logger = get_logger()


class ScenarioLoadError(Exception):
    """Raised when a scenario file cannot be loaded."""
    pass


class ScenarioValidationError(Exception):
    """Raised when a scenario has invalid structure."""
    pass


class YAMLScenarioLoader:
    """Loads and validates YAML test scenarios."""

    VALID_STEP_TYPES = {"write", "command", "wait", "assert"}

    REQUIRED_FIELDS = {
        "write": ["register", "value"],
        "command": ["action"],
        "wait": ["ms"],
        "assert": ["register"],  # Also needs one of: equals, greater_than, less_than, etc.
    }

    def __init__(self, scenarios_dir: Optional[str] = None):
        """
        Initialize the loader.

        Args:
            scenarios_dir: Directory containing scenario YAML files
        """
        if scenarios_dir is None:
            # Default to config/examples relative to this file
            base_dir = Path(__file__).parent.parent
            scenarios_dir = base_dir / "config" / "examples"

        self.scenarios_dir = Path(scenarios_dir)

    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Load a single scenario by name.

        Args:
            scenario_name: Name of the scenario (without .yaml extension)

        Returns:
            Dictionary with scenario metadata and steps

        Raises:
            ScenarioLoadError: If file cannot be loaded
            ScenarioValidationError: If scenario structure is invalid
        """
        # Add .yaml extension if not present
        if not scenario_name.endswith(".yaml"):
            scenario_name = f"{scenario_name}.yaml"

        scenario_path = self.scenarios_dir / scenario_name

        if not scenario_path.exists():
            raise ScenarioLoadError(f"Scenario file not found: {scenario_path}")

        logger.debug(f"Loading scenario from {scenario_path}")

        try:
            with open(scenario_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ScenarioLoadError(f"Failed to parse YAML: {e}")
        except Exception as e:
            raise ScenarioLoadError(f"Failed to load scenario: {e}")

        # Extract metadata and steps
        if isinstance(data, dict):
            # New format with metadata
            scenario = {
                "name": data.get("name", scenario_name.replace(".yaml", "")),
                "description": data.get("description", ""),
                "steps": data.get("steps", []),
            }
        elif isinstance(data, list):
            # Legacy format - just steps
            scenario = {
                "name": scenario_name.replace(".yaml", ""),
                "description": "",
                "steps": data,
            }
        else:
            raise ScenarioValidationError("Scenario must be a dictionary or list")

        # Validate steps
        self._validate_steps(scenario["steps"])

        logger.info(f"Loaded scenario '{scenario['name']}' with {len(scenario['steps'])} steps")

        return scenario

    def _validate_steps(self, steps: List[Dict[str, Any]]) -> None:
        """
        Validate scenario steps.

        Args:
            steps: List of step dictionaries

        Raises:
            ScenarioValidationError: If any step is invalid
        """
        if not isinstance(steps, list):
            raise ScenarioValidationError("Steps must be a list")

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ScenarioValidationError(f"Step {i} must be a dictionary")

            if "step" not in step:
                raise ScenarioValidationError(f"Step {i} missing 'step' field")

            step_type = step["step"]
            if step_type not in self.VALID_STEP_TYPES:
                raise ScenarioValidationError(
                    f"Step {i} has invalid type '{step_type}'. "
                    f"Valid types: {self.VALID_STEP_TYPES}"
                )

            # Check required fields
            required = self.REQUIRED_FIELDS.get(step_type, [])
            for field in required:
                if field not in step:
                    raise ScenarioValidationError(
                        f"Step {i} (type '{step_type}') missing required field '{field}'"
                    )

            # Special validation for assert steps
            if step_type == "assert":
                assertion_types = [
                    "equals", "not_equals",
                    "greater_than", "less_than",
                    "greater_or_equal", "less_or_equal",
                    "contains", "in_range"
                ]
                if not any(at in step for at in assertion_types):
                    raise ScenarioValidationError(
                        f"Step {i} (assert) must have at least one assertion type: {assertion_types}"
                    )

    def list_scenarios(self) -> List[Dict[str, str]]:
        """
        List all available scenarios.

        Returns:
            List of dictionaries with scenario metadata
        """
        if not self.scenarios_dir.exists():
            logger.warning(f"Scenarios directory does not exist: {self.scenarios_dir}")
            return []

        scenarios = []
        for yaml_file in self.scenarios_dir.glob("*.yaml"):
            try:
                scenario = self.load_scenario(yaml_file.name)
                scenarios.append({
                    "name": scenario["name"],
                    "description": scenario["description"],
                    "filename": yaml_file.name,
                })
            except Exception as e:
                logger.error(f"Failed to load scenario {yaml_file.name}: {e}")

        return scenarios

    def validate_scenario_file(self, scenario_path: str) -> bool:
        """
        Validate a scenario file without fully loading it.

        Args:
            scenario_path: Path to scenario file

        Returns:
            True if valid, False otherwise
        """
        try:
            self.load_scenario(scenario_path)
            return True
        except (ScenarioLoadError, ScenarioValidationError) as e:
            logger.error(f"Validation failed: {e}")
            return False
