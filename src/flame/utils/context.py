"""Gather system context for AI awareness of the development environment."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console
import pathspec


class SystemContext:
    """Collect and format system context information."""

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize context collector.
        
        Args:
            working_dir: Working directory to analyze (defaults to current)
        """
        self.working_dir = Path(working_dir or os.getcwd())
        self.console = Console()
        self.gitignore = self._load_gitignore()
        self.snippets: Dict[str, str] = {}

    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load and parse .gitignore file if it exists."""
        gitignore_path = self.working_dir / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    return pathspec.PathSpec.from_lines('gitwildmatch', f)
            except Exception:
                pass
        return None

    def inject_snippet(self, name: str, content: str):
        """Add a dynamic context snippet (e.g., current file content)."""
        self.snippets[name] = content

    def remove_snippet(self, name: str):
        """Remove a dynamic context snippet."""
        if name in self.snippets:
            del self.snippets[name]

    def _is_ignored(self, path: Path) -> bool:
        """Check if a path is ignored by .gitignore."""
        if not self.gitignore:
            return False
        
        # Get relative path for matching
        try:
            rel_path = str(path.relative_to(self.working_dir))
            # pathspec expects directories to end with / if matching directory patterns
            if path.is_dir() and not rel_path.endswith('/'):
                rel_path += '/'
            return self.gitignore.match_file(rel_path)
        except ValueError:
            return False

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
                # Skip hidden dirs, common ignore patterns, AND gitignored files
                entries = [e for e in entries if not e.name.startswith(".") 
                          and e.name not in {"__pycache__", "node_modules", "venv", ".venv"}
                          and not self._is_ignored(e)]
                
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
            # Avoid rglob("*") in potentially huge directories like user home
            # Instead, just walk the top level or a small subset
            # For now, let's limit it to one level deeep or skip in huge dirs
            for path in self.working_dir.iterdir():
                if path.is_file() and not path.name.startswith(".") and not self._is_ignored(path):
                    ext = path.suffix or "no_ext"
                    extensions[ext] = extensions.get(ext, 0) + 1
                    total += 1
                elif path.is_dir() and not path.name.startswith(".") and not self._is_ignored(path):
                    # For directories, maybe just count them?
                    pass
        except PermissionError:
            pass
        
        summary = f"Total top-level files: {total}\n"
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
        
        if self.snippets:
            context_parts.append("\n📝 Active Context Snippets:")
            for name, content in self.snippets.items():
                context_parts.append(f"--- {name} ---\n{content}\n--- End Snippet ---")
        
        return "\n".join(context_parts)

    def get_context_prompt(self) -> str:
        """Get system context as a pre-prompt for AI responses."""
        return (
            f"You are assisting in a development environment with the following context:\n\n"
            f"{self.get_full_context()}\n\n"
            f"Use this context to provide accurate, contextual assistance."
        )
