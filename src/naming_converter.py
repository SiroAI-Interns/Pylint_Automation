"""Naming convention converter for Autoencoder."""
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from colorama import Fore, Style


class NamingConverter:
    """Converts variable names between snake_case and camelCase."""

    def __init__(self, naming_convention: str = "camelCase"):
        """Initialize the naming converter."""
        self.naming_convention = naming_convention
        # Track all conversions made
        self.conversions: Dict[str, str] = {}
        # Reserved Python keywords and builtins to skip
        self.reserved = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'self', 'cls', '__init__', '__name__',
            '__main__', '__file__', '__doc__', '__dict__', '__class__',
            '__str__', '__repr__', '__len__', '__getitem__', '__setitem__',
            '__delitem__', '__iter__', '__next__', '__call__', '__enter__',
            '__exit__', '__eq__', '__ne__', '__lt__', '__le__', '__gt__',
            '__ge__', '__hash__', '__bool__', '__contains__', '__add__',
            '__sub__', '__mul__', '__truediv__', '__floordiv__', '__mod__',
            '__pow__', '__and__', '__or__', '__xor__', '__lshift__', '__rshift__',
            '__neg__', '__pos__', '__abs__', '__invert__', '__complex__',
            '__int__', '__float__', '__round__', '__index__', '__new__',
        }
        # Common library variables to skip
        self.skip_patterns = {
            r'^_.*',  # Private variables starting with _
            r'^__.*__$',  # Dunder methods
            r'^[A-Z][A-Z0-9_]*$',  # CONSTANTS
        }

    def snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        if not name or name in self.reserved:
            return name
        
        # Skip if matches skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, name):
                return name
        
        # Skip private variables (start with _)
        if name.startswith('_'):
            return name
        
        # Check if it contains underscore (snake_case or mixed)
        if '_' not in name:
            return name
        
        # Split by underscore
        parts = name.split('_')
        if len(parts) == 1:
            return name
        
        # Convert: first part lowercase, rest with first letter capitalized
        # PRESERVE existing capitalization within each part!
        result = parts[0].lower()
        for part in parts[1:]:
            if part:  # Skip empty parts from multiple underscores
                # Capitalize first letter, KEEP the rest as-is
                result += part[0].upper() + part[1:] if len(part) > 1 else part.upper()
        
        return result

    def camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        if not name or name in self.reserved:
            return name
        
        # Skip if matches skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, name):
                return name
        
        # Insert underscore before uppercase letters and convert to lowercase
        result = re.sub(r'([A-Z])', r'_\1', name).lower()
        # Remove leading underscore if present
        if result.startswith('_'):
            result = result[1:]
        return result

    def should_convert(self, name: str) -> bool:
        """Check if a name should be converted."""
        if not name or name in self.reserved:
            return False
        
        # Skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, name):
                return False
        
        if self.naming_convention == "camelCase":
            # Should convert if it's snake_case (contains underscore in middle)
            # Also convert mixed cases like json_Block
            if '_' in name and not name.startswith('__'):
                # Make sure it's not a constant (all caps)
                if not re.match(r'^[A-Z][A-Z0-9_]*$', name):
                    return True
        else:  # snake_case
            # Should convert if it's camelCase (has uppercase after lowercase)
            if re.search(r'[a-z][A-Z]', name):
                return True
        
        return False

    def convert_name(self, name: str) -> str:
        """Convert a name based on the naming convention."""
        if not self.should_convert(name):
            return name
        
        if self.naming_convention == "camelCase":
            return self.snake_to_camel(name)
        else:
            return self.camel_to_snake(name)

    def find_names_in_file(self, filepath: Path) -> Set[str]:
        """Find all variable/function names in a Python file."""
        names = set()
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Variable assignments
                if isinstance(node, ast.Name):
                    names.add(node.id)
                # Function definitions
                elif isinstance(node, ast.FunctionDef):
                    names.add(node.name)
                    for arg in node.args.args:
                        names.add(arg.arg)
                # Async function definitions
                elif isinstance(node, ast.AsyncFunctionDef):
                    names.add(node.name)
                    for arg in node.args.args:
                        names.add(arg.arg)
                # Attribute access
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                    
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception:
            pass
        
        return names

    def convert_file(self, filepath: Path) -> Tuple[int, Dict[str, str]]:
        """
        Convert naming conventions in a single file.
        Returns: (number of conversions, dict of old->new names)
        """
        conversions = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Find all names that need conversion
            names = self.find_names_in_file(filepath)
            
            for name in names:
                # Skip empty names or very short names
                if not name or len(name) < 2:
                    continue
                if self.should_convert(name):
                    new_name = self.convert_name(name)
                    # Only add if conversion is valid and different
                    if new_name and new_name != name and len(new_name) >= 2:
                        conversions[name] = new_name
            
            # Sort by length (longest first) to avoid partial replacements
            sorted_conversions = sorted(conversions.items(), key=lambda x: len(x[0]), reverse=True)
            
            # Apply conversions using word boundary regex
            for old_name, new_name in sorted_conversions:
                # Use word boundaries to avoid partial replacements
                # Only replace if it's a standalone identifier (not part of string or comment)
                pattern = r'(?<!["\'])\b' + re.escape(old_name) + r'\b(?!["\'])'
                content = re.sub(pattern, new_name, content)
            
            # SAFETY CHECK: Verify the file is still valid Python
            try:
                ast.parse(content)
            except SyntaxError:
                # If conversion broke the file, don't save
                print(f"    {Fore.RED}⚠️  Skipping {filepath.name} - conversion would break syntax{Style.RESET_ALL}")
                return 0, {}
            
            # Only write if changes were made
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
        except Exception as e:
            pass
        
        return len(conversions), conversions

    def convert_directory(self, directory: Path) -> Tuple[int, int, Dict[str, str]]:
        """
        Convert naming conventions in all Python files in a directory.
        Returns: (files_processed, total_conversions, all_conversions)
        """
        files_processed = 0
        total_conversions = 0
        all_conversions = {}
        
        # Find all Python files
        python_files = list(directory.rglob("*.py"))
        
        for filepath in python_files:
            # Skip __pycache__ and other hidden directories
            if '__pycache__' in str(filepath) or '/.git/' in str(filepath):
                continue
            
            count, conversions = self.convert_file(filepath)
            if count > 0:
                files_processed += 1
                total_conversions += count
                all_conversions.update(conversions)
        
        return files_processed, total_conversions, all_conversions


def fix_naming(codebase_path: Path, naming_convention: str = "camelCase") -> Tuple[int, int]:
    """
    Fix naming conventions in a codebase.
    Returns: (files_fixed, total_conversions)
    """
    print(f"  {Fore.YELLOW}→ Converting to {naming_convention}...{Style.RESET_ALL}")
    
    converter = NamingConverter(naming_convention)
    files_fixed, total_conversions, conversions = converter.convert_directory(codebase_path)
    
    if total_conversions > 0:
        print(f"    {Fore.GREEN}✅ Converted {total_conversions} names in {files_fixed} files{Style.RESET_ALL}")
        # Show some examples (max 5)
        examples = list(conversions.items())[:5]
        for old, new in examples:
            print(f"       {Fore.YELLOW}{old}{Style.RESET_ALL} → {Fore.GREEN}{new}{Style.RESET_ALL}")
        if len(conversions) > 5:
            print(f"       ... and {len(conversions) - 5} more")
    else:
        print(f"    {Fore.GREEN}✅ No naming conversions needed{Style.RESET_ALL}")
    
    return files_fixed, total_conversions

