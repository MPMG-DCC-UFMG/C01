import time
import subprocess
import os
import argparse

parser = argparse.ArgumentParser(description='Run docker compose to build and up de container.')
parser.add_argument('-d', '--debug', default='nodebug',
                    help='set environment variable file used on docker compose to debug (debug) or not (nodebug) the docker execution (default: nodebug)')
args = vars(parser.parse_args())

myenv = {
    **os.environ,
    "DEBUGENV": str(args["debug"]),
}
subprocess.run("docker-compose down".split())
subprocess.run("docker volume rm c01_static_volume".split())
subprocess.run("docker-compose build --parallel".split(), env=myenv)
subprocess.run("docker-compose up -d".split(), env=myenv)
time.sleep(10)
print("Finished")