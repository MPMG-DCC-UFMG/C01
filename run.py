import time
import subprocess
import os
import argparse

parser = argparse.ArgumentParser(description='Run docker compose to build and up the container.')
parser.add_argument('-d', '--debug', default='main',
                    help='set environment variable file used on docker compose to debug (debug) or not (main) the docker execution (default: main)')
args = vars(parser.parse_args())

myenv = {
    **os.environ,
    "ENVFILENAME": str(args["debug"]),
}
subprocess.run("docker compose down".split(), env=myenv)
subprocess.run("docker compose -f docker-compose-cleanup.yml down -v".split(), env=myenv)
subprocess.run("docker compose build --parallel".split(), env=myenv)
subprocess.run("docker compose up -d".split(), env=myenv)
time.sleep(10)
print("Finished")