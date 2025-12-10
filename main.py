"""
Autoencoder - Automated Pylint Error Fixer

Main entry point for the automation tool.
"""
import argparse
import sys
from pathlib import Path

from colorama import init, Fore, Style

from src.config import Config
from src.pylintrc_generator import PylintrcGenerator
from src.fixer import CodeFixer
from src.runner import PylintRunner


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
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


def main():
    """Main entry point."""
    init()  # Initialize colorama
    print_banner()

    parser = argparse.ArgumentParser(
        description="Autoencoder - Automated Pylint Error Fixer"
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the codebase to fix"
    )
    parser.add_argument(
        "--naming",
        type=str,
        choices=["camelCase", "snake_case"],
        default="camelCase",
        help="Naming convention to enforce (default: camelCase)"
    )
    parser.add_argument(
        "--fix-imports",
        type=bool,
        default=True,
        help="Fix import order issues (default: True)"
    )
    parser.add_argument(
        "--fix-whitespace",
        type=bool,
        default=True,
        help="Fix whitespace issues (default: True)"
    )
    parser.add_argument(
        "--fix-unused",
        type=bool,
        default=True,
        help="Remove unused imports/variables (default: True)"
    )
    parser.add_argument(
        "--fix-naming",
        action="store_true",
        default=True,
        help="Convert snake_case to camelCase (with syntax validation)"
    )
    parser.add_argument(
        "--generate-pylintrc",
        type=bool,
        default=True,
        help="Generate a .pylintrc file (default: True)"
    )
    parser.add_argument(
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

    # Create configuration
    config = Config(
        codebase_path=codebase_path,
        naming_convention=args.naming,
        fix_imports=args.fix_imports,
        fix_whitespace=args.fix_whitespace,
        fix_unused=args.fix_unused,
        fix_naming=args.fix_naming,
        generate_pylintrc=args.generate_pylintrc,
        max_line_length=args.max_line_length
    )

    print(f"\n{Fore.GREEN}Configuration:{Style.RESET_ALL}")
    print(f"  📁 Codebase Path: {config.codebase_path}")
    print(f"  🐫 Naming Convention: {config.naming_convention}")
    print(f"  📏 Max Line Length: {config.max_line_length}")
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

    # Step 3: Apply fixes
    print(f"{Fore.CYAN}[Step 3/4] Applying automated fixes...{Style.RESET_ALL}")
    fixer = CodeFixer(config)
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

