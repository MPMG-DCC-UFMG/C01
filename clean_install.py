import subprocess

subprocess.run("docker-compose down".split())
subprocess.run("docker-compose rm --volumes".split())
subprocess.run("rm -r main/migrations/*".split())
subprocess.run("docker-compose build --parallel".split())
