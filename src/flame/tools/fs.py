"""File system tools."""

from .base import Tool

def create_file_tool(file_executor):
    return Tool(
        name="create",
        description="Create a new file (requires permission)",
        usage='/create path="..." content="..."',
        handler=file_executor.suggest_file_creation,
        regex_pattern=r'/create\s+(?:(?:path|filepath|file)[:=]?\s*)?(?P<q>["\'])(?P<filepath>.*?)(?P=q)(?:\s+(?:content[:=]?\s*)?(?P<q2>["\'])(?P<content>(?:\\.|(?!(?P=q2)).)*)(?P=q2))?|/create\s+(?P<filepath_simple>[^\s"\'\n\r]+)\s+(?P<content_simple>[^\n]+)',
        example='/create path="hello.py" content="print(\'hello\')"'
    )

def read_file_tool(file_executor):
    return Tool(
        name="read",
        description="Read file content (AUTO-APPROVED)",
        usage='/read path="..."',
        handler=file_executor.read_file,
        regex_pattern=r'/read\s+(?:path|filepath|file)?[:=]?\s*["\'](?P<filepath>.*?)["\']|/read\s+(?P<filepath_simple>[^\s\n\r]+)',
        auto_approve=True,
        example='/read path="main.py"'
    )

def edit_file_tool(file_executor):
    return Tool(
        name="edit",
        description="Edit a file (requires permission)",
        usage='/edit path="..." old_content="..." new_content="..."',
        handler=file_executor.suggest_file_edit,
        regex_pattern=r'/edit\s+(?:path|filepath|file)[:=]?\s*["\'](?P<filepath>.*?)["\']\s+old_content[:=]?\s*["\'](?P<old_content>.*?)["\']\s+new_content[:=]?\s*["\'](?P<new_content>.*?)["\']',
        example='/edit path="app.py" old_content="print(\'old\')" new_content="print(\'new\')"'
    )

def ls_tool(file_executor):
    return Tool(
        name="ls",
        description="List directory items (AUTO-APPROVED)",
        usage='/ls directory="..."',
        handler=file_executor.list_dir,
        regex_pattern=r'/ls\s+(?:directory|dir)?[:=]?\s*["\'](?P<directory>.*?)["\']|/ls\s*(?P<directory_simple>[^\s\n\r]*)',
        auto_approve=True,
        example='/ls directory="src"'
    )

def find_tool(file_executor):
    return Tool(
        name="find",
        description="Find files by glob pattern (AUTO-APPROVED)",
        usage='/find pattern="..."',
        handler=file_executor.find_files,
        regex_pattern=r'/find\s+(?:pattern)?[:=]?\s*["\'](?P<pattern>.*?)["\']|/find\s+(?P<pattern_simple>[^\s\n\r]+)',
        auto_approve=True,
        example='/find pattern="**/*.py"'
    )

def grep_tool(file_executor):
    return Tool(
        name="grep",
        description="Search text in files (AUTO-APPROVED)",
        usage='/grep query="..." pattern="..."',
        handler=file_executor.grep_search,
        regex_pattern=r'/grep\s+query[:=]?\s*["\'](?P<query>.*?)["\'](?:\s+pattern[:=]?\s*["\'](?P<pattern>.*?)["\'])?|/grep\s+["\'](?P<query_simple>.*?)["\']\s*["\']?(?P<pattern_simple>.*?)["\']?$',
        auto_approve=True,
        example='/grep query="TODO" pattern="src/**/*.ts"'
    )

def errors_tool(file_executor):
    return Tool(
        name="errors",
        description="Check Python syntax errors (AUTO-APPROVED)",
        usage='/errors path="..."',
        handler=file_executor.get_errors,
        regex_pattern=r'/errors\s+(?:path|filepath|file)?[:=]?\s*["\'](?P<filepath>.*?)["\']|/errors\s+(?P<filepath_simple>[^\s\n\r]+)',
        auto_approve=True,
        example='/errors path="broken.py"'
    )
