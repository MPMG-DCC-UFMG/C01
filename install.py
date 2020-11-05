import os
import subprocess
import asyncio


src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()

print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "."])
print()

from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())


print(f"Creating database...")
subprocess.run(["python", "manage.py", "makemigrations"])
subprocess.run(["python", "manage.py", "migrate"])
print()
