import random
import time
import sys 

# Project libs
from crawler_manager.log_writer import LogWriter
from crawler_manager.message_sender import MessageSender
from crawler_manager.spider_manager_listener import SpiderManagerListener

from crawling_utils import system_running_db_migrations

message_sender = None
if not system_running_db_migrations():
    message_sender = MessageSender()

def log_writer_process():
    '''Redirects log_writer output and starts descriptor consumer loop.'''
    if not system_running_db_migrations():
        LogWriter.log_consumer()
    
def run_spider_manager_listener():
    '''Start spider_manager message consumer loop'''
    if not system_running_db_migrations():
        sm_listener = SpiderManagerListener()
        sm_listener.run()

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