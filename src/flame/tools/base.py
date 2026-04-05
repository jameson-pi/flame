"""Base class for all Flame tools."""

import re
from typing import Callable, List, Optional, Tuple

class Tool:
    """Represents a single command tool available to the AI."""

    def __init__(
        self,
        name: str,
        description: str,
        usage: str,
        handler: Callable,
        regex_pattern: Optional[str] = None,
        auto_approve: bool = False,
        example: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.usage = usage
        self.handler = handler
        self.regex = re.compile(regex_pattern, re.IGNORECASE | re.DOTALL) if regex_pattern else None
        self.auto_approve = auto_approve
        self.example = example

    def find_matches(self, text: str) -> List[Tuple[int, re.Match]]:
        """Find all starting positions of this tool's matches in the text.
        
        Returns:
            List of (start_index, Match object)
        """
        if not self.regex:
            return []
            
        valid_matches = []
        for m in self.regex.finditer(text):
            # Ensure command is at the start of a line (ignoring whitespace)
            # This prevents accidental matches within paragraph text (e.g. "tools like /read")
            match_start = m.start()
            string_before = text[:match_start]
            last_newline = string_before.rfind('\n')
            line_start = string_before[last_newline + 1:] if last_newline != -1 else string_before
            
            if not line_start.strip():
                valid_matches.append((match_start, m))
                
        return valid_matches

    def execute_match(self, match: re.Match) -> Tuple[bool, str]:
        """Execute the tool for a specific match object."""
        # Get only the groups that matched and are not None
        raw_args = {k: v for k, v in match.groupdict().items() if v is not None}
        
        # Clean up keys ending in _simple (internal routing workaround)
        args = {}
        for k, v in raw_args.items():
            if re.match(r'^q\d*$', k):  # Skip internal quote-matching groups
                continue
            
            val = v
            # Strip wrapping quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            
            clean_key = k.replace("_simple", "")
            # If both key and key_simple exist, the explicit keyword takes precedence
            if clean_key not in args or not k.endswith("_simple"):
                args[clean_key] = val
        
        # If no groupdict, use groups as positional args
        if not args:
            args_list = [v for v in match.groups() if v is not None]
            if not args_list: return False, "No arguments found"
            
            try:
                # For positional args, we need to hope the handler signature matches
                result = self.handler(*args_list)
            except Exception as e:
                return False, f"Error executing tool {self.name} with positional args: {e}"
        else:
            # Execute handler with cleaned up keyword args
            try:
                result = self.handler(**args)
            except Exception as e:
                return False, f"Error executing tool {self.name}: {e}"
        
        # Ensure it returns (success, output)
        if isinstance(result, tuple) and len(result) == 2:
            return result[0], str(result[1])
        elif isinstance(result, bool):
             return result, ""
        else:
            return True, str(result)

    def parse_and_execute(self, text: str) -> Optional[Tuple[bool, str]]:
        """Parse command from text and execute if found.
        
        Returns:
            Tuple of (success, output) if matched, else None.
        """
        if not self.regex:
            return None
        
        match = self.regex.search(text)
        if match:
            return self.execute_match(match)
        
        return None

