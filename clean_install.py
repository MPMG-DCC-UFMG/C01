import subprocess

subprocess.run("docker-compose down".split())
subprocess.run("docker-compose -f docker-compose.yml down --rmi all -v".split())
subprocess.run("rm -r ./main/migrations".split())
subprocess.run("mkdir -m 777 ./main/migrations".split())
subprocess.run("touch ./main/migrations/__init__.py".split())
subprocess.run("docker-compose build --parallel".split())
