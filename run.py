import subprocess
import sys
import os
import shutil

def run_tests():
    print("🚀 Running tests...")
    subprocess.run(["pytest", "tests"])

def install():
    print("🛠️ Installing in editable mode...")
    subprocess.run(["pip", "install", "-e", ".[dev]"])

def clean():
    print("🧹 Cleaning cache files...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".pyc", ".pyo", ".pyd")):
                try:
                    os.remove(os.path.join(root, file))
                except: pass
        for adir in dirs:
            if adir in ("__pycache__", ".pytest_cache", "flame.egg-info"):
                shutil.rmtree(os.path.join(root, adir), ignore_errors=True)

if __name__ == "__main__":
    commands = {
        "test": run_tests,
        "clean": clean,
        "install": install
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in commands:
        commands[sys.argv[1]]()
    else:
        print(f"Usage: python run.py [{'|'.join(commands.keys())}]")