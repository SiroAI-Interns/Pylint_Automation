# Autoencoder - Automated Pylint Error Fixer

An automated tool that fixes pylint errors in Python codebases based on configurable rules.

## Features

- 🔧 Automatically fixes pylint errors
- 🐫 Supports camelCase naming convention
- 🔄 **NEW: Converts snake_case → camelCase automatically**
- 📦 Uses autopep8, isort, autoflake under the hood
- ⚙️ Generates custom `.pylintrc` based on your rules

## Installation

```bash
cd Autoencoder
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py --path /path/to/your/codebase --naming camelCase
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path` | Path to the codebase to fix | Required |
| `--naming` | Naming convention: `camelCase` or `snake_case` | `camelCase` |
| `--fix-imports` | Fix import order issues | `True` |
| `--fix-whitespace` | Fix whitespace issues | `True` |
| `--fix-unused` | Remove unused imports/variables | `True` |
| `--fix-naming` | ⚠️ Convert snake_case to camelCase (RISKY) | `False` |
| `--generate-pylintrc` | Generate a .pylintrc file | `True` |

### Example

```bash
# Fix a codebase with camelCase naming (converts snake_case automatically!)
python main.py --path C:\MyProject\app --naming camelCase

# Only generate pylintrc without fixing
python main.py --path C:\MyProject\app --naming camelCase --fix-imports False --fix-whitespace False --fix-unused False
```

## How It Works

1. **Generates `.pylintrc`** - Creates a pylint configuration file based on your naming rules
2. **Runs isort** - Fixes import order issues
3. **Runs autopep8** - Fixes whitespace, indentation, line length
4. **Runs autoflake** - Removes unused imports and variables
5. **Converts naming** - **Detects snake_case and converts to camelCase** (or vice versa)
6. **Runs pylint** - Validates the fixes and shows remaining issues

## What Gets Fixed

| Issue Type | Tool Used | Example |
|------------|-----------|---------|
| Import order | isort | Sorts imports alphabetically |
| Whitespace | autopep8 | Removes trailing spaces |
| Line length | autopep8 | Breaks long lines |
| Unused imports | autoflake | Removes `import json` if unused |
| **snake_case names** | naming_converter | `my_variable` → `myVariable` |
| **Mixed case names** | naming_converter | `json_Block` → `jsonBlock` |

## Naming Conversion Examples

```python
# BEFORE (snake_case)
user_name = "John"
get_user_data()
total_count = 10

# AFTER (camelCase)
userName = "John"
getUserData()
totalCount = 10
```

## What's NOT Fixed (Requires Manual Fix)

- Syntax errors (unterminated strings, etc.)
- Logic bugs (missing arguments, duplicate functions)
- Design issues (too many arguments, etc.)

## ⚠️ Warning: Naming Conversion is RISKY

The `--fix-naming` flag is **disabled by default** because:

1. It converts names in **one file** but may miss references in **other files**
2. This can cause `undefined-variable` errors across the codebase
3. It may break imports, function calls, and attribute access

**Only use `--fix-naming` if:**
- Your codebase is small
- You have good test coverage
- You can manually verify the changes

## License

MIT
