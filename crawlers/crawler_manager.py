# Scrapy and Twister libs
import scrapy
from scrapy.crawler import CrawlerProcess

# Other external libs
import json
import logging
import os
import random
import requests
import shutil
import sys
import time
from multiprocessing import Process

# Project libs
from crawlers.constants import *
from crawlers.log_writer import LogWriter
from crawlers.command_sender import CommandSender

command_sender = CommandSender()

def log_writer_process():
    """Redirects log_writer output and starts descriptor consumer loop."""

    # crawling_utils.check_file_path("crawlers/log/")
    # sys.stdout = open(f"crawlers/log/log_writer.out", "a", buffering=1)
    # sys.stderr = open(f"crawlers/log/log_writer.err", "a", buffering=1)

    LogWriter.log_consumer()

def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))

def generate_initial_requests(config: dict):
    data = {
        "url": config['base_url'],
        "appid": config['instance_id'],
        "crawlid": str(config['crawler_id']),
        "spiderid": str(config['crawler_id']),
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

    generate_initial_requests(config)

    command_sender.send_create_spider(config)

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
