import os
import subprocess

subprocess.run(["pip", "install", "-U", "pip"])

print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "-r" "requirements.txt"])
print()

# Install modules from src directory, with their dependencies
src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()