import os
import subprocess

subprocess.run(["pip", "install", "-U", "pip"])

import asyncio
import shutil
import sys

subprocess.run(["pip", "install", "-U", "pip"])
subprocess.run(["pip", "install", "twisted"])
subprocess.run(["pip", "install", "django-environ"])

import environ
from twisted.internet import asyncioreactor

# Initialize Django-environ to read settings from environment variables
env = environ.Env(
    # set casting, default value
    INSTALL_REDIS=(bool, True),
    INSTALL_KAFKA=(bool, True),
    EXECUTION_TYPE=(str, "standalone"),
)

if env('INSTALL_REDIS'):
    # Install Redis
    if not os.path.isdir("redis-5.0.10"):
        subprocess.run(["wget", "https://download.redis.io/releases/redis-5.0.10.tar.gz"])
        subprocess.run(["tar", "-xvzf", "redis-5.0.10.tar.gz"])
        subprocess.run(["make"], cwd="redis-5.0.10")
        subprocess.run(["rm", "redis-5.0.10.tar.gz"])

if env('INSTALL_KAFKA'):
    # Install Kafka and Zookeeper
    if not os.path.isdir("kafka_2.13-2.4.0"):
        subprocess.run(["wget", "http://archive.apache.org/dist/kafka/2.4.0/kafka_2.13-2.4.0.tgz"])
        subprocess.run(["tar", "-xzf", "kafka_2.13-2.4.0.tgz"])
        subprocess.run(["rm", "kafka_2.13-2.4.0.tgz"])

    # Overwrites zookeeper.properties
    # Please, make sure you have zoo.properties in this directory.
    # If not, make sure you have it on kafka_<version>/config/
    if os.path.isfile("zoo.properties"):
        shutil.copy("zoo.properties", "kafka_2.13-2.4.0/config/zoo.properties")

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


try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    asyncioreactor.install(loop)
except Exception:
    pass

if env("EXECUTION_TYPE") == "standalone":
    print(f"Creating database...")
    subprocess.run(["python", "manage.py", "makemigrations"])
    subprocess.run(["python", "manage.py", "migrate"])
    print()
