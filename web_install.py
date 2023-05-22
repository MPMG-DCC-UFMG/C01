import os
import subprocess

# Install modules from src directory, with their dependencies
src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()
