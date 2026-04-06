"""Flame - AI-powered CLI coding assistant with API."""

import os
import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from flame.api.client import APIClient
from flame.cli.repl import REPL


def main():
    """Main entry point for Flame CLI."""
    # Define home directory config path
    home_config_dir = Path.home() / ".flame"
    home_env_path = home_config_dir / ".env"

    # Create directory if it doesn't exist
    if not home_config_dir.exists():
        try:
            home_config_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    # Load environment variables (prefer current dir .env, then home dir)
    load_dotenv()  # Local directory
    if home_env_path.exists():
        load_dotenv(dotenv_path=home_env_path)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Flame - AI Coding Assistant powered by API",
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
        help="Test connection to API",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Interactive setup to configure your API key and settings",
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
        help="AI model to use (overrides FLAME_MODEL env var)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    console = Console()

    if args.setup:
        console.print("[bold cyan]🔥 Flame Interactive Setup[/bold cyan]")
        console.print("This will create a .env file in your ~/.flame/ directory with your settings.\n")
        api_key = input("Enter your API Key: ").strip()
        
        if not api_key:
            console.print("[red]❌ Setup cancelled: API key cannot be empty.[/red]")
            sys.exit(1)
            
        model = input("Enter preferred model (press Enter for default 'google/gemini-3-flash-preview'): ").strip()
        
        # Determine setup location (home dir)
        setup_env_path = Path.home() / ".flame" / ".env"
        setup_env_path.parent.mkdir(parents=True, exist_ok=True)
        
        env_content = []
        if setup_env_path.exists():
            env_content = setup_env_path.read_text(encoding="utf-8").splitlines()
            
        # Basic replacement or append
        new_env = []
        key_found = False
        model_found = False
        for line in env_content:
            if line.startswith("FLAME_API_KEY="):
                new_env.append(f"FLAME_API_KEY={api_key}")
                key_found = True
            elif line.startswith("FLAME_MODEL=") and model:
                new_env.append(f"FLAME_MODEL={model}")
                model_found = True
            else:
                new_env.append(line)
                
        if not key_found:
            new_env.append(f"FLAME_API_KEY={api_key}")
        if model and not model_found:
            new_env.append(f"FLAME_MODEL={model}")
            
        setup_env_path.write_text("\n".join(new_env) + "\n", encoding="utf-8")
        console.print(f"\n[green]✅ Setup complete! Settings saved to {setup_env_path}[/green]")
        console.print("Run [bold cyan]flame[/bold cyan] to start chatting!")
        sys.exit(0)

    # Initialize API client
    try:
        client = APIClient(
            model=args.model,
            console=console,
        )
    except ValueError as e:
        console.print(f"[red]❌ Configuration Error: {e}[/red]")
        console.print("\n[yellow]Setup Instructions:[/yellow]")
        console.print("Run [bold cyan]flame --setup[/bold cyan] to configure your API key interactively.")
        sys.exit(1)

    # Check connection if requested
    if args.check:
        console.print("[cyan]🔍 Testing connection to API...[/cyan]")
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
