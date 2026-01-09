# Autoencoder - Automated Pylint Error Fixer

An automated tool that fixes pylint errors in Python codebases based on configurable rules.

## Features

- 🔧 Automatically fixes pylint errors
- 🎯 **NEW: Dynamic Naming Conventions** - Set different styles for variables, functions, and classes!
- 🐫 Supports camelCase, snake_case, PascalCase, SCREAMING_SNAKE_CASE
- 🔄 Converts naming automatically based on your preferences
- 📦 Uses autopep8, isort, autoflake under the hood
- ⚙️ Generates custom `.pylintrc` based on your rules

## Installation

```bash
cd Autoencoder
pip install -r requirements.txt
```

## Usage

### Dynamic Naming (Recommended)

Specify different naming conventions for different identifier types:

```bash
# Variables: snake_case | Functions: camelCase | Classes: PascalCase
python main.py --path ./myproject --var-naming snake_case --func-naming camelCase --class-naming PascalCase
```

### Using Presets

```bash
# Python standard (PEP8 style)
python main.py --path ./myproject --preset python_standard

# Java style
python main.py --path ./myproject --preset java_style

# Mixed style (what you asked for!)
python main.py --path ./myproject --preset mixed_style
```

### Using Config File

```bash
python main.py --path ./myproject --config naming_config.json
```

### Legacy Mode (Single Convention)

```bash
python main.py --path /path/to/your/codebase --naming camelCase
```

## Dynamic Naming Options

| Option | Description | Default |
|--------|-------------|---------|
| `--var-naming` | Naming style for variables | `snake_case` |
| `--func-naming` | Naming style for functions | `camelCase` |
| `--class-naming` | Naming style for classes | `PascalCase` |
| `--method-naming` | Naming style for methods | `camelCase` |
| `--arg-naming` | Naming style for arguments | `snake_case` |
| `--config` | Path to JSON config file | - |
| `--preset` | Use a preset: `python_standard`, `java_style`, `mixed_style` | - |

## Available Naming Styles

| Style | Example | Best For |
|-------|---------|----------|
| `snake_case` | `my_variable_name` | Variables, arguments |
| `camelCase` | `myVariableName` | Functions, methods |
| `PascalCase` | `MyClassName` | Classes |
| `SCREAMING_SNAKE_CASE` | `MY_CONSTANT` | Constants |

## Available Presets

### `python_standard` (PEP8)
```
Variables:  snake_case
Functions:  snake_case
Classes:    PascalCase
Constants:  SCREAMING_SNAKE_CASE
```

### `java_style`
```
Variables:  camelCase
Functions:  camelCase
Classes:    PascalCase
Constants:  SCREAMING_SNAKE_CASE
```

### `mixed_style` (Your Request!)
```
Variables:  snake_case
Functions:  camelCase
Classes:    PascalCase
Constants:  SCREAMING_SNAKE_CASE
```

## Config File Format

Create a `naming_config.json`:

```json
{
  "naming_preferences": {
    "variables": "snake_case",
    "functions": "camelCase",
    "classes": "PascalCase",
    "methods": "camelCase",
    "arguments": "snake_case",
    "attributes": "snake_case",
    "constants": "SCREAMING_SNAKE_CASE",
    "preserve_private": true,
    "preserve_constants": true
  }
}
```

## Other Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path` | Path to the codebase to fix | Required |
| `--fix-imports` | Fix import order issues | `True` |
| `--fix-whitespace` | Fix whitespace issues | `True` |
| `--fix-unused` | Remove unused imports/variables | `True` |
| `--fix-naming` | Apply naming convention fixes | `True` |
| `--generate-pylintrc` | Generate a .pylintrc file | `True` |
| `--max-line-length` | Maximum line length | `100` |

## Example: Dynamic Naming in Action

### Before
```python
class user_manager:
    def Get_User_Data(self, UserId):
        user_name = "John"
        UserAge = 25
        return user_name, UserAge
    
def processData(input_data):
    result_value = input_data * 2
    return result_value
```

### After (with `--var-naming snake_case --func-naming camelCase --class-naming PascalCase`)
```python
class UserManager:
    def getUserData(self, user_id):
        user_name = "John"
        user_age = 25
        return user_name, user_age
    
def processData(input_data):
    result_value = input_data * 2
    return result_value
```

## How It Works

1. **Generates `.pylintrc`** - Creates a pylint configuration file
2. **Runs isort** - Fixes import order issues
3. **Runs autopep8** - Fixes whitespace, indentation, line length
4. **Runs autoflake** - Removes unused imports and variables
5. **Dynamic Naming Conversion** - Detects identifier types and converts based on preferences
6. **Runs pylint** - Validates the fixes and shows remaining issues

## What Gets Fixed

| Issue Type | Tool Used | Example |
|------------|-----------|---------|
| Import order | isort | Sorts imports alphabetically |
| Whitespace | autopep8 | Removes trailing spaces |
| Line length | autopep8 | Breaks long lines |
| Unused imports | autoflake | Removes `import json` if unused |
| **Variable names** | dynamic_converter | Based on `--var-naming` |
| **Function names** | dynamic_converter | Based on `--func-naming` |
| **Class names** | dynamic_converter | Based on `--class-naming` |


- Syntax errors (unterminated strings, etc.)
- Logic bugs (missing arguments, duplicate functions)
- Design issues (too many arguments, etc.)
- External library references

## ⚠️ Important Notes

1. **Backup your code** before running with naming fixes
2. Private variables (`_private`) and dunder methods (`__init__`) are preserved
3. Constants (`ALL_CAPS`) are preserved by default
4. External library names are not modified

**Only use `--fix-naming` if:**
- Your codebase is small
- You have good test coverage
- You can manually verify the changes

## License

MIT
