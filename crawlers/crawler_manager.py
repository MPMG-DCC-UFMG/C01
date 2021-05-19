
import json
import random
import sys
import time
from datetime import datetime

import tldextract
import redis
from redis.exceptions import ConnectionError

# Project libs
from crawlers.log_writer import LogWriter
from crawlers.command_sender import CommandSender
from crawlers.spider_manager_handler import SpiderManagerListener
from crawlers import settings

command_sender = CommandSender()

# Responsible for extracting the domain and subdomain from a url
extractor = tldextract.TLDExtract()
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
    sys.error("Failed to connect to Redis")
    sys.exit(1)

sm_listener = SpiderManagerListener()

def log_writer_process():
    """Redirects log_writer output and starts descriptor consumer loop."""
    LogWriter.log_consumer()

def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))

def format_request(config: dict) -> dict:
    """Formats a collection request according to Scrapy Cluster standards
    
    Args:
        - Config: Scraper configuration to be processed
    
    Returns:

        Returns a scraping request in the Scrapy Cluster pattern
    """

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
    """Generates initial requests
    
    Args:
        - Config: Scraper configuration to be processed
    
    """
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

def start_crawler(config: dict):
    """Send the command to the spider managers to create the spiders.
   
    Args:
        - Config: Scraper configuration to be processed
   
    """

    config["crawler_id"] = config["id"]
    del config["id"]
    generate_initial_requests(config)
    command_sender.send_create_spider(config)

def stop_crawler(crawler_id):
    """Send the command to the spider managers to stop the spiders.
    
    Args:
        - crawler_id: Uniquer crawler identifier

    """


    command_sender.send_stop_crawl(str(crawler_id))

def update_instances_info(data_path: str, instance_id: str, instance: dict):
    """Updates the file with information about instances when they are created, initialized or terminated."""
    pass
