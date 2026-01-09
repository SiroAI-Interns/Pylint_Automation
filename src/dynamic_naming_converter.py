"""
Dynamic Naming Converter - Type-aware naming convention converter.

Detects identifier types (variable, function, class) and applies
user-specified naming conventions to each type independently.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from colorama import Fore, Style

from .dynamic_config import NamingPreferences, NamingStyle


class IdentifierType(Enum):
    """Types of identifiers in Python code."""
    VARIABLE = "variable"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    ARGUMENT = "argument"
    ATTRIBUTE = "attribute"
    CONSTANT = "constant"
    UNKNOWN = "unknown"


@dataclass
class IdentifierInfo:
    """Information about an identifier found in code."""
    name: str
    type: IdentifierType
    line: int
    col: int


class DynamicNamingConverter:
    """
    Converts identifiers based on per-type naming preferences.
    
    Supports:
    - Variables → snake_case, camelCase, PascalCase
    - Functions → snake_case, camelCase, PascalCase
    - Classes → snake_case, camelCase, PascalCase
    - And more...
    """

    # Python reserved keywords and builtins - never convert these
    RESERVED = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield', 'self', 'cls',
        # Common builtins
        'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set',
        'tuple', 'bool', 'type', 'object', 'super', 'isinstance', 'issubclass',
        'hasattr', 'getattr', 'setattr', 'delattr', 'open', 'file', 'input',
        'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum',
        'min', 'max', 'abs', 'round', 'pow', 'divmod', 'hex', 'oct', 'bin',
        'format', 'repr', 'hash', 'id', 'dir', 'vars', 'locals', 'globals',
        'staticmethod', 'classmethod', 'property', 'callable', 'iter', 'next',
        'slice', 'frozenset', 'bytes', 'bytearray', 'memoryview', 'complex',
        'Exception', 'BaseException', 'ValueError', 'TypeError', 'KeyError',
        'IndexError', 'AttributeError', 'ImportError', 'RuntimeError',
        'StopIteration', 'GeneratorExit', 'SystemExit', 'KeyboardInterrupt',
    }

    # Dunder methods pattern
    DUNDER_PATTERN = re.compile(r'^__[a-z_]+__$')
    
    # Constant pattern (ALL_CAPS)
    CONSTANT_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
    
    # Private variable pattern
    PRIVATE_PATTERN = re.compile(r'^_[a-zA-Z_][a-zA-Z0-9_]*$')

    def __init__(self, preferences: NamingPreferences):
        """Initialize with user preferences."""
        self.preferences = preferences
        self.conversions: Dict[str, str] = {}

    # ============== STYLE DETECTION ==============
    
    def detect_style(self, name: str) -> Optional[NamingStyle]:
        """Detect the current naming style of an identifier."""
        if not name or len(name) < 2:
            return None
        
        # SCREAMING_SNAKE_CASE: ALL_CAPS_WITH_UNDERSCORES
        if self.CONSTANT_PATTERN.match(name):
            return "SCREAMING_SNAKE_CASE"
        
        # PascalCase: StartsWithCapitalNoUnderscores
        if name[0].isupper() and '_' not in name and any(c.islower() for c in name):
            return "PascalCase"
        
        # snake_case: lower_with_underscores
        if '_' in name and name.islower():
            return "snake_case"
        
        # camelCase: startsLowerHasCapitals
        if name[0].islower() and any(c.isupper() for c in name) and '_' not in name:
            return "camelCase"
        
        # Pure lowercase (could be snake_case without underscores)
        if name.islower() and '_' not in name:
            return "snake_case"
        
        # Mixed case with underscores (needs conversion)
        if '_' in name:
            return "snake_case"
        
        return None

    # ============== CONVERSION FUNCTIONS ==============

    def to_snake_case(self, name: str) -> str:
        """Convert any naming style to snake_case."""
        if not name:
            return name
        
        # Handle PascalCase and camelCase
        # Insert underscore before capitals (except at start)
        result = re.sub(r'([A-Z])', r'_\1', name)
        
        # Remove leading underscore if created
        if result.startswith('_') and not name.startswith('_'):
            result = result[1:]
        
        # Handle consecutive capitals (e.g., XMLParser -> xml_parser)
        result = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', result)
        
        return result.lower()

    def to_camel_case(self, name: str) -> str:
        """Convert any naming style to camelCase."""
        if not name:
            return name
        
        # If already camelCase, return as-is
        if self.detect_style(name) == "camelCase":
            return name
        
        # Handle snake_case
        if '_' in name:
            parts = name.lower().split('_')
            if not parts:
                return name
            # First part lowercase, rest capitalized
            result = parts[0]
            for part in parts[1:]:
                if part:
                    result += part[0].upper() + part[1:]
            return result
        
        # Handle PascalCase -> camelCase
        if name[0].isupper():
            return name[0].lower() + name[1:]
        
        return name

    def to_pascal_case(self, name: str) -> str:
        """Convert any naming style to PascalCase (CapitalCase)."""
        if not name:
            return name
        
        # If already PascalCase, return as-is
        if self.detect_style(name) == "PascalCase":
            return name
        
        # Handle snake_case
        if '_' in name:
            parts = name.lower().split('_')
            result = ''
            for part in parts:
                if part:
                    result += part[0].upper() + part[1:]
            return result
        
        # Handle camelCase -> PascalCase
        if name[0].islower():
            return name[0].upper() + name[1:]
        
        return name

    def to_screaming_snake_case(self, name: str) -> str:
        """Convert any naming style to SCREAMING_SNAKE_CASE."""
        # First convert to snake_case, then uppercase
        snake = self.to_snake_case(name)
        return snake.upper()

    def convert_to_style(self, name: str, target_style: NamingStyle) -> str:
        """Convert a name to the target naming style."""
        if target_style == "snake_case":
            return self.to_snake_case(name)
        elif target_style == "camelCase":
            return self.to_camel_case(name)
        elif target_style == "PascalCase":
            return self.to_pascal_case(name)
        elif target_style == "SCREAMING_SNAKE_CASE":
            return self.to_screaming_snake_case(name)
        return name

    # ============== IDENTIFIER ANALYSIS ==============

    def should_skip(self, name: str) -> bool:
        """Check if an identifier should be skipped."""
        if not name or len(name) < 2:
            return True
        
        # Skip reserved words
        if name in self.RESERVED:
            return True
        
        # Skip dunder methods
        if self.DUNDER_PATTERN.match(name):
            return True
        
        # Skip private if configured
        if self.preferences.preserve_private and name.startswith('_'):
            return True
        
        # Skip constants if configured
        if self.preferences.preserve_constants and self.CONSTANT_PATTERN.match(name):
            return True
        
        return False

    def get_target_style(self, id_type: IdentifierType) -> NamingStyle:
        """Get the target naming style for an identifier type."""
        style_map = {
            IdentifierType.VARIABLE: self.preferences.variables,
            IdentifierType.FUNCTION: self.preferences.functions,
            IdentifierType.CLASS: self.preferences.classes,
            IdentifierType.METHOD: self.preferences.methods,
            IdentifierType.ARGUMENT: self.preferences.arguments,
            IdentifierType.ATTRIBUTE: self.preferences.attributes,
            IdentifierType.CONSTANT: self.preferences.constants,
        }
        return style_map.get(id_type, "snake_case")

    def needs_conversion(self, name: str, id_type: IdentifierType) -> bool:
        """Check if an identifier needs to be converted."""
        if self.should_skip(name):
            return False
        
        current_style = self.detect_style(name)
        target_style = self.get_target_style(id_type)
        
        return current_style != target_style

    # ============== AST-BASED IDENTIFIER EXTRACTION ==============

    def extract_identifiers(self, filepath: Path) -> List[IdentifierInfo]:
        """Extract all identifiers from a Python file with their types."""
        identifiers = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Track class context for method detection
            class IdentifierVisitor(ast.NodeVisitor):
                def __init__(self, collector):
                    self.collector = collector
                    self.in_class = False
                    self.in_function = False
                
                def visit_ClassDef(self, node):
                    # Class definition
                    self.collector.append(IdentifierInfo(
                        name=node.name,
                        type=IdentifierType.CLASS,
                        line=node.lineno,
                        col=node.col_offset
                    ))
                    
                    # Process class body
                    old_in_class = self.in_class
                    self.in_class = True
                    self.generic_visit(node)
                    self.in_class = old_in_class
                
                def visit_FunctionDef(self, node):
                    # Determine if it's a method or function
                    if self.in_class:
                        id_type = IdentifierType.METHOD
                    else:
                        id_type = IdentifierType.FUNCTION
                    
                    self.collector.append(IdentifierInfo(
                        name=node.name,
                        type=id_type,
                        line=node.lineno,
                        col=node.col_offset
                    ))
                    
                    # Process function arguments
                    for arg in node.args.args:
                        if arg.arg not in ('self', 'cls'):
                            self.collector.append(IdentifierInfo(
                                name=arg.arg,
                                type=IdentifierType.ARGUMENT,
                                line=arg.lineno if hasattr(arg, 'lineno') else node.lineno,
                                col=arg.col_offset if hasattr(arg, 'col_offset') else 0
                            ))
                    
                    # Process function body
                    old_in_function = self.in_function
                    self.in_function = True
                    self.generic_visit(node)
                    self.in_function = old_in_function
                
                def visit_AsyncFunctionDef(self, node):
                    # Same as FunctionDef
                    self.visit_FunctionDef(node)
                
                def visit_Assign(self, node):
                    # Variable assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            # Check if it's a constant (ALL_CAPS)
                            if re.match(r'^[A-Z][A-Z0-9_]*$', name):
                                id_type = IdentifierType.CONSTANT
                            elif self.in_class and not self.in_function:
                                id_type = IdentifierType.ATTRIBUTE
                            else:
                                id_type = IdentifierType.VARIABLE
                            
                            self.collector.append(IdentifierInfo(
                                name=name,
                                type=id_type,
                                line=target.lineno,
                                col=target.col_offset
                            ))
                        elif isinstance(target, ast.Attribute):
                            # self.attribute = value
                            self.collector.append(IdentifierInfo(
                                name=target.attr,
                                type=IdentifierType.ATTRIBUTE,
                                line=target.lineno,
                                col=target.col_offset
                            ))
                    
                    self.generic_visit(node)
                
                def visit_AnnAssign(self, node):
                    # Annotated assignments: x: int = 5
                    if isinstance(node.target, ast.Name):
                        name = node.target.id
                        if re.match(r'^[A-Z][A-Z0-9_]*$', name):
                            id_type = IdentifierType.CONSTANT
                        elif self.in_class and not self.in_function:
                            id_type = IdentifierType.ATTRIBUTE
                        else:
                            id_type = IdentifierType.VARIABLE
                        
                        self.collector.append(IdentifierInfo(
                            name=name,
                            type=id_type,
                            line=node.target.lineno,
                            col=node.target.col_offset
                        ))
                    
                    self.generic_visit(node)
            
            visitor = IdentifierVisitor(identifiers)
            visitor.visit(tree)
            
        except SyntaxError:
            pass
        except Exception:
            pass
        
        return identifiers

    # ============== FILE CONVERSION ==============

    def convert_file(self, filepath: Path) -> Tuple[int, Dict[str, str]]:
        """
        Convert naming conventions in a file based on preferences.
        Returns: (number of conversions, dict of old->new names)
        """
        conversions = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Extract identifiers with their types
            identifiers = self.extract_identifiers(filepath)
            
            # Build conversion map
            for info in identifiers:
                if self.should_skip(info.name):
                    continue
                
                if self.needs_conversion(info.name, info.type):
                    target_style = self.get_target_style(info.type)
                    new_name = self.convert_to_style(info.name, target_style)
                    
                    if new_name and new_name != info.name:
                        # Avoid conflicts
                        if info.name not in conversions:
                            conversions[info.name] = new_name
            
            # Sort by length (longest first) to avoid partial replacements
            sorted_conversions = sorted(
                conversions.items(), 
                key=lambda x: len(x[0]), 
                reverse=True
            )
            
            # Apply conversions using word boundary regex
            for old_name, new_name in sorted_conversions:
                # Use word boundaries, avoid strings and comments
                pattern = r'(?<!["\'])\b' + re.escape(old_name) + r'\b(?!["\'])'
                content = re.sub(pattern, new_name, content)
            
            # SAFETY: Verify the file is still valid Python
            try:
                ast.parse(content)
            except SyntaxError:
                print(f"    {Fore.RED}⚠️  Skipping {filepath.name} - conversion would break syntax{Style.RESET_ALL}")
                return 0, {}
            
            # Write if changed
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
        
        python_files = list(directory.rglob("*.py"))
        
        for filepath in python_files:
            # Skip __pycache__ and hidden directories
            if '__pycache__' in str(filepath) or '/.git/' in str(filepath) or '\\.git\\' in str(filepath):
                continue
            
            count, conversions = self.convert_file(filepath)
            if count > 0:
                files_processed += 1
                total_conversions += count
                all_conversions.update(conversions)
        
        return files_processed, total_conversions, all_conversions


def fix_naming_dynamic(codebase_path: Path, preferences: NamingPreferences) -> Tuple[int, int]:
    """
    Fix naming conventions using dynamic preferences.
    Returns: (files_fixed, total_conversions)
    """
    print(f"  {Fore.YELLOW}→ Applying dynamic naming conventions...{Style.RESET_ALL}")
    print(f"    Variables: {Fore.CYAN}{preferences.variables}{Style.RESET_ALL}")
    print(f"    Functions: {Fore.CYAN}{preferences.functions}{Style.RESET_ALL}")
    print(f"    Classes:   {Fore.CYAN}{preferences.classes}{Style.RESET_ALL}")
    print(f"    Methods:   {Fore.CYAN}{preferences.methods}{Style.RESET_ALL}")
    print()
    
    converter = DynamicNamingConverter(preferences)
    files_fixed, total_conversions, conversions = converter.convert_directory(codebase_path)
    
    if total_conversions > 0:
        print(f"    {Fore.GREEN}✅ Converted {total_conversions} names in {files_fixed} files{Style.RESET_ALL}")
        
        # Group by type for better display
        examples = list(conversions.items())[:8]
        for old, new in examples:
            print(f"       {Fore.YELLOW}{old}{Style.RESET_ALL} → {Fore.GREEN}{new}{Style.RESET_ALL}")
        if len(conversions) > 8:
            print(f"       ... and {len(conversions) - 8} more")
    else:
        print(f"    {Fore.GREEN}✅ No naming conversions needed{Style.RESET_ALL}")
    
    return files_fixed, total_conversions
