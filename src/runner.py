"""Pylint runner module for Autoencoder."""
import re
import subprocess
import sys

from colorama import Fore, Style

from .config import Config


class PylintRunner:
    """Runs pylint and parses the output."""

    def __init__(self, config: Config):
        """Initialize the runner with configuration."""
        self.config = config

    def run_and_count(self) -> int:
        """Run pylint and return the error count."""
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pylint",
                    str(self.config.codebase_path),
                    "--output-format=text"
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace"
            )

            output = result.stdout + result.stderr

            # Count errors by counting lines that match the pattern
            # Format: file.py:line:col: CODE: message
            error_pattern = r"\.py:\d+:\d+: [CWERF]\d+"
            matches = re.findall(error_pattern, output)
            error_count = len(matches)

            # Also check for the score line
            score_match = re.search(r"Your code has been rated at ([\d.]+)/10", output)
            if score_match:
                score = float(score_match.group(1))
                print(f"  📈 Pylint Score: {score}/10")

            return error_count

        except FileNotFoundError:
            print(f"    {Fore.RED}❌ pylint not found. Install with: pip install pylint{Style.RESET_ALL}")
            return -1
        except Exception as e:
            print(f"    {Fore.RED}❌ Error running pylint: {e}{Style.RESET_ALL}")
            return -1

    def run_full_report(self) -> str:
        """Run pylint and return the full output."""
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pylint",
                    str(self.config.codebase_path),
                    "--output-format=text"
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace"
            )

            return result.stdout + result.stderr

        except Exception as e:
            return f"Error running pylint: {e}"

