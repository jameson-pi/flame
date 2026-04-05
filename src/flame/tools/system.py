"""System tools."""

from .base import Tool

def run_command_tool(command_executor):
    return Tool(
        name="run",
        description="Execute shell command (requires permission)",
        usage='/run command="..."',
        handler=command_executor.suggest_command,
        regex_pattern=r'/run\s+(?:command)?[:=]?\s*(?P<q>["\'])(?P<command>.*?)(?P=q)|/run\s+(?P<command_simple>[^\n\r]+)',
        example='/run command="npm install"'
    )
