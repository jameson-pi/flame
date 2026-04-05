"""Interactive REPL for chat loop with streaming responses."""

import json
import signal
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML

from api.client import APIClient
from utils.context import SystemContext
from cli.executor import FileExecutor, CommandExecutor


class REPL:
    """Interactive read-eval-print loop for AI coding assistant."""

    def __init__(
        self,
        api_client: APIClient,
        working_dir: Optional[str] = None,
        history_file: Optional[str] = None,
    ):
        """Initialize REPL.
        
        Args:
            api_client: APIClient instance
            working_dir: Working directory for file operations
            history_file: Path to save command history
        """
        self.client = api_client
        self.console = Console()
        self.working_dir = Path(working_dir or os.getcwd())
        self.system_context = SystemContext(working_dir=str(self.working_dir))
        self.file_executor = FileExecutor(base_dir=str(self.working_dir), console=self.console)
        self.command_executor = CommandExecutor(console=self.console)

        # Message history for multi-turn conversation
        self.messages = []
        self.add_system_message()

        # Setup command history
        history_file = history_file or Path.home() / ".flame_history"
        self.prompt_session = PromptSession(history=FileHistory(str(history_file)))

    def add_system_message(self):
        """Add system context as initial message."""
        context_prompt = self.system_context.get_context_prompt()
        self.messages.append({
            "role": "system",
            "content": (
                f"{context_prompt}\n\n"
                "CRITICAL: You are an agent that can directly interact with the user's terminal and filesystem.\n"
                "To perform actions, you MUST use the following commands in your output:\n\n"
                "1. `/create <filepath>` - Use this to create a NEW file.\n"
                "   Followed by a markdown code block containing the content. Example:\n"
                "   /create hello.py\n"
                "   ```python\n"
                "   print('hello')\n"
                "   ```\n\n"
                "2. `/edit <filepath>` - Use this to EDIT an existing file.\n"
                "   Followed by a markdown code block containing the FULL new content. Example:\n"
                "   /edit existing.txt\n"
                "   ```\n"
                "   This is the new content.\n"
                "   ```\n\n"
                "3. `/read <filepath>` - Use this to READ a file's content automatically (No user approval needed for reading). Example:\n"
                "   /read src/main.py\n\n"
                "4. `/run <command>` - Use this to run a shell command. Example:\n"
                "   /run pip install requests\n\n"
                "Do NOT just explain how to do it. ACT by emitting these commands.\n"
                "IMPORTANT: After you emit a command, the system will provide the output in the NEXT turn as 'Action results:'. Use this feedback to continue your task.\n"
                "CRITICAL: Always wrap file content in triple backticks (```). "
                "Any text OUTSIDE of the /command line and the code block will be treated as conversational notes and NOT part of the file.\n"
                "File creation, editing, and command execution require user approval (y/n), but READING is automatic.\n"
                "If the user asks to 'test a shell command' or 'make a file', use the /run or /create commands respectively."
            ),
        })

    def print_welcome(self):
        """Print welcome message."""
        self.console.print("\n")
        self.console.print(
            Panel.fit(
                "[bold cyan]🔥 Flame - AI Coding Assistant[/bold cyan]\n"
                "Powered by API",
                border_style="cyan",
            )
        )
        self.console.print("[dim]Type 'help' for commands, 'exit' to quit\n[/dim]")

    def print_help(self):
        """Print help message."""
        help_text = """
[bold]Available Commands:[/bold]

  [cyan]help[/cyan]          - Show this help message
  [cyan]context[/cyan]       - Show current system context
  [cyan]clear[/cyan]         - Clear conversation history
  [cyan]exit[/cyan]          - Exit the program
  [cyan]/read <file>[/cyan]   - Read a file's content (auto-approved)
  [cyan]/run <cmd>[/cyan]     - Suggest running a command (AI-aware)
  [cyan]/edit <file>[/cyan]   - Suggest editing a file
  [cyan]/create <file>[/cyan] - Suggest creating a file

[bold]Tips:[/bold]
  • Type normally to chat with the AI
  • The AI has context about your project
  • All file/command operations require your approval
  • Multi-line input: Ctrl+Enter (or continue on new line)
        """
        self.console.print(Markdown(help_text))

    def print_context(self):
        """Print current system context."""
        self.console.print("\n[cyan]📍 System Context:[/cyan]\n")
        self.console.print(self.system_context.get_full_context())

    def handle_command(self, user_input: str) -> Optional[str]:
        """Handle special commands before sending to AI.
        
        Args:
            user_input: User input text
            
        Returns:
            Modified input to send to AI, or None if command was handled
        """
        stripped = user_input.strip().lower()

        if stripped == "help":
            self.print_help()
            return None
        elif stripped == "context":
            self.print_context()
            return None
        elif stripped == "clear":
            self.messages = []
            self.add_system_message()
            self.console.print("[green]✅ Conversation history cleared[/green]")
            return None
        elif stripped == "exit":
            raise KeyboardInterrupt()
        elif stripped.startswith("/read "):
            filepath = user_input[6:].strip()
            if filepath:
                content = self.file_executor.read_file(filepath)
                self.console.print(Panel(content, title=f"Content of {filepath}"))
            return None
        elif stripped.startswith("/run "):
            command = user_input[5:].strip()
            if command:
                success, output = self.command_executor.suggest_command(
                    command,
                    description="Suggested by AI assistant",
                )
            return None
        elif stripped.startswith("/create "):
            filepath = user_input[8:].strip()
            if filepath:
                self.console.print(
                    "[yellow]Note: Use AI to help generate file content, "
                    "then approve creation[/yellow]"
                )
            return None
        elif stripped.startswith("/edit "):
            filepath = user_input[6:].strip()
            if filepath:
                self.console.print(
                    "[yellow]Note: Use AI to help generate edits, "
                    "then approve changes[/yellow]"
                )
            return None

        return user_input

    def _process_assistant_commands(self, response: str):
        """Parse and execute commands from AI response and return feedback."""
        feedback = []
        
        # Regex for block commands (/create, /edit)
        block_cmd_pattern = r"/(create|edit)\s+([^\n]+)\s*\n\s*```[^\n]*\n(.*?)\n\s*```"
        
        # First, find all block commands
        for match in re.finditer(block_cmd_pattern, response, re.DOTALL):
            cmd = match.group(1)
            filepath = match.group(2).strip()
            content = match.group(3)
            
            if cmd == "create":
                success = self.file_executor.suggest_file_creation(filepath, content, description="AI suggestion")
                if success:
                    feedback.append(f"File '{filepath}' created successfully.")
                else:
                    feedback.append(f"Creation of file '{filepath}' was rejected or failed.")
            elif cmd == "edit":
                target_path = self.working_dir / filepath
                old_content = ""
                if target_path.exists():
                    old_content = target_path.read_text(encoding="utf-8")
                
                if old_content:
                    success = self.file_executor.suggest_file_edit(filepath, old_content, content, description="AI suggestion")
                    if success:
                        feedback.append(f"File '{filepath}' updated successfully.")
                    else:
                        feedback.append(f"Edit of file '{filepath}' was rejected or failed.")
                else:
                    success = self.file_executor.suggest_file_creation(filepath, content, description="AI suggestion")
                    if success:
                        feedback.append(f"File '{filepath}' created (as it didn't exist).")
                    else:
                        feedback.append(f"Creation of file '{filepath}' was rejected.")

        # Pattern for simple commands (/read, /run)
        # Avoid matching /read or /run if they are inside a markdown block that was already processed
        remaining_response = response
        for match in re.finditer(block_cmd_pattern, response, re.DOTALL):
            remaining_response = remaining_response.replace(match.group(0), "")

        simple_cmd_pattern = r"/(read|run)\s+([^\n]+)"
        for match in re.finditer(simple_cmd_pattern, remaining_response):
            cmd = match.group(1)
            arg = match.group(2).strip()
            
            if cmd == "read":
                content = self.file_executor.read_file(arg)
                feedback.append(f"Content of '{arg}':\n{content}")
            elif cmd == "run":
                success, output = self.command_executor.suggest_command(arg, description="AI suggestion")
                if success:
                    feedback.append(f"Command '{arg}' executed.\nOutput:\n{output or '(No output)'}")
                else:
                    feedback.append(f"Command '{arg}' failed or was rejected.")

        return "\n".join(feedback)

    def run_conversation_step(self, user_message: str):
        """Run a interaction turn and process any commands."""
        
        # Add user response to history
        self.messages.append({
            "role": "user",
            "content": user_message,
        })

        # Get streaming response
        self.console.print("\n[cyan]🤖 Flame:[/cyan] ", end="", highlight=False)

        full_response = ""
        try:
            for chunk in self.client.chat_stream(self.messages):
                full_response += chunk
                self.console.print(chunk, end="", highlight=False)
                sys.stdout.flush()
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            return

        self.console.print("\n")

        # Process commands and get feedback
        feedback = self._process_assistant_commands(full_response)
        
        # Add assistant response to history
        self.messages.append({
            "role": "assistant",
            "content": full_response,
        })

        # If there's feedback, automatically start a new turn
        if feedback:
            self.console.print(f"\n[dim]🔄 Processing action results...[/dim]")
            self.run_conversation_step(f"Action results:\n{feedback}")

    def run(self):
        """Start the interactive REPL loop."""
        self.print_welcome()

        # Setup signal handlers for clean exit
        def signal_handler(sig, frame):
            self.console.print("\n[yellow]👋 Goodbye![/yellow]")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            while True:
                try:
                    # Get user input
                    user_input = self.prompt_session.prompt(
                        HTML("<cyan>You:</cyan> "),
                        multiline=False,
                    ).strip()

                    if not user_input:
                        continue

                    # Handle special commands
                    processed_input = self.handle_command(user_input)
                    if processed_input is None:
                        continue

                    # Run interaction loop
                    self.run_conversation_step(processed_input)

                except KeyboardInterrupt:
                    self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break
                except EOFError:
                    self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break

        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
            raise

