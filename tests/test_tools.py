import pytest
from flame.tools.base import Tool
import re

def test_find_matches_simple():
    content = "This is a text. /my_tool arg=\"value\""
    pattern = r"^\s*/(?P<command>my_tool)\s+(?P<args>.*)$"
    tool = Tool(name="my_tool", description="test", usage="test", handler=lambda **kwargs: "", regex_pattern=pattern)
    
    # Needs to match at start of line according to recent changes, so let's adjust content
    content_valid = "\n/my_tool arg=\"value\""
    matches = tool.find_matches(content_valid)
    assert len(matches) == 1
    assert matches[0][1].group("command") == "my_tool"

def test_find_matches_ignores_inline():
    content_invalid = "Here is an inline /my_tool arg=\"value\" that should be ignored."
    pattern = r"^\s*/(?P<command>my_tool)\s+(?P<args>.*)$"
    tool = Tool(name="my_tool", description="test", usage="test", handler=lambda **kwargs: "", regex_pattern=pattern)
    matches = tool.find_matches(content_invalid)
    assert len(matches) == 0

def dummy_handler(**kwargs):
    return True, f"Dummy executed with {kwargs.get('arg')}"

def test_tool_execute():
    pattern = r"^\s*/(?P<command>dummy)\s+arg=(?P<q>[\"'])(?P<arg>.*?)(?P=q)"
    tool = Tool(name="dummy", description="Dummy tool", usage="/dummy arg='x'", handler=dummy_handler, regex_pattern=pattern)
    
    content = "\n/dummy arg=\"hello\""
    matches = tool.find_matches(content)
    assert len(matches) == 1
    
    success, result = tool.execute_match(matches[0][1])
    assert success is True
    assert result == "Dummy executed with hello"
