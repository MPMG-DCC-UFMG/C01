import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description='Performs a clean install, running docker compose to build the container.')
parser.add_argument('-d', '--debug', default='main',
                    help='set environment variable file used on docker compose to debug (debug) or not (main) the docker execution (default: main)')
args = vars(parser.parse_args())

myenv = {
    **os.environ,
    "ENVFILENAME": str(args["debug"]),
}


subprocess.run("docker-compose down".split(), env=myenv)
subprocess.run("docker-compose -f docker-compose.yml down --rmi all -v".split(), env=myenv)
subprocess.run("rm -r ./main/migrations".split())
subprocess.run("mkdir -m 777 ./main/migrations".split())
subprocess.run("touch ./main/migrations/__init__.py".split())
subprocess.run("docker-compose build --parallel".split(), env=myenv)
