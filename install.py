import os
import subprocess
import asyncio
import sys
import json
import getpass

###################### PEGANDO A PASSWORD
try:
    pass_1 = getpass.getpass(prompt='Choose a password for Redis DB: ')
except Exception as error: 
    print('ERROR', error)   
else: 
    pass_2 = getpass.getpass(prompt='Confirm password for Redis DB: ')

if pass_1 == pass_2:
    with open('clustersettings.json', 'r') as json_file:
        settings = json.load(json_file)
        settings["REDIS_PASSWORD"] = pass_2

    with open('clustersettings.json', 'w') as json_file:
        json.dump(settings, json_file, indent=4)
else:
    print("Passwords didn't match. Aborting...")
    sys.exit(0)
        

###################### INSTALANDO O REDIS
subprocess.run(["wget", "https://download.redis.io/releases/redis-5.0.10.tar.gz"])
subprocess.run(["tar", "-xvzf", "redis-5.0.10.tar.gz"])

with open('clustersettings.json', 'r') as json_file:
    settings = json.load(json_file)
    expr = "s/\<6379\>/" + str(settings['REDIS_PORT']) + "/g"
    subprocess.run(["find", ".", "-type", "f", "-exec", "sed", "-i", expr, "{}", "+"], cwd=".")

subprocess.run(["make"], cwd="redis-5.0.10")
subprocess.run(["rm", "redis-5.0.10.tar.gz"])


###################### ALTERANDO A SENHA DO REDIS
with open('clustersettings.json', 'r') as json_file:
    settings = json.load(json_file)
    expr = "s/# requirepass foobared/requirepass " + settings['REDIS_PASSWORD'] + "/g"
    subprocess.run(["sed", "-i", expr, "redis.conf"], cwd="redis-5.0.10")


###################### INSTALANDO O KAFKA / ZOOKEEPER
subprocess.run(["wget", "http://www-us.apache.org/dist/kafka/2.4.0/kafka_2.13-2.4.0.tgz"])
subprocess.run(["tar", "-xzf", "kafka_2.13-2.4.0.tgz"])
subprocess.run(["rm", "kafka_2.13-2.4.0.tgz"])


###################### ADICIONANDO WHITELIST TO ZOOKEEPER
with open("kafka_2.13-2.4.0/config/zookeeper.properties", "a") as f:
    f.write("4lw.commands.whitelist=*")


###################### INSTALANDO OS MÓDULOS DO PROJETO
src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()


print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "."])
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