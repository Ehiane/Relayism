"""
Report generation for test scenario results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..runner import ScenarioResult
from ..utils import get_logger

logger = get_logger()


class ReportGenerator:
    """Generates reports from scenario results."""

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for saving reports (defaults to ./reports)
        """
        if output_dir is None:
            # Default to reports/ in project root
            base_dir = Path(__file__).parent.parent.parent
            output_dir = base_dir / "reports"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(
        self,
        result: ScenarioResult,
        filename: Optional[str] = None
    ) -> Path:
        """
        Generate a JSON report for a scenario result.

        Args:
            result: Scenario result to report
            filename: Optional custom filename (auto-generated if not provided)

        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{result.scenario_name}_{timestamp}.json"

        report_path = self.output_dir / filename

        report_data = result.to_dict()

        # Add report metadata
        report_data["report_generated_at"] = datetime.now().isoformat()
        report_data["report_version"] = "1.0"

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"JSON report generated: {report_path}")
        return report_path

    def generate_summary(self, result: ScenarioResult) -> str:
        """
        Generate a human-readable summary of a scenario result.

        Args:
            result: Scenario result to summarize

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"SCENARIO: {result.scenario_name}")
        if result.description:
            lines.append(f"Description: {result.description}")
        lines.append("=" * 70)
        lines.append("")

        # Overall status
        status_symbol = {
            "passed": "✓ PASSED",
            "failed": "✗ FAILED",
            "error": "⚠ ERROR",
            "running": "⋯ RUNNING",
        }
        lines.append(f"Status: {status_symbol.get(result.overall_status, result.overall_status)}")

        # Timing
        lines.append(f"Duration: {result.duration_seconds:.3f}s")
        start_dt = datetime.fromtimestamp(result.start_time).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"Started: {start_dt}")

        # Step summary
        lines.append(f"\nSteps: {result.passed_steps}/{len(result.step_results)} passed")
        if result.failed_steps > 0:
            lines.append(f"Failed: {result.failed_steps}")

        # Error message if any
        if result.error_message:
            lines.append(f"\nError: {result.error_message}")

        lines.append("")
        lines.append("-" * 70)
        lines.append("STEP DETAILS:")
        lines.append("-" * 70)

        # Step details
        for step_result in result.step_results:
            status_icon = "✓" if step_result.status == "pass" else "✗"
            lines.append(
                f"  [{status_icon}] Step {step_result.step_number}: {step_result.step_type} "
                f"({step_result.duration_ms:.1f}ms)"
            )
            if step_result.message and step_result.status != "pass":
                lines.append(f"      Message: {step_result.message}")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_batch_summary(self, results: list[ScenarioResult]) -> str:
        """
        Generate a summary for multiple scenario results.

        Args:
            results: List of scenario results

        Returns:
            Formatted batch summary string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("BATCH TEST SUMMARY")
        lines.append("=" * 70)
        lines.append("")

        total_scenarios = len(results)
        passed_scenarios = sum(1 for r in results if r.overall_status == "passed")
        failed_scenarios = sum(1 for r in results if r.overall_status == "failed")
        error_scenarios = sum(1 for r in results if r.overall_status == "error")

        lines.append(f"Total scenarios: {total_scenarios}")
        lines.append(f"Passed: {passed_scenarios}")
        lines.append(f"Failed: {failed_scenarios}")
        lines.append(f"Errors: {error_scenarios}")
        lines.append("")

        # Individual scenario status
        lines.append("-" * 70)
        for result in results:
            status_symbol = {
                "passed": "✓",
                "failed": "✗",
                "error": "⚠",
            }
            symbol = status_symbol.get(result.overall_status, "?")
            lines.append(
                f"  [{symbol}] {result.scenario_name} "
                f"({result.duration_seconds:.3f}s, "
                f"{result.passed_steps}/{len(result.step_results)} steps)"
            )

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def save_text_report(self, result: ScenarioResult, filename: Optional[str] = None) -> Path:
        """
        Save a text summary report to a file.

        Args:
            result: Scenario result
            filename: Optional custom filename

        Returns:
            Path to the saved report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{result.scenario_name}_{timestamp}.txt"

        report_path = self.output_dir / filename

        summary = self.generate_summary(result)

        with open(report_path, "w") as f:
            f.write(summary)

        logger.info(f"Text report saved: {report_path}")
        return report_path
