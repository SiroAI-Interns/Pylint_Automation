"""
Autoencoder - Automated Pylint Error Fixer

Main entry point for the automation tool.
Supports dynamic naming conventions per identifier type.
"""
import argparse
import sys
from pathlib import Path

from colorama import init, Fore, Style

from src.config import Config
from src.pylintrc_generator import PylintrcGenerator
from src.fixer import CodeFixer
from src.runner import PylintRunner
from src.dynamic_config import NamingPreferences, PRESETS


def print_banner():
    """Print the Autoencoder banner."""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║                                                               ║
║     {Fore.YELLOW}█████╗ ██╗   ██╗████████╗ ██████╗ ███████╗███╗   ██╗{Fore.CYAN}     ║
║    {Fore.YELLOW}██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝████╗  ██║{Fore.CYAN}    ║
║    {Fore.YELLOW}███████║██║   ██║   ██║   ██║   ██║█████╗  ██╔██╗ ██║{Fore.CYAN}    ║
║    {Fore.YELLOW}██╔══██║██║   ██║   ██║   ██║   ██║██╔══╝  ██║╚██╗██║{Fore.CYAN}    ║
║    {Fore.YELLOW}██║  ██║╚██████╔╝   ██║   ╚██████╔╝███████╗██║ ╚████║{Fore.CYAN}    ║
║    {Fore.YELLOW}╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝{Fore.CYAN}    ║
║                                                               ║
║          {Fore.WHITE}Automated Pylint Error Fixer{Fore.CYAN}                        ║
║       {Fore.GREEN}Now with Dynamic Naming Conventions!{Fore.CYAN}                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


VALID_STYLES = ["snake_case", "camelCase", "PascalCase", "SCREAMING_SNAKE_CASE"]


def main():
    """Main entry point."""
    init()  # Initialize colorama
    print_banner()

    parser = argparse.ArgumentParser(
        description="Autoencoder - Automated Pylint Error Fixer with Dynamic Naming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Fore.CYAN}═══ DYNAMIC NAMING EXAMPLES ═══{Style.RESET_ALL}

  {Fore.GREEN}# Use preset configuration:{Style.RESET_ALL}
  python main.py --path ./myproject --preset mixed_style

  {Fore.GREEN}# Custom per-type naming conventions:{Style.RESET_ALL}
  python main.py --path ./myproject --var-naming snake_case --func-naming camelCase --class-naming PascalCase

  {Fore.GREEN}# Use a config file:{Style.RESET_ALL}
  python main.py --path ./myproject --config naming_config.json

{Fore.CYAN}═══ AVAILABLE NAMING STYLES ═══{Style.RESET_ALL}

  • snake_case          → my_variable_name
  • camelCase           → myVariableName  
  • PascalCase          → MyClassName
  • SCREAMING_SNAKE_CASE → MY_CONSTANT

{Fore.CYAN}═══ AVAILABLE PRESETS ═══{Style.RESET_ALL}

  • python_standard  → PEP8 style (snake_case for most, PascalCase for classes)
  • java_style       → Java style (camelCase for most, PascalCase for classes)
  • mixed_style      → Mixed (snake_case vars, camelCase funcs, PascalCase classes)
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the codebase to fix"
    )
    
    # Dynamic naming options
    naming_group = parser.add_argument_group('Dynamic Naming Options')
    
    naming_group.add_argument(
        "--config",
        type=str,
        help="Path to JSON config file with naming preferences"
    )
    
    naming_group.add_argument(
        "--preset",
        type=str,
        choices=["python_standard", "java_style", "mixed_style"],
        help="Use a preset naming configuration"
    )
    
    naming_group.add_argument(
        "--var-naming",
        type=str,
        choices=VALID_STYLES,
        default="snake_case",
        help="Naming convention for variables (default: snake_case)"
    )
    
    naming_group.add_argument(
        "--func-naming",
        type=str,
        choices=VALID_STYLES,
        default="camelCase",
        help="Naming convention for functions (default: camelCase)"
    )
    
    naming_group.add_argument(
        "--class-naming",
        type=str,
        choices=VALID_STYLES,
        default="PascalCase",
        help="Naming convention for classes (default: PascalCase)"
    )
    
    naming_group.add_argument(
        "--method-naming",
        type=str,
        choices=VALID_STYLES,
        default="camelCase",
        help="Naming convention for methods (default: camelCase)"
    )
    
    naming_group.add_argument(
        "--arg-naming",
        type=str,
        choices=VALID_STYLES,
        default="snake_case",
        help="Naming convention for function arguments (default: snake_case)"
    )
    
    # Legacy single-convention option (for backwards compatibility)
    parser.add_argument(
        "--naming",
        type=str,
        choices=["camelCase", "snake_case"],
        help="[LEGACY] Single naming convention for all (use --var-naming etc. instead)"
    )
    
    # Fix options
    fix_group = parser.add_argument_group('Fix Options')
    
    fix_group.add_argument(
        "--fix-imports",
        type=bool,
        default=True,
        help="Fix import order issues (default: True)"
    )
    fix_group.add_argument(
        "--fix-whitespace",
        type=bool,
        default=True,
        help="Fix whitespace issues (default: True)"
    )
    fix_group.add_argument(
        "--fix-unused",
        type=bool,
        default=True,
        help="Remove unused imports/variables (default: True)"
    )
    fix_group.add_argument(
        "--fix-naming",
        action="store_true",
        default=True,
        help="Apply naming convention fixes (default: True)"
    )
    fix_group.add_argument(
        "--generate-pylintrc",
        type=bool,
        default=True,
        help="Generate a .pylintrc file (default: True)"
    )
    fix_group.add_argument(
        "--max-line-length",
        type=int,
        default=100,
        help="Maximum line length (default: 100)"
    )

    args = parser.parse_args()

    # Validate path
    codebase_path = Path(args.path)
    if not codebase_path.exists():
        print(f"{Fore.RED}Error: Path '{args.path}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)

    # Determine naming preferences
    naming_preferences = None
    use_dynamic = False
    
    if args.config:
        # Load from config file
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"{Fore.RED}Error: Config file '{args.config}' does not exist.{Style.RESET_ALL}")
            sys.exit(1)
        naming_preferences = NamingPreferences.from_json_file(config_path)
        use_dynamic = True
        print(f"{Fore.GREEN}📄 Loaded naming config from: {args.config}{Style.RESET_ALL}")
        
    elif args.preset:
        # Use preset
        naming_preferences = PRESETS[args.preset]
        use_dynamic = True
        print(f"{Fore.GREEN}📋 Using preset: {args.preset}{Style.RESET_ALL}")
        
    elif not args.naming:
        # Use custom per-type naming (dynamic mode)
        naming_preferences = NamingPreferences(
            variables=args.var_naming,
            functions=args.func_naming,
            classes=args.class_naming,
            methods=args.method_naming,
            arguments=args.arg_naming,
            constants="SCREAMING_SNAKE_CASE",
            attributes=args.var_naming,  # Same as variables by default
        )
        use_dynamic = True

    # Create configuration (legacy mode for compatibility)
    config = Config(
        codebase_path=codebase_path,
        naming_convention=args.naming if args.naming else "camelCase",
        fix_imports=args.fix_imports,
        fix_whitespace=args.fix_whitespace,
        fix_unused=args.fix_unused,
        fix_naming=args.fix_naming,
        generate_pylintrc=args.generate_pylintrc,
        max_line_length=args.max_line_length
    )

    # Print configuration
    print(f"\n{Fore.GREEN}Configuration:{Style.RESET_ALL}")
    print(f"  📁 Codebase Path: {config.codebase_path}")
    print(f"  📏 Max Line Length: {config.max_line_length}")
    
    if use_dynamic and naming_preferences:
        print(f"\n{Fore.CYAN}  🎯 Dynamic Naming Conventions:{Style.RESET_ALL}")
        print(f"     Variables:  {Fore.YELLOW}{naming_preferences.variables}{Style.RESET_ALL}")
        print(f"     Functions:  {Fore.YELLOW}{naming_preferences.functions}{Style.RESET_ALL}")
        print(f"     Classes:    {Fore.YELLOW}{naming_preferences.classes}{Style.RESET_ALL}")
        print(f"     Methods:    {Fore.YELLOW}{naming_preferences.methods}{Style.RESET_ALL}")
        print(f"     Arguments:  {Fore.YELLOW}{naming_preferences.arguments}{Style.RESET_ALL}")
        print(f"     Constants:  {Fore.YELLOW}{naming_preferences.constants}{Style.RESET_ALL}")
    else:
        print(f"  🐫 Naming Convention: {config.naming_convention} (legacy mode)")
    print()

    # Step 1: Generate .pylintrc if requested
    if config.generate_pylintrc:
        print(f"{Fore.CYAN}[Step 1/4] Generating .pylintrc...{Style.RESET_ALL}")
        generator = PylintrcGenerator(config)
        pylintrc_path = generator.generate()
        print(f"  ✅ Generated: {pylintrc_path}\n")
    else:
        print(f"{Fore.YELLOW}[Step 1/4] Skipping .pylintrc generation{Style.RESET_ALL}\n")

    # Step 2: Run initial pylint to get baseline
    print(f"{Fore.CYAN}[Step 2/4] Running initial pylint scan...{Style.RESET_ALL}")
    runner = PylintRunner(config)
    initial_count = runner.run_and_count()
    print(f"  📊 Initial errors: {initial_count}\n")

    # Step 3: Apply fixes (with dynamic naming if configured)
    print(f"{Fore.CYAN}[Step 3/4] Applying automated fixes...{Style.RESET_ALL}")
    fixer = CodeFixer(config, naming_preferences if use_dynamic else None)
    fixer.fix_all()
    print()

    # Step 4: Run final pylint
    print(f"{Fore.CYAN}[Step 4/4] Running final pylint scan...{Style.RESET_ALL}")
    final_count = runner.run_and_count()
    print(f"  📊 Final errors: {final_count}\n")

    # Summary
    reduction = initial_count - final_count
    percentage = (reduction / initial_count * 100) if initial_count > 0 else 100

    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"  Initial Errors: {initial_count}")
    print(f"  Final Errors:   {final_count}")
    print(f"  Reduction:      {reduction} ({percentage:.1f}%)")
    print()

    if final_count == 0:
        print(f"{Fore.GREEN}🎉 All errors fixed! Your code is now pylint-clean!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  {final_count} errors remaining. Check pylint output for details.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
