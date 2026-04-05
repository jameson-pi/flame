"""Interactive REPL for chat loop with streaming responses."""

import os
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
from pygments.token import Token
import re

from flame.api.client import HackClubAIClient
from flame.utils.context import SystemContext
from flame.cli.executor import FileExecutor, CommandExecutor
from flame.utils.prompts import SYSTEM_PROMPTS
from flame.tools.registry import ToolRegistry
from flame.tools import fs, system


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
        self.system_context = SystemContext(working_dir=str(self.working_dir))
        self.file_executor = FileExecutor(base_dir=str(self.working_dir), console=self.console)
        self.command_executor = CommandExecutor(console=self.console)

        self.tool_registry = ToolRegistry(console=self.console)
        self._register_tools()

        self.messages = []
        self.add_system_message()

        # Custom Lexer for orange highlighting of tech words, filenames, etc.
        class TechLexer(PythonLexer):
            """Extends PythonLexer to highlight tech keywords, filenames, and proper nouns in orange."""
            
            TECH_WORDS = {
                'python', 'javascript', 'typescript', 'rust', 'go', 'html', 'css',
                'api', 'json', 'yaml', 'toml', 'git', 'docker', 'kubernetes',
                'flame', 'hackclub', 'ai', 'repl', 'cli', 'npm', 'pip', 'venv',
                'github', 'openrouter', 'gemini', 'deepseek', 'markdown',
                'function', 'variable', 'class', 'method', 'import', 'export',
                'server', 'client', 'database', 'rest', 'graphql', 'ssh'
            }

            def get_tokens_unprocessed(self, text):
                for index, token, value in super().get_tokens_unprocessed(text):
                    # Check for filenames (e.g., file.ext, /path/to/file)
                    is_filename = re.match(r'^[\w./-]+\.\w+$', value)
                    # Check for tech words or proper nouns
                    is_tech = value.lower() in self.TECH_WORDS
                    
                    if is_filename or is_tech:
                        yield index, Token.Name.Entity, value # Token.Name.Entity usually maps to orange/distinct color
                    else:
                        yield index, token, value

        # Setup persistent history in user home
        history_path = history_file or str(Path.home() / ".flame_history")
        self.prompt_session = PromptSession(
            history=FileHistory(history_path),
            lexer=PygmentsLexer(TechLexer),
        )

    def _register_tools(self):
        """Register all available tools."""
        self.tool_registry.register_tool(system.run_command_tool(self.command_executor))
        self.tool_registry.register_tool(fs.read_file_tool(self.file_executor))
        self.tool_registry.register_tool(fs.read_lines_tool(self.file_executor))
        self.tool_registry.register_tool(fs.create_file_tool(self.file_executor))
        self.tool_registry.register_tool(fs.edit_file_tool(self.file_executor))
        self.tool_registry.register_tool(fs.ls_tool(self.file_executor))
        self.tool_registry.register_tool(fs.find_tool(self.file_executor))
        self.tool_registry.register_tool(fs.grep_tool(self.file_executor))
        self.tool_registry.register_tool(fs.errors_tool(self.file_executor))

    def add_system_message(self):
        """Add system context as initial message."""
        # Remove any existing system messages to avoid duplicates
        self.messages = [m for m in self.messages if m.get("role") != "system"]
        
        context_prompt = self.system_context.get_context_prompt()
        base_prompt = SYSTEM_PROMPTS.get("base") or SYSTEM_PROMPTS.get("default")
        commands_help = self.tool_registry.get_system_prompt_fragment()
        
        self.messages.insert(0, {
            "role": "system",
            "content": (
                f"{base_prompt}\n\n"
                f"{context_prompt}\n\n"
                "CRITICAL: You are an agent that can interact with the filesystem.\n"
                f"{commands_help}"
            ),
        })

    def print_welcome(self):
        ascii_art = r"""
[bold orange1].------------------------------------------.
|                                          |
|   (      (                  *            |
|   )\ )   )\ )     (       (  `           |
|  (()/(  (()/(     )\      )\))(    (     |
|   /(_))  /(_)) ((((_)(   ((_)()\   )\    |
|  (_))_| (_))    )\ _ )\  (_()((_) ((_)   |
|  | |_   | |     (_)_\(_) |  \/  | | __|  |
|  | __|  | |__    / _ \   | |\/| | | _|   |
|  |_|    |____|  /_/ \_\  |_|  |_| |___|  |
|                                          |
'------------------------------------------'[/bold orange1]
"""
        self.console.print(ascii_art)
        self.console.print(
            Panel.fit(
                "[bold cyan]🔥 Flame AI Refactored\n[/bold cyan]"
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
        # Multi-model evaluation and planning
        # 1. Evaluation with google/gemini-3-flash-preview
        eval_messages = self.messages + [{"role": "user", "content": f"User request: {user_message}\nDoes this request require multiple steps or a plan? Respond with YES or NO only."}]
        needs_plan_raw = self.client.chat_complete(eval_messages, model="google/gemini-3-flash-preview")
        needs_plan = needs_plan_raw.strip().upper()

        if "YES" in needs_plan:
            self.console.print("[yellow]🧠 Complex request detected, generating plan...[/yellow]")
            plan_messages = self.messages + [
                {"role": "user", "content": (
                    f"User request: {user_message}\n"
                    "Generate a definitive technical plan for this task. Use a clear structure with numbered steps.\n"
                    "Available tools: read, ls, find, grep, errors, run, create, edit.\n"
                    "The plan will be shown to the user and then executed step-by-step."
                )}
            ]
            plan_content = self.client.chat_complete(plan_messages, model="google/gemini-3-flash-preview")
            
            # Save the plan in .flame directory with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_dir = self.working_dir / ".flame"
            plan_dir.mkdir(exist_ok=True)
            plan_filename = f"PLAN_{timestamp}.md"
            plan_path = plan_dir / plan_filename
            
            plan_path.write_text(plan_content, encoding="utf-8")
            self.console.print(f"[green]✅ Plan saved to {plan_path.relative_to(self.working_dir)}[/green]")
            
            # Show the plan in the console
            self.console.print("\n[bold cyan]📋 Generated Plan:[/bold cyan]")
            self.console.print(Panel(Markdown(plan_content), border_style="cyan"))
            self.console.print("\n")
            
            # Enter Plan Mode: Multi-turn loop to execute the plan
            self.console.print("[bold yellow]🚀 Entering Plan Execution Mode...[/bold yellow]")
            
            # Inject plan into initial context for the execution turn
            plan_context_name = f"Current Plan ({plan_filename})"
            self.system_context.inject_snippet(plan_context_name, plan_content)
            
            # Start a sub-conversation for plan execution
            # This allows the model to have multiple turns to read, check errors, and then create/edit
            plan_exec_messages = list(self.messages)
            plan_exec_messages.append({"role": "assistant", "content": f"I have generated a plan and saved it to {plan_filename}:\n\n{plan_content}"})
            plan_exec_messages.append({"role": "user", "content": f"Now, proceed with the plan step-by-step. Use /read and /errors to verify files before editing or after creating if needed. Current task: {user_message}"})

            # Run multi-turn execution
            self._execute_multi_turn(plan_exec_messages, model="google/gemini-3-flash-preview")
            
            # Cleanup
            self.system_context.remove_snippet(plan_context_name)
            
            # Sync the final state back to main history
            # We don't want to bloat the main history too much, but we should record that it happened
            self.messages.append({"role": "assistant", "content": f"Task completed according to the plan in {plan_filename}."})
        else:
            # Normal single-turn execution with gemini-3-flash-preview
            self._execute_with_model(user_message, model="google/gemini-3-flash-preview")

    def _execute_multi_turn(self, conversation_messages: list, model: str, max_turns: int = 10):
        """Execute a multi-turn conversation loop for complex plans."""
        turn_count = 0
        while turn_count < max_turns:
            turn_count += 1
            
            # Refresh system prompt with latest context (including snippets)
            self.add_system_message()
            # Find the index of the system message and update it in current conversation
            for i, msg in enumerate(conversation_messages):
                if msg["role"] == "system":
                    conversation_messages[i] = self.messages[0]
                    break
            else:
                conversation_messages.insert(0, self.messages[0])

            self.console.print(f"\n[cyan]🤖 Flame [Turn {turn_count}] ({model}):[/cyan] ")
            
            full_response = ""
            try:
                from rich.live import Live
                with Live(Markdown(""), console=self.console, refresh_per_second=4, transient=False) as live:
                    for chunk in self.client.chat_stream(conversation_messages, model=model):
                        if chunk:
                            full_response += chunk
                            live.update(Markdown(full_response))
                
                if not full_response:
                    self.console.print("[yellow]Plan execution concluded or empty response.[/yellow]")
                    break
            except Exception as e:
                self.console.print(f"\n[red]Execution Error: {e}[/red]")
                break

            self.console.print("\n")
            conversation_messages.append({"role": "assistant", "content": full_response})

            # Process tools
            tool_results = self.tool_registry.process_text(full_response)
            
            if not tool_results:
                # If the AI stopped calling tools, it might be done
                # We can ask it if it's finished or if it needs more steps
                # For now, we'll assume it's done if no tools were called in the last response
                break

            for name, success, output in tool_results:
                result_content = f"Tool {name} result:\n{output}" if output is not None else f"Tool {name} executed successfully."
                if not success:
                    result_content = f"Tool {name} failed or was rejected:\n{output}"
                    self.console.print(f"[red]⚠️ Tool '{name}' failed:[/red] {output}")
                
                conversation_messages.append({
                    "role": "user",
                    "content": result_content
                })

                if not success and not self.tool_registry.tools[name].auto_approve:
                    # Halt if a non-auto-approved tool (like run/create/edit) is rejected or fails
                    # But continue if it's just a read/ls failure (the AI can try again)
                    turn_count = max_turns # Break outer loop
                    break
            
            # If after processing tools, the last message is from assistant (no tools matched), we break
            if conversation_messages[-1]["role"] == "assistant":
                break

    def _execute_with_model(self, user_message: str, model: str):
        self.messages.append({"role": "user", "content": user_message})
        
        while True:
            # Clear console markers for tools if any
            self.console.print(f"\n[cyan]🤖 Flame ({model}):[/cyan] ")

            full_response = ""
            try:
                from rich.live import Live
                # Use a simpler Live setup to avoid potential display issues on some Windows terminals
                with Live(Markdown(""), console=self.console, refresh_per_second=4, transient=False) as live:
                    for chunk in self.client.chat_stream(self.messages, model=model):
                        if chunk:
                            full_response += chunk
                            live.update(Markdown(full_response))
                
                # If for some reason full_response is empty but no exception was raised
                if not full_response:
                    self.console.print("[yellow]Empty response received from AI.[/yellow]")
                    break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                return

            self.console.print("\n")
            self.messages.append({"role": "assistant", "content": full_response})

            # Process tools using ToolRegistry
            tool_results = self.tool_registry.process_text(full_response)
            
            if not tool_results:
                break

            for name, success, output in tool_results:
                # If tool was successful, we tell the AI and the loop continues
                # If it failed or was rejected, we should also inform the AI
                result_content = f"Tool {name} result:\n{output}" if output is not None else f"Tool {name} executed successfully."
                if not success:
                    result_content = f"Tool {name} failed or was rejected:\n{output}"
                    self.console.print(f"[red]⚠️ Tool '{name}' failed:[/red] {output}")
                
                self.messages.append({
                    "role": "user",
                    "content": result_content
                })

                if not success:
                    # Halt further execution if a tool in the sequence fails
                    break

            # After processing all tools in this response, refresh the system prompt
            # so the model sees the updated project structure/context in the next turn.
            self.add_system_message()

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
