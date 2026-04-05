"""Interactive REPL for chat loop with streaming responses."""

import sys
import os
import signal
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import HTML
from pygments.lexers import PythonLexer
import re

from flame.api.client import HackClubAIClient
from flame.utils.context import SystemContext
from flame.cli.executor import FileExecutor, CommandExecutor
from flame.utils.prompts import SYSTEM_PROMPTS


class REPL:
    """Enhanced Interactive REPL for Flame AI."""

    def __init__(
        self,
        api_client: HackClubAIClient,
        working_dir: Optional[str] = None,
        history_file: Optional[str] = None,
    ):
        self.client = api_client
        self.console = Console()
        self.working_dir = Path(working_dir or os.getcwd())
        self.system_context = SystemContext(working_dir=self.working_dir)
        self.file_executor = FileExecutor(base_dir=self.working_dir, console=self.console)
        self.command_executor = CommandExecutor(console=self.console)

        self.messages = []
        self.add_system_message()

        # Setup persistent history in user home
        history_path = history_file or str(Path.home() / ".flame_history")
        self.prompt_session = PromptSession(
            history=FileHistory(history_path),
            lexer=PygmentsLexer(PythonLexer),
        )

    def add_system_message(self):
        """Add system context as initial message."""
        context_prompt = self.system_context.get_context_prompt()
        base_prompt = SYSTEM_PROMPTS.get("default")
        
        self.messages.append({
            "role": "system",
            "content": (
                f"{base_prompt}\n\n"
                f"{context_prompt}\n\n"
                "CRITICAL: You are an agent that can interact with the filesystem.\n"
                "COMMANDS AVAILABLE:\n"
                "1. /run command=\"...\" - Execute shell command (requires permission)\n"
                "2. /create path=\"...\" content=\"...\" - Create a new file (requires permission)\n"
                "3. /edit path=\"...\" old_content=\"...\" new_content=\"...\" - Edit a file (requires permission)\n"
                "4. /read path=\"...\" - Read file content (AUTO-APPROVED)\n"
                "5. /ls directory=\"...\" - List directory items (AUTO-APPROVED)\n"
                "6. /find pattern=\"...\" - Find files by glob pattern (AUTO-APPROVED)\n"
                "7. /grep query=\"...\" pattern=\"...\" - Search text in files (AUTO-APPROVED)\n"
                "8. /errors path=\"...\" - Check Python syntax errors (AUTO-APPROVED)\n"
            ),
        })

    def print_welcome(self):
        self.console.print(
            Panel.fit(
                "[bold cyan]🔥 Flame AI Refactored[/bold cyan]\n"
                "[dim]Syntax highlighting enabled (Python style). Press Alt+Enter for new line.[/dim]",
                border_style="cyan",
            )
        )

    def handle_command(self, user_input: str) -> Optional[str]:
        stripped = user_input.strip().lower()
        if stripped == "exit":
            raise KeyboardInterrupt()
        if stripped == "clear":
            self.messages = [self.messages[0]]
            self.console.print("[green]History cleared.[/green]")
            return None
        return user_input

    def run_conversation_step(self, user_message: str):
        self.messages.append({"role": "user", "content": user_message})
        
        while True:
            self.console.print("\n[cyan]🤖 Flame:[/cyan] ", end="")

            full_response = ""
            try:
                for chunk in self.client.chat_stream(self.messages):
                    full_response += chunk
                    self.console.print(chunk, end="", highlight=False)
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                return

            self.console.print("\n")
            self.messages.append({"role": "assistant", "content": full_response})

            # Look for commands in the response
            # Format: /run command="...", /create path="...", content="..." etc.
            # Simplified regex for demo purposes, can be improved
            command_found = False
            
            # Check for /run command="..."
            run_match = re.search(r'/run\s+(?:shell_command|command)=["\'](.*?)["\']', full_response)
            if not run_match:
                # Try simpler format if agent uses it
                run_match = re.search(r'/run\s+(.*)', full_response)

            if run_match:
                cmd = run_match.group(1).strip().strip('"').strip("'")
                success, output = self.command_executor.suggest_command(cmd)
                if success:
                    self.messages.append({
                        "role": "user",
                        "content": f"Command output:\n{output}" if output else "Command executed successfully (no output)."
                    })
                    command_found = True

            # Check for /read path="..."
            read_match = re.search(r'/read\s+(?:path|filepath|file)=["\'](.*?)["\']', full_response)
            if not read_match:
                read_match = re.search(r'/read\s+(.*)', full_response)
            
            if read_match:
                filepath = read_match.group(1).strip().strip('"').strip("'")
                content = self.file_executor.read_file(filepath)
                self.messages.append({
                    "role": "user",
                    "content": f"Content of {filepath}:\n\n{content}"
                })
                command_found = True

            # Check for /create path="..." content="..."
            create_match = re.search(r'/create\s+(?:path|filepath|file)=["\'](.*?)["\'](?:\s+content=["\'](.*?)["\'])?', full_response, re.DOTALL)
            if not create_match:
                create_match = re.search(r'/create\s+([^\s]+)\s+(.*)', full_response, re.DOTALL)

            if create_match:
                filepath = create_match.group(1).strip().strip('"').strip("'")
                content = create_match.group(2).strip().strip('"').strip("'") if create_match.lastindex >= 2 else ""
                success = self.file_executor.suggest_file_creation(filepath, content)
                if success:
                    self.messages.append({
                        "role": "user",
                        "content": f"File {filepath} created successfully."
                    })
                    command_found = True

            # Check for /edit path="..." old_content="..." new_content="..."
            edit_match = re.search(r'/edit\s+(?:path|filepath|file)=["\'](.*?)["\']\s+old_content=["\'](.*?)["\']\s+new_content=["\'](.*?)["\']', full_response, re.DOTALL)
            if edit_match:
                filepath = edit_match.group(1).strip().strip('"').strip("'")
                old_c = edit_match.group(2).strip().strip('"').strip("'")
                new_c = edit_match.group(3).strip().strip('"').strip("'")
                success = self.file_executor.suggest_file_edit(filepath, old_c, new_c)
                if success:
                    self.messages.append({
                        "role": "user",
                        "content": f"File {filepath} edited successfully."
                    })
                    command_found = True

            # Check for /ls directory="..."
            ls_match = re.search(r'/ls\s+(?:directory|dir)=["\'](.*?)["\']', full_response)
            if not ls_match:
                ls_match = re.search(r'/ls\s+(.*)', full_response)
            if ls_match:
                directory = ls_match.group(1).strip().strip('"').strip("'") or "."
                output = self.file_executor.list_dir(directory)
                self.messages.append({"role": "user", "content": f"Directory listing of {directory}:\n{output}"})
                command_found = True

            # Check for /find pattern="..."
            find_match = re.search(r'/find\s+pattern=["\'](.*?)["\']', full_response)
            if not find_match:
                find_match = re.search(r'/find\s+(.*)', full_response)
            if find_match:
                pattern = find_match.group(1).strip().strip('"').strip("'")
                output = self.file_executor.find_files(pattern)
                self.messages.append({"role": "user", "content": f"Find results for {pattern}:\n{output}"})
                command_found = True

            # Check for /grep query="..." pattern="..."
            grep_match = re.search(r'/grep\s+query=["\'](.*?)["\'](?:\s+pattern=["\'](.*?)["\'])?', full_response)
            if grep_match:
                query = grep_match.group(1).strip().strip('"').strip("'")
                pattern = grep_match.group(2).strip().strip('"').strip("'") if grep_match.lastindex >= 2 else "*"
                output = self.file_executor.grep_search(query, pattern)
                self.messages.append({"role": "user", "content": f"Grep results for '{query}' in {pattern}:\n{output}"})
                command_found = True

            # Check for /errors path="..."
            errors_match = re.search(r'/errors\s+(?:path|filepath|file)=["\'](.*?)["\']', full_response)
            if not errors_match:
                errors_match = re.search(r'/errors\s+(.*)', full_response)
            if errors_match:
                filepath = errors_match.group(1).strip().strip('"').strip("'")
                output = self.file_executor.get_errors(filepath)
                self.messages.append({"role": "user", "content": f"Error check for {filepath}:\n{output}"})
                command_found = True

            # If no command was executed, break the loop
            if not command_found:
                break

    def run(self):
        self.print_welcome()
        while True:
            try:
                user_input = self.prompt_session.prompt(
                    HTML("<cyan><b>>>></b></cyan> "),
                    multiline=False,
                ).strip()

                if not user_input: continue
                
                processed = self.handle_command(user_input)
                if processed:
                    self.run_conversation_step(processed)

            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
