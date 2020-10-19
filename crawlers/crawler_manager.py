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
from crawlers.file_downloader import FileDownloader
from crawlers.static_page import StaticPageSpider

# TODO: implement following antiblock options
# antiblock_mask_type
# antiblock_ip_rotation_type
# antiblock_proxy_list
# antiblock_max_reqs_per_ip
# antiblock_max_reuse_rounds
# antiblock_reqs_per_user_agent
# antiblock_user_agents_file
# antiblock_cookies_file
# antiblock_persist_cookies

def file_downloader_process():
    """Redirects downloader output and starts downloader consumer loop."""
    crawling_utils.check_file_path("crawlers/log/")
    sys.stdout = open(f"crawlers/log/file_downloader.out", "a", buffering=1)
    sys.stderr = open(f"crawlers/log/file_downloader.err", "a", buffering=1)
    FileDownloader.download_consumer()


def file_descriptor_process():
    """Redirects descriptor output and starts descriptor consumer loop."""
    crawling_utils.check_file_path("crawlers/log/")
    sys.stdout = open(f"crawlers/log/file_descriptor.out", "a", buffering=1)
    sys.stderr = open(f"crawlers/log/file_descriptor.err", "a", buffering=1)
    FileDescriptor.description_consumer()


def start_consumers_and_producers():
    """Starts file_description and file_downlaoder processes."""
    downloader = Process(target=file_downloader_process)
    downloader.start()

    descriptor = Process(target=file_descriptor_process)
    descriptor.start()


def create_folders(data_path):
    """Create essential folders for crawlers if they do not exists"""
    files = [
        f"{data_path}",
        f"{data_path}/config",
        f"{data_path}/data",
        f"{data_path}/flags",
        f"{data_path}/log",
        f"{data_path}/webdriver",
    ]
    for f in files:
        crawling_utils.check_file_path(f)


def get_crawler_base_settings(config):
    """Returns scrapy base configurations."""
    autothrottle = "antiblock_autothrottle_"
    return {
        "BOT_NAME": "crawlers",
        "ROBOTSTXT_OBEY": config['obey_robots'],
        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": {'scrapy_puppeteer.PuppeteerMiddleware': 800},
        "DOWNLOAD_DELAY": config["antiblock_download_delay"],
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": config[f"{autothrottle}enabled"],
        "AUTOTHROTTLE_START_DELAY": config[f"{autothrottle}start_delay"],
        "AUTOTHROTTLE_MAX_DELAY": config[f"{autothrottle}max_delay"],
    }


def crawler_process(config):
    """Starts crawling."""
    crawler_id = config["crawler_id"]
    instance_id = config["instance_id"]
    data_path = config["data_path"]

    # Redirects process logs to files
    sys.stdout = open(f"{data_path}/log/{instance_id}.out", "a", buffering=1)
    sys.stderr = open(f"{data_path}/log/{instance_id}.err", "a", buffering=1)

    process = CrawlerProcess(settings=get_crawler_base_settings(config))

    if config["crawler_type"] == "single_file":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "file_bundle":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "deep_crawler":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "static_page":
        process.crawl(StaticPageSpider, config=json.dumps(config))

    def update_database():
        # TODO: get port as variable
        port = 8000
        requests.get(
            f'http://localhost:{port}/detail/stop_crawl/{crawler_id}')

    for crawler in process.crawlers:
        crawler.signals.connect(
            update_database, signal=scrapy.signals.spider_closed)

    process.start()


def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))


def start_crawler(config):
    """Create and starts a crawler as a new process."""
    
    config["crawler_id"] = config["id"]
    del config["id"]
    config["instance_id"] = gen_key()

    data_path = config["data_path"]
    create_folders(data_path=data_path)

    with open(f"{data_path}/config/{config['instance_id']}.json", "w+") as f:
        f.write(json.dumps(config, indent=2))

    with open(f"{data_path}/flags/{config['instance_id']}.json", "w+") as f:
        f.write(json.dumps({"stop": False}))

    # starts new process
    p = Process(target=crawler_process, args=(config,))
    p.start()

    return config["instance_id"]


def stop_crawler(instance_id, config):
    """Sets the flags of a crawler to stop."""
    data_path = config["data_path"]
    with open(f"{data_path}/flags/{instance_id}.json", "w+") as f:
        f.write(json.dumps({"stop": True}))


def remove_crawler(instance_id, are_you_sure=False):
    """
    CAUTION: Delete ALL files and folders created by a crawler run.
    This includes all data stored under
    {CURR_FOLDER_FROM_ROOT}/data/.
    Save data before deleting.
    """

    if are_you_sure is False:
        msg = "ERROR: Delete ALL files and folders created by a crawler run." \
            f" This includes all data stored under {CURR_FOLDER_FROM_ROOT}/" \
            "data/. Save data before deleting. "
        raise Exception(msg)

    files = [
        f"{CURR_FOLDER_FROM_ROOT}/config/{instance_id}.json",
        f"{CURR_FOLDER_FROM_ROOT}/flags/{instance_id}.json",
        f"{CURR_FOLDER_FROM_ROOT}/log/{instance_id}.out",
        f"{CURR_FOLDER_FROM_ROOT}/log/{instance_id}.err",
    ]
    for f in files:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass

    folders = [
        f"{CURR_FOLDER_FROM_ROOT}/data/",
    ]
    for f in folders:
        try:
            shutil.rmtree(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
