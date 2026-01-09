"""Dynamic configuration module for per-type naming conventions."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Literal, Optional

# Supported naming conventions
NamingStyle = Literal["snake_case", "camelCase", "PascalCase", "SCREAMING_SNAKE_CASE"]


@dataclass
class NamingPreferences:
    """
    User preferences for naming conventions per identifier type.
    
    Supported styles:
    - snake_case: my_variable_name
    - camelCase: myVariableName
    - PascalCase: MyClassName (also called CapitalCase)
    - SCREAMING_SNAKE_CASE: MY_CONSTANT
    """
    
    variables: NamingStyle = "snake_case"
    functions: NamingStyle = "camelCase"
    classes: NamingStyle = "PascalCase"
    constants: NamingStyle = "SCREAMING_SNAKE_CASE"
    methods: NamingStyle = "camelCase"
    arguments: NamingStyle = "snake_case"
    attributes: NamingStyle = "snake_case"
    
    # Additional options
    preserve_private: bool = True  # Don't touch _private or __dunder__
    preserve_constants: bool = True  # Don't touch ALL_CAPS names
    
    @classmethod
    def from_dict(cls, data: Dict) -> "NamingPreferences":
        """Create NamingPreferences from a dictionary."""
        valid_styles = {"snake_case", "camelCase", "PascalCase", "SCREAMING_SNAKE_CASE"}
        
        # Validate styles
        for key in ["variables", "functions", "classes", "constants", "methods", "arguments", "attributes"]:
            if key in data and data[key] not in valid_styles:
                raise ValueError(f"Invalid naming style '{data[key]}' for {key}. Must be one of: {valid_styles}")
        
        return cls(
            variables=data.get("variables", "snake_case"),
            functions=data.get("functions", "camelCase"),
            classes=data.get("classes", "PascalCase"),
            constants=data.get("constants", "SCREAMING_SNAKE_CASE"),
            methods=data.get("methods", "camelCase"),
            arguments=data.get("arguments", "snake_case"),
            attributes=data.get("attributes", "snake_case"),
            preserve_private=data.get("preserve_private", True),
            preserve_constants=data.get("preserve_constants", True),
        )
    
    @classmethod
    def from_json_file(cls, filepath: Path) -> "NamingPreferences":
        """Load preferences from a JSON configuration file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data.get("naming_preferences", data))
    
    def to_dict(self) -> Dict:
        """Convert preferences to dictionary."""
        return {
            "variables": self.variables,
            "functions": self.functions,
            "classes": self.classes,
            "constants": self.constants,
            "methods": self.methods,
            "arguments": self.arguments,
            "attributes": self.attributes,
            "preserve_private": self.preserve_private,
            "preserve_constants": self.preserve_constants,
        }
    
    def save_to_json(self, filepath: Path) -> None:
        """Save preferences to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"naming_preferences": self.to_dict()}, f, indent=2)


@dataclass 
class DynamicConfig:
    """Extended configuration with dynamic naming preferences."""
    
    codebase_path: Path
    naming_preferences: NamingPreferences = field(default_factory=NamingPreferences)
    fix_imports: bool = True
    fix_whitespace: bool = True
    fix_unused: bool = True
    fix_naming: bool = True
    generate_pylintrc: bool = True
    max_line_length: int = 100
    
    @classmethod
    def from_config_file(cls, codebase_path: Path, config_file: Path) -> "DynamicConfig":
        """Create configuration from a JSON config file."""
        preferences = NamingPreferences.from_json_file(config_file)
        return cls(
            codebase_path=codebase_path,
            naming_preferences=preferences,
        )


# Preset configurations for common conventions
PRESETS = {
    "python_standard": NamingPreferences(
        variables="snake_case",
        functions="snake_case",
        classes="PascalCase",
        constants="SCREAMING_SNAKE_CASE",
        methods="snake_case",
        arguments="snake_case",
        attributes="snake_case",
    ),
    "java_style": NamingPreferences(
        variables="camelCase",
        functions="camelCase",
        classes="PascalCase",
        constants="SCREAMING_SNAKE_CASE",
        methods="camelCase",
        arguments="camelCase",
        attributes="camelCase",
    ),
    "mixed_style": NamingPreferences(
        variables="snake_case",
        functions="camelCase",
        classes="PascalCase",
        constants="SCREAMING_SNAKE_CASE",
        methods="camelCase",
        arguments="snake_case",
        attributes="snake_case",
    ),
}
