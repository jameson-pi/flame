"""Flame - AI-powered CLI coding assistant with Hack Club AI."""

import os
import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from flame.api.client import HackClubAIClient
from flame.cli.repl import REPL


def main():
    """Main entry point for Flame CLI."""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Flame - AI Coding Assistant powered by Hack Club AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start interactive REPL
  python main.py --check           # Check API connection
  python main.py --version         # Show version
        """,
    )
    parser.add_argument("--version", action="version", version="Flame 0.1.0")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Test connection to Hack Club AI API",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Working directory (defaults to current directory)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="AI model to use (overrides HACK_CLUB_MODEL env var)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    console = Console()

    # Initialize API client
    try:
        client = HackClubAIClient(
            model=args.model,
            console=console,
        )
    except ValueError as e:
        console.print(f"[red]❌ Configuration Error: {e}[/red]")
        console.print("\n[yellow]Setup Instructions:[/yellow]")
        console.print("1. Copy .env.example to .env")
        console.print("2. Add your Hack Club AI API key to .env")
        sys.exit(1)

    # Check connection if requested
    if args.check:
        console.print("[cyan]🔍 Testing connection to Hack Club AI...[/cyan]")
        if client.validate_connection():
            console.print("[green]✅ Connection successful![/green]")
            sys.exit(0)
        else:
            console.print("[red]❌ Connection failed. Check your API key and network.[/red]")
            sys.exit(1)

    # Determine working directory
    working_dir = args.dir or os.getcwd()
    if not Path(working_dir).exists():
        console.print(f"[red]❌ Directory not found: {working_dir}[/red]")
        sys.exit(1)

    # Start REPL
    try:
        repl = REPL(
            api_client=client,
            working_dir=working_dir,
        )
        repl.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if args.debug:
            raise
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
