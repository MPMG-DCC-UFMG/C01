# Scrapy and Twister libs
import scrapy
from scrapy.crawler import CrawlerProcess

# Other external libs
import json
import os
import random
import requests
import shutil
import sys
import time
from multiprocessing import Process

# Project libs
import crawling_utils.crawling_utils as crawling_utils
from crawlers.constants import *
from crawlers.file_descriptor import FileDescriptor

from crawlers.command_sender import CommandSender

KAFKA_HOSTS = ['localhost:9092']
COMMANDS_TOPIC = 'spider_manager-commands'

command_sender = CommandSender(KAFKA_HOSTS, COMMANDS_TOPIC)

def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))

def generate_initial_requests(config: dict):
    data = {
        "url": config['base_url'],
        "appid": config['instance_id'],
        "crawlid": str(config['crawler_id']),
        "spiderid": 'static_page',
        "attrs": {
            "referer": "start_requests"
        }
    }


    url = 'http://0.0.0.0:5343/feed'
    headers = {'content-type': 'application/json'}

    print('\nFeeding API\n')
    req = requests.post(url, data=json.dumps(data), headers=headers)
    print(req.json())

def start_crawler(config):
    """Create and starts a crawler as a new process."""
    config["crawler_id"] = config["id"]
    del config["id"]
    config["instance_id"] = gen_key()
    
    command_sender.send_create_spider(config)
    generate_initial_requests(config)

    return config["instance_id"]

def stop_crawler(instance_id, config):
    """Sets the flags of a crawler to stop."""
    command_sender.send_stop_crawl(str(instance_id)) 

def update_instances_info(data_path: str, instance_id: str, instance: dict):
    """Updates the file with information about instances when they are created, initialized or terminated."""
    pass
    # instances = dict()

    # filename = f"{data_path}/instances.json"
    # if os.path.exists(filename):
    #     with open(filename) as f:
    #         instances = json.loads(f.read())

    # instances[instance_id] = instance
    # with open(filename, "w+") as f:
    #     f.write(json.dumps(instances, indent=4))
