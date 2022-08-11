import subprocess

subprocess.run("docker-compose down".split())
subprocess.run("docker-compose build --parallel".split())