import json
import itertools
import random
import sys
import time
from datetime import datetime

# Project libs
from crawler_manager.log_writer import LogWriter
from crawler_manager.message_sender import MessageSender
from crawler_manager.spider_manager_handler import SpiderManagerListener
from crawler_manager import settings

from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest, HTTPStatusProbingResponse, TextMatchProbingResponse, EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference

message_sender = MessageSender()
sm_listener = SpiderManagerListener()

def log_writer_process():
    """Redirects log_writer output and starts descriptor consumer loop."""
    LogWriter.log_consumer()

def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))

def start_crawler(config: dict):
    """Send the command to the spider managers to create the spiders.
   
    Args:
        - Config: Scraper configuration to be processed
   
    """

    config["crawler_id"] = config["id"]
    del config["id"]
    
    message_sender.send_start_crawl(config)

def stop_crawler(crawler_id):
    """Send the command to the spider managers to stop the spiders.
    
    Args:
        - crawler_id: Uniquer crawler identifier

    """
    message_sender.send_stop_crawl(str(crawler_id))

def update_instances_info(data_path: str, instance_id: str, instance: dict):
    """Updates the file with information about instances when they are created, initialized or terminated."""
    pass
