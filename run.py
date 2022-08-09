import time
import subprocess

subprocess.run("docker-compose down".split())
subprocess.run("docker volume rm c01_static_volume".split())
subprocess.run("docker-compose build --parallel".split())
subprocess.run("docker-compose up -d".split())
time.sleep(10)
print("Finished")