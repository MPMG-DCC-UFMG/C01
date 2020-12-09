import os
import subprocess
import asyncio


src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "--no-cache-dir", "install", "--force-reinstall", f"{src_folder}/{folder}"])
        print()

print(f"Installing other project dependencies...")
subprocess.run(["pip", "--no-cache-dir", "install", "--force-reinstall", "."])
print()

from twisted.internet import asyncioreactor
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    asyncioreactor.install(loop)
except Exception:
    pass

print(f"Creating database...")
subprocess.run(["python", "manage.py", "makemigrations"])
subprocess.run(["python", "manage.py", "migrate"])
print()
