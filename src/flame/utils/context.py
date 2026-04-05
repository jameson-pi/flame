"""Gather system context for AI awareness of the development environment."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict
from rich.console import Console


class SystemContext:
    """Collect and format system context information."""

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize context collector.
        
        Args:
            working_dir: Working directory to analyze (defaults to current)
        """
        self.working_dir = Path(working_dir or os.getcwd())
        self.console = Console()

    def get_os_info(self) -> str:
        """Get OS and Python version information."""
        return f"{platform.system()} {platform.release()} | Python {platform.python_version()}"

    def get_git_status(self) -> Optional[str]:
        """Get git branch and status if in a git repo."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--branch"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    def get_project_structure(self, max_depth: int = 2) -> str:
        """Get directory tree structure.
        
        Args:
            max_depth: Maximum depth to traverse
            
        Returns:
            Formatted directory tree
        """
        def build_tree(path: Path, prefix: str = "", depth: int = 0) -> str:
            if depth > max_depth:
                return ""
            
            items = []
            try:
                entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                # Skip hidden dirs and common ignore patterns
                entries = [e for e in entries if not e.name.startswith(".") 
                          and e.name not in {"__pycache__", "node_modules", "venv", ".venv"}]
                
                for i, entry in enumerate(entries[:10]):  # Limit to 10 entries per dir
                    is_last = i == len(entries) - 1
                    current_prefix = "└── " if is_last else "├── "
                    items.append(f"{prefix}{current_prefix}{entry.name}")
                    
                    if entry.is_dir() and depth < max_depth:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        items.append(build_tree(entry, next_prefix, depth + 1))
            except PermissionError:
                pass
            
            return "\n".join(filter(None, items))

        tree = f"{self.working_dir.name}/\n"
        tree += build_tree(self.working_dir)
        return tree

    def get_file_summary(self) -> str:
        """Get count of major file types in project."""
        extensions = {}
        total = 0
        
        try:
            for path in self.working_dir.rglob("*"):
                if path.is_file() and not path.parts[-1].startswith("."):
                    ext = path.suffix or "no_ext"
                    extensions[ext] = extensions.get(ext, 0) + 1
                    total += 1
        except PermissionError:
            pass
        
        summary = f"Total files: {total}\n"
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary += f"  {ext}: {count}\n"
        
        return summary

    def get_full_context(self) -> str:
        """Compile full context as a formatted string for AI injection."""
        context_parts = [
            f"📍 Working Directory: {self.working_dir}",
            f"🖥️  System: {self.get_os_info()}",
            "\n📂 Project Structure:",
            self.get_project_structure(),
            "\n📊 File Summary:",
            self.get_file_summary(),
        ]
        
        git_status = self.get_git_status()
        if git_status:
            context_parts.insert(4, f"\n🌿 Git Status:\n{git_status}")
        
        return "\n".join(context_parts)

    def get_context_prompt(self) -> str:
        """Get system context as a pre-prompt for AI responses."""
        return (
            f"You are assisting in a development environment with the following context:\n\n"
            f"{self.get_full_context()}\n\n"
            f"Use this context to provide accurate, contextual assistance."
        )

