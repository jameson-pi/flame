"""Registry to manage and dispatch tools."""

from typing import Dict, List, Tuple, Optional
from rich.console import Console
from .base import Tool

class ToolRegistry:
    """Registry to manage and dispatch tools."""

    def __init__(self, console: Optional[Console] = None):
        self.tools: Dict[str, Tool] = {}
        self.console = console or Console()

    def register_tool(self, tool: Tool):
        """Register a new tool."""
        self.tools[tool.name] = tool

    def get_system_prompt_fragment(self) -> str:
        """Generate the 'COMMANDS AVAILABLE' section for the system prompt."""
        fragment = "COMMANDS AVAILABLE (CRITICAL: EXECUTED TOP-TO-BOTTOM, ONE COMMAND PER LINE, NEVER PUT TWO COMMANDS ON THE SAME LINE):\n"
        for i, (name, tool) in enumerate(self.tools.items(), 1):
            approval = "(AUTO-APPROVED)" if tool.auto_approve else "(REQUIRES PERMISSION)"
            fragment += f"{i}. {tool.usage} - {tool.description} {approval}\n"
            if tool.example:
                fragment += f"   Example: {tool.example}\n"
        return fragment

    def process_text(self, text: str) -> List[Tuple[str, bool, str]]:
        """Scan text for all registered tools and execute them in the order they appear.
        
        Returns:
            List of (tool_name, success, output)
        """
        all_matches = []
        for name, tool in self.tools.items():
            matches = tool.find_matches(text)
            for start_pos, match in matches:
                all_matches.append((start_pos, match.end(), tool, match))
        
        # Sort matches by their starting position in the text
        all_matches.sort(key=lambda x: x[0])
        
        results = []
        last_end = 0
        for start, end, tool, match in all_matches:
            if start < last_end:
                # Skip overlapping matches (usually caused by greedy fallbacks swallowing next command)
                continue
            last_end = end
            success, output = tool.execute_match(match)
            results.append((tool.name, success, output))
            
        return results

