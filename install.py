from twisted.internet import asyncioreactor
import os
import subprocess
import asyncio
import sys

# INSTALANDO O REDIS
if not os.path.isdir('redis-5.0.10'):
    subprocess.run(["wget", "https://download.redis.io/releases/redis-5.0.10.tar.gz"])
    subprocess.run(["tar", "-xvzf", "redis-5.0.10.tar.gz"])
    subprocess.run(["make"], cwd="redis-5.0.10")
    subprocess.run(["rm", "redis-5.0.10.tar.gz"])

# INSTALANDO O KAFKA / ZOOKEEPER
if not os.path.isdir('kafka_2.13-2.4.0'):
    subprocess.run(["wget", "http://www-us.apache.org/dist/kafka/2.4.0/kafka_2.13-2.4.0.tgz"])
    subprocess.run(["tar", "-xzf", "kafka_2.13-2.4.0.tgz"])
    subprocess.run(["rm", "kafka_2.13-2.4.0.tgz"])

# INSTALANDO OS MÓDULOS DO PROJETO
src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()

print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "."])
print()

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
