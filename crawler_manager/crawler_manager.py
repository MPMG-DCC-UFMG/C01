from cmath import log
from glob import glob
import random
import time

# Project libs
from crawler_manager.log_writer import LogWriter
from crawler_manager.message_sender import MessageSender
from crawler_manager.spider_manager_listener import SpiderManagerListener

from crawling_utils import system_is_deploying

MESSAGE_SENDER = None
LOG_WRITER = None 

if not system_is_deploying():
    MESSAGE_SENDER = MessageSender()

def run_kafka_listeners():
    '''Start spider_manager message consumer loop'''
    global LOG_WRITER
    
    if not system_is_deploying():
        sm_listener = SpiderManagerListener()
        sm_listener.run()
        
        LOG_WRITER = LogWriter()
        LOG_WRITER.run()

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

    MESSAGE_SENDER.send_start_crawl(config)


def stop_crawler(crawler_id):
    """Send the command to the spider managers to stop the spiders.

    Args:
        - crawler_id: Uniquer crawler identifier

    """
    MESSAGE_SENDER.send_stop_crawl(str(crawler_id))
