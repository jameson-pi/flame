"""Handle file creation/editing and command execution with user approval."""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from difflib import unified_diff
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax


class FileExecutor:
    """Safely create and edit files with user approval."""

    def __init__(self, base_dir: Optional[str] = None, console: Optional[Console] = None):
        """Initialize file executor.
        
        Args:
            base_dir: Base directory to restrict operations (defaults to current)
            console: Rich console for output
        """
        self.base_dir = Path(base_dir or os.getcwd()).resolve()
        self.console = console or Console()

    def _is_path_safe(self, path: Path) -> bool:
        """Check if path is within allowed base directory.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            path.resolve().relative_to(self.base_dir)
            return True
        except ValueError:
            return False

    def suggest_file_creation(
        self,
        filepath: str,
        content: str,
        description: str = "",
    ) -> bool:
        """Suggest creating a new file with user approval.
        
        Args:
            filepath: Relative path to file
            content: File content
            description: Description of why file is needed
            
        Returns:
            True if file was created, False if rejected
        """
        target_path = (self.base_dir / filepath).resolve()
        
        # Safety check
        if not self._is_path_safe(target_path):
            self.console.print(
                f"[red]❌ Security Error: Cannot create file outside base directory[/red]\n"
                f"   Attempted: {target_path}\n"
                f"   Allowed: {self.base_dir}"
            )
            return False

        # Check if file exists
        if target_path.exists():
            self.console.print(
                f"[yellow]⚠️  File already exists: {filepath}[/yellow]"
            )
            if not Confirm.ask("Overwrite?"):
                return False

        # Show preview
        self.console.print(f"\n[cyan]📝 Create File: {filepath}[/cyan]")
        if description:
            self.console.print(f"   {description}")
        
        # Show content preview (first 30 lines)
        lines = content.split("\n")[:30]
        preview = "\n".join(lines)
        if len(content.split("\n")) > 30:
            preview += "\n   ... (truncated)"
        
        self.console.print("\n[blue]Preview:[/blue]")
        self.console.print(preview)
        
        # Request approval
        if not Confirm.ask("\n✅ Create this file?", default=False):
            return False

        # Create parent directories
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        target_path.write_text(content, encoding="utf-8")
        self.console.print(f"[green]✅ File created: {filepath}[/green]")
        return True

    def suggest_file_edit(
        self,
        filepath: str,
        old_content: str,
        new_content: str,
        description: str = "",
    ) -> bool:
        """Suggest editing an existing file with diff preview.
        
        Args:
            filepath: Relative path to file
            old_content: Original content
            new_content: New content
            description: Description of changes
            
        Returns:
            True if file was edited, False if rejected
        """
        target_path = (self.base_dir / filepath).resolve()
        
        # Safety check
        if not self._is_path_safe(target_path):
            self.console.print(
                f"[red]❌ Security Error: Cannot edit file outside base directory[/red]"
            )
            return False

        # Generate and show diff
        diff_lines = unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=filepath,
            tofile=filepath,
            lineterm="",
        )
        diff_text = "".join(diff_lines)

        self.console.print(f"\n[cyan]✏️  Edit File: {filepath}[/cyan]")
        if description:
            self.console.print(f"   {description}")
        
        # Show diff with syntax highlighting
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
        self.console.print(syntax)
        
        # Request approval
        if not Confirm.ask("\n✅ Apply these changes?", default=False):
            return False

        # Write file
        target_path.write_text(new_content, encoding="utf-8")
        self.console.print(f"[green]✅ File updated: {filepath}[/green]")
        return True

    def read_file(self, filepath: str) -> str:
        """Read a file's content automatically (auto-approved).

        Args:
            filepath: Relative path to file

        Returns:
            Content of the file or an error message
        """
        target_path = (self.base_dir / filepath).resolve()

        # Safety check
        if not self._is_path_safe(target_path):
            return f"Error: Security restriction - Cannot read file outside base directory."

        if not target_path.exists():
            return f"Error: File '{filepath}' does not exist."

        if not target_path.is_file():
            return f"Error: '{filepath}' is not a file."

        try:
            content = target_path.read_text(encoding="utf-8")
            self.console.print(f"[blue]📖 Auto-read file: {filepath}[/blue]")
            return content
        except Exception as e:
            return f"Error reading file '{filepath}': {str(e)}"

    def list_dir(self, directory: str = ".") -> str:
        """List contents of a directory (auto-approved).

        Args:
            directory: Directory to list

        Returns:
            Directory listing or error
        """
        target_path = (self.base_dir / directory).resolve()

        if not self._is_path_safe(target_path):
            return "Error: Security restriction - Cannot list directory outside base directory."

        if not target_path.exists():
            return f"Error: Directory '{directory}' does not exist."

        if not target_path.is_dir():
            return f"Error: '{directory}' is not a directory."

        try:
            items = os.listdir(target_path)
            self.console.print(f"[blue]📂 Auto-list directory: {directory}[/blue]")
            return "\n".join(items)
        except Exception as e:
            return f"Error listing directory '{directory}': {str(e)}"

    def find_files(self, pattern: str) -> str:
        """Find files matching a pattern (auto-approved).

        Args:
            pattern: Glob pattern to search for

        Returns:
            List of matching files or error
        """
        try:
            self.console.print(f"[blue]🔍 Auto-find files: {pattern}[/blue]")
            matches = list(self.base_dir.rglob(pattern))
            if not matches:
                return "No matches found."
            
            relative_matches = []
            for m in matches:
                try:
                    relative_matches.append(str(m.relative_to(self.base_dir)))
                except ValueError:
                    continue
                    
            return "\n".join(relative_matches)
        except Exception as e:
            return f"Error finding files with pattern '{pattern}': {str(e)}"

    def grep_search(self, query: str, pattern: str = "*") -> str:
        """Search for text within files (auto-approved).

        Args:
            query: Text to search for
            pattern: File pattern to include

        Returns:
            Search results or error
        """
        try:
            self.console.print(f"[blue]🔎 Auto-grep search: '{query}' in {pattern}[/blue]")
            results = []
            for path in self.base_dir.rglob(pattern):
                if path.is_file() and self._is_path_safe(path):
                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        for i, line in enumerate(content.splitlines(), 1):
                            if query in line:
                                rel_path = path.relative_to(self.base_dir)
                                results.append(f"{rel_path}:{i}: {line.strip()}")
                    except Exception:
                        continue
            
            if not results:
                return "No matches found."
            return "\n".join(results[:100]) # Limit output
        except Exception as e:
            return f"Error during grep search: {str(e)}"

    def get_errors(self, filepath: str) -> str:
        """Check for syntax errors in a Python file (auto-approved).

        Args:
            filepath: Relative path to file

        Returns:
            Errors or 'No syntax errors found.'
        """
        target_path = (self.base_dir / filepath).resolve()
        if not self._is_path_safe(target_path):
            return "Error: Security restriction."

        if not target_path.exists() or not target_path.suffix == ".py":
            return f"Error: File '{filepath}' not found or not a Python file."

        try:
            self.console.print(f"[blue]🛡️  Auto-check errors: {filepath}[/blue]")
            import ast
            with open(target_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            return "No syntax errors found."
        except SyntaxError as e:
            return f"Syntax Error in {filepath}:{e.lineno}:{e.offset}: {e.msg}\n{e.text}"
        except Exception as e:
            return f"Error checking syntax in {filepath}: {str(e)}"


class CommandExecutor:
    """Safely execute terminal commands with user approval and safety checks."""

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"sudo\s+",
        r"dd\s+",
        r"mkfs\s+",
        r":\s*\(\s*:\s*\)\s*;\s*:",  # Fork bomb
    ]

    def __init__(self, console: Optional[Console] = None):
        """Initialize command executor.
        
        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.command_history = []

    def is_dangerous(self, command: str) -> bool:
        """Check if command matches dangerous patterns.
        
        Args:
            command: Command to check
            
        Returns:
            True if command is dangerous
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def suggest_command(
        self,
        command: str,
        description: str = "",
        dry_run: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Suggest executing a command with user approval.
        
        Args:
            command: Command to execute
            description: Description of what command does
            dry_run: If True, show command but don't execute
            
        Returns:
            Tuple of (success, output)
        """
        # Check for dangerous patterns
        if self.is_dangerous(command):
            self.console.print(
                f"[red]🚨 Dangerous Command Detected:[/red]\n"
                f"   {command}\n\n"
                f"This command matches safety patterns and is blocked."
            )
            return False, None

        # Show command details
        self.console.print(f"\n[cyan]🔧 Run Command:[/cyan]")
        if description:
            self.console.print(f"   {description}")
        self.console.print(f"\n[blue]Command:[/blue]\n   {command}")

        if dry_run:
            self.console.print("\n[yellow]🔄 Dry-run mode (not executing)[/yellow]")
            return True, None

        # Request approval
        if not Confirm.ask("\n✅ Execute this command?", default=False):
            return False, None

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.command_history.append(command)
            output = result.stdout + (result.stderr if result.returncode != 0 else "")

            if result.returncode == 0:
                self.console.print(f"[green]✅ Command executed successfully[/green]")
            else:
                self.console.print(
                    f"[yellow]⚠️  Command exited with code {result.returncode}[/yellow]"
                )

            if output:
                self.console.print(f"\n[blue]Output:[/blue]\n{output}")

            return True, output

        except subprocess.TimeoutExpired:
            self.console.print("[red]❌ Command timed out after 30 seconds[/red]")
            return False, None
        except Exception as e:
            self.console.print(f"[red]❌ Error executing command: {e}[/red]")
            return False, None

