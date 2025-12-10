"""Configuration module for Autoencoder."""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Config:
    """Configuration for the Autoencoder tool."""

    codebase_path: Path
    naming_convention: Literal["camelCase", "snake_case"] = "camelCase"
    fix_imports: bool = True
    fix_whitespace: bool = True
    fix_unused: bool = True
    fix_naming: bool = False  # DISABLED - can break external library calls
    generate_pylintrc: bool = True
    max_line_length: int = 100

    def get_variable_regex(self) -> str:
        """Get the regex pattern for variable names based on naming convention."""
        if self.naming_convention == "camelCase":
            # STRICT: Only camelCase (no underscores except for CONSTANTS)
            # Also allow single letter vars (i, j, x, etc.) and UPPER_CASE constants
            return r"[a-z][a-zA-Z0-9]*$|[A-Z][A-Z0-9_]*$|[a-z]$"
        else:
            # snake_case only (no uppercase in middle)
            return r"[a-z_][a-z0-9_]*$|[A-Z_][A-Z0-9_]*$"

    def get_function_regex(self) -> str:
        """Get the regex pattern for function names based on naming convention."""
        if self.naming_convention == "camelCase":
            # STRICT: camelCase only (no underscores)
            return r"[a-z][a-zA-Z0-9]*$"
        else:
            return r"[a-z_][a-z0-9_]*$"

    def get_method_regex(self) -> str:
        """Get the regex pattern for method names based on naming convention."""
        if self.naming_convention == "camelCase":
            # STRICT: camelCase only (no underscores), but allow dunder methods
            return r"[a-z][a-zA-Z0-9]*$|__[a-z_]+__$"
        else:
            return r"[a-z_][a-z0-9_]*$"

    def get_argument_regex(self) -> str:
        """Get the regex pattern for argument names based on naming convention."""
        if self.naming_convention == "camelCase":
            # STRICT: camelCase only
            return r"[a-z][a-zA-Z0-9]*$"
        else:
            return r"[a-z_][a-z0-9_]*$"

    def get_attr_regex(self) -> str:
        """Get the regex pattern for attribute names based on naming convention."""
        if self.naming_convention == "camelCase":
            # STRICT: camelCase or UPPER_CASE constants
            return r"[a-z][a-zA-Z0-9]*$|[A-Z][A-Z0-9_]*$"
        else:
            return r"[a-z_][a-z0-9_]*$|[A-Z_][A-Z0-9_]*$"

    def get_const_regex(self) -> str:
        """Get the regex pattern for constant names."""
        # Constants are always UPPER_CASE
        return r"[A-Z][A-Z0-9_]*$"

    def get_class_regex(self) -> str:
        """Get the regex pattern for class names (always PascalCase)."""
        return r"[A-Z][a-zA-Z0-9]*$"

    def get_class_attribute_regex(self) -> str:
        """Get the regex pattern for class attribute names."""
        if self.naming_convention == "camelCase":
            # STRICT: camelCase or UPPER_CASE constants
            return r"[a-z][a-zA-Z0-9]*$|[A-Z][A-Z0-9_]*$"
        else:
            return r"[a-z_][a-z0-9_]*$|[A-Z_][A-Z0-9_]*$"

