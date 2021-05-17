
import json
import logging
import os
import random
import requests
import shutil
import sys
import time
from multiprocessing import Process
from datetime import datetime

import tldextract
import redis
from redis.exceptions import ConnectionError

# Project libs
from crawlers.constants import *
from crawlers.log_writer import LogWriter
from crawlers.command_sender import CommandSender
from crawlers.spider_manager_handler import SpiderManagerHandler
from crawlers import settings


extractor = tldextract.TLDExtract()
command_sender = CommandSender()
redis_conn = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        password=settings.REDIS_PASSWORD,
                        decode_responses=True,
                        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                        socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT)

try:
    redis_conn.info()
    
except ConnectionError:
    sys.error("Failed to connect to Redis in ScraperHandler")
    sys.exit(1)

sm_handler = SpiderManagerHandler()

def log_writer_process():
    """Redirects log_writer output and starts descriptor consumer loop."""

    # crawling_utils.check_file_path("crawlers/log/")
    # sys.stdout = open(f"crawlers/log/log_writer.out", "a", buffering=1)
    # sys.stderr = open(f"crawlers/log/log_writer.err", "a", buffering=1)

    LogWriter.log_consumer()

def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))

def format_request(config: dict) -> dict:
    formated_request = {
                    "url": config['base_url'],
                    "appid":"162099279113314",
                    "crawlid": str(config['crawler_id']),
                    "spiderid": str(config['crawler_id']),
                    "attrs":{
                        "referer": "start_requests"
                    },
                    "priority":1,
                    "maxdepth":0,
                    "domain_max_pages": None,
                    "allowed_domains": None,
                    "allow_regex": None,
                    "deny_regex": None,
                    "deny_extensions": None,
                    "expires":0,
                    "useragent": None,
                    "cookie": None,
                    "ts": datetime.now().timestamp()
                }

    return formated_request

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

    req = format_request(config)

    ex_res = extractor(req['url'])
    key = "{sid}:{dom}.{suf}:queue".format(
        sid=req['spiderid'],
        dom=ex_res.domain,
        suf=ex_res.suffix)

    val = json.dumps(req)
    redis_conn.zadd(key, {val: -req['priority']})


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
