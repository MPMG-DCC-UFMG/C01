import os
import subprocess

subprocess.run(["pip", "install", "-U", "pip"])

import asyncio

subprocess.run(["pip", "install", "-U", "pip"])
subprocess.run(["pip", "install", "twisted"])
subprocess.run(["pip", "install", "django-environ"])

import environ
from twisted.internet import asyncioreactor

# Initialize Django-environ to read settings from environment variables
env = environ.Env(
    # set casting, default value
    EXECUTION_TYPE=(str, "standalone"),
)

# Install modules from src directory, with their dependencies
src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()

print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "-r" "requirements.txt"])
print()

if env("EXECUTION_TYPE") == "standalone":
    print(f"Creating database...")
    subprocess.run(["python", "manage.py", "makemigrations"])
    subprocess.run(["python", "manage.py", "migrate"])
    print()
