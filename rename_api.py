import os
import glob

def process_file(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content.replace("Hack Club AI", "API")\
                         .replace("HackClubAIClient", "APIClient")\
                         .replace("hack club", "api")\
                         .replace("Hack Club", "API")\
                         .replace("HACK_CLUB_", "FLAME_")\
                         .replace("ai.hackclub.com", "api.example.com")\
                         .replace("hackclub", "api")
                         
    if content != new_content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {path}")

for path in glob.glob("src/**/*.py", recursive=True) + glob.glob("*.md") + ["tests/test_basic.py", "pyproject.toml"]:
    process_file(path)

