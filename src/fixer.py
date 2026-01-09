"""Code fixer module for Autoencoder."""
import subprocess
import sys
from pathlib import Path
from typing import Optional

from colorama import Fore, Style

from .config import Config
from .naming_converter import fix_naming
from .dynamic_config import NamingPreferences, DynamicConfig
from .dynamic_naming_converter import fix_naming_dynamic


class CodeFixer:
    """Applies automated fixes to the codebase."""

    def __init__(self, config: Config, naming_preferences: Optional[NamingPreferences] = None):
        """Initialize the fixer with configuration."""
        self.config = config
        self.naming_preferences = naming_preferences

    def fix_all(self) -> None:
        """Apply all configured fixes."""
        if self.config.fix_imports:
            self._fix_imports()

        if self.config.fix_whitespace:
            self._fix_whitespace()

        if self.config.fix_unused:
            self._fix_unused()

        # Naming conversion
        if self.config.fix_naming:
            self._fix_naming()

    def _fix_naming(self) -> None:
        """Fix naming conventions."""
        if self.naming_preferences:
            # Use dynamic naming with per-type preferences
            print(f"  {Fore.YELLOW}⚠️  Converting names (dynamic mode with syntax validation)...{Style.RESET_ALL}")
            fix_naming_dynamic(self.config.codebase_path, self.naming_preferences)
        else:
            # Fall back to legacy single-convention mode
            print(f"  {Fore.YELLOW}⚠️  Converting names (legacy mode with syntax validation)...{Style.RESET_ALL}")
            fix_naming(self.config.codebase_path, self.config.naming_convention)

    def _fix_imports(self) -> None:
        """Fix import order using isort."""
        print(f"  {Fore.YELLOW}→ Running isort (fixing import order)...{Style.RESET_ALL}")
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "isort",
                    str(self.config.codebase_path),
                    "--profile", "black",
                    "--quiet"
                ],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"    {Fore.GREEN}✅ Import order fixed{Style.RESET_ALL}")
            else:
                print(f"    {Fore.YELLOW}⚠️  isort completed with warnings{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"    {Fore.RED}❌ isort not found. Install with: pip install isort{Style.RESET_ALL}")

    def _fix_whitespace(self) -> None:
        """Fix whitespace and formatting using autopep8."""
        print(f"  {Fore.YELLOW}→ Running autopep8 (fixing whitespace/formatting)...{Style.RESET_ALL}")
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "autopep8",
                    "--in-place",
                    "--recursive",
                    f"--max-line-length={self.config.max_line_length}",
                    "--aggressive",
                    "--aggressive",
                    str(self.config.codebase_path)
                ],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"    {Fore.GREEN}✅ Whitespace and formatting fixed{Style.RESET_ALL}")
            else:
                print(f"    {Fore.YELLOW}⚠️  autopep8 completed with warnings{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"    {Fore.RED}❌ autopep8 not found. Install with: pip install autopep8{Style.RESET_ALL}")

    def _fix_unused(self) -> None:
        """Remove unused imports and variables using autoflake."""
        print(f"  {Fore.YELLOW}→ Running autoflake (removing unused imports)...{Style.RESET_ALL}")
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "autoflake",
                    "--in-place",
                    "--recursive",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(self.config.codebase_path)
                ],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"    {Fore.GREEN}✅ Unused imports/variables removed{Style.RESET_ALL}")
            else:
                print(f"    {Fore.YELLOW}⚠️  autoflake completed with warnings{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"    {Fore.RED}❌ autoflake not found. Install with: pip install autoflake{Style.RESET_ALL}")
