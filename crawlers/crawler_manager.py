# Scrapy and Twister libs
import scrapy
from scrapy.crawler import CrawlerProcess

# Other external libs
import json
import os
import random
import shutil
import sys
import time
import multiprocessing as mp
from multiprocessing import Process

# Project libs
import crawling_utils.crawling_utils as crawling_utils
from crawlers.constants import *
from crawlers.file_descriptor import FileDescriptor


def file_descriptor_process():
    """Redirects descriptor output and starts descriptor consumer loop."""
    crawling_utils.check_file_path("crawlers/log/")
    sys.stdout = open(f"crawlers/log/file_descriptor.out", "w+", buffering=1)
    sys.stderr = open(f"crawlers/log/file_descriptor.err", "w+", buffering=1)
    FileDescriptor.description_consumer()


def create_folders(data_path: dict):
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


def get_ip_rotation_settings(config: dict, settings: dict):
    """Updates the settings for ip rotation."""

    if config["antiblock_ip_rotation_enabled"]:
        # rotação de IPs via Tor
        if config["antiblock_ip_rotation_type"] == "tor":
            settings["DOWNLOADER_MIDDLEWARES"]["antiblock_scrapy.middlewares.TorProxyMiddleware"] = 900
            settings["DOWNLOADER_MIDDLEWARES"]["scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware"] = 910

            settings["TOR_IPROTATOR_CHANGE_AFTER"] = config["antiblock_max_reqs_per_ip"]
            settings["TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER"] = config["antiblock_max_reuse_rounds"]

            settings["TOR_IPROTATOR_ENABLED"] = True

        # rotação de IPs via lista de proxies
        else:
            settings["DOWNLOADER_MIDDLEWARES"]["rotating_proxies.middlewares.RotatingProxyMiddleware"] = 610
            settings["DOWNLOADER_MIDDLEWARES"]["rotating_proxies.middlewares.BanDetectionMiddleware"] = 620

            config["antiblock_proxy_list"] = config["antiblock_proxy_list"].split('\r\n')

            settings["ROTATING_PROXY_LIST"] = config["antiblock_proxy_list"]


def get_user_agent_rotation_settings(config: dict, settings: dict):
    """Updates the settings for user-agent rotation."""

    if config["antiblock_user_agent_rotation_enabled"]:
        settings["DOWNLOADER_MIDDLEWARES"]["scrapy.downloadermiddlewares.useragent.UserAgentMiddleware"] = None
        settings["DOWNLOADER_MIDDLEWARES"]["antiblock_scrapy.middlewares.RotateUserAgentMiddleware"] = 500

        settings["USER_AGENTS"] = config["antiblock_user_agents_list"].split('\r\n')

        settings["MIN_USER_AGENT_USAGE"] = max(1, int(config["antiblock_reqs_per_user_agent"] * .5))
        settings["MAX_USER_AGENT_USAGE"] = int(config["antiblock_reqs_per_user_agent"] * 1.5)

        settings["ROTATE_USER_AGENT_ENABLED"] = True


def get_insert_cookies_settings(config: dict, settings: dict):
    """Updates the settings for inserting cookies."""

    if config["antiblock_insert_cookies_enabled"]:
        cookies = [json.loads(cookie) for cookie in config["antiblock_cookies_list"].split('\r\n')]
        config["antiblock_cookies_list"] = cookies

    else:
        config["antiblock_cookies_list"] = None


def get_autothrottle_settings(config: dict, settings: dict):
    """Updates the settings to AUTOTHROTTLE."""

    settings["AUTOTHROTTLE_ENABLED"] = config["antiblock_autothrottle_enabled"]
    settings["AUTOTHROTTLE_START_DELAY"] = config["antiblock_autothrottle_start_delay"]
    settings["AUTOTHROTTLE_MAX_DELAY"] = config["antiblock_autothrottle_max_delay"]


def get_dynamic_processing_settings(config: dict, settings: dict):

    if config.get("dynamic_processing", False):
        settings["DOWNLOADER_MIDDLEWARES"]["scrapy_puppeteer.PuppeteerMiddleware"] = 800
        settings["DATA_PATH"] = config["data_path"]
        settings["CRAWLER_ID"] = config["crawler_id"]
        settings["INSTANCE_ID"] = config["instance_id"]
        settings["SKIP_ITER_ERRORS"] = config["skip_iter_errors"]


def get_crawler_base_settings(config: dict):
    """Returns scrapy base configurations."""

    settings = {
        "CRAWLER_ID": config["crawler_id"],
        "BOT_NAME": "crawlers",
        "DOWNLOADER_MIDDLEWARES": {},
        "ROBOTSTXT_OBEY": config["obey_robots"],
        "DOWNLOAD_DELAY": config["antiblock_download_delay"],
        "DEPTH_LIMIT": config["link_extractor_max_depth"],
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "LOG_LEVEL": "DEBUG"
    }

    get_dynamic_processing_settings(config, settings)
    get_ip_rotation_settings(config, settings)
    get_user_agent_rotation_settings(config, settings)
    get_insert_cookies_settings(config, settings)
    get_autothrottle_settings(config, settings)

    if len(settings["DOWNLOADER_MIDDLEWARES"]) == 0:
        del settings["DOWNLOADER_MIDDLEWARES"]

    return settings


def crawler_process(config):
    """Starts crawling."""
    import scrapy_puppeteer
    from crawlers.page_spider import PageSpider

    crawler_id = config["crawler_id"]
    instance_id = config["instance_id"]
    data_path = config["data_path"]

    # Redirects process logs to files
    sys.stdout = open(f"{data_path}/log/{instance_id}.out", "a", buffering=1)
    sys.stderr = open(f"{data_path}/log/{instance_id}.err", "a", buffering=1)

    process = CrawlerProcess(settings=get_crawler_base_settings(config))
    process.crawl(PageSpider, config=json.dumps(config))
    process.start()


def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))


def start_crawler(config: dict):
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
    p = Process(name='Crawler-' + str(config['crawler_id']), target=crawler_process, args=(config,))
    p.start()

    return config["instance_id"]


def stop_crawler(crawler_id: str, instance_id: str, config: dict):
    """Sets the flags of a crawler to stop."""

    data_path = config["data_path"]
    with open(f"{data_path}/flags/{instance_id}.json", "w+") as f:
        f.write(json.dumps({"stop": True}))

    # iterate over the running processes and explicitly terminate it
    for p in mp.active_children():
        if p.name == 'Crawler-' + str(crawler_id):
            p.terminate()


def remove_crawler(instance_id: str, are_you_sure: bool = False):
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


def update_instances_info(data_path: str, instance_id: str, instance: dict):
    """Updates the file with information about instances when they are created, initialized or terminated."""

    instances = dict()

    filename = f"{data_path}/instances.json"
    if os.path.exists(filename):
        with open(filename) as f:
            instances = json.loads(f.read())

    instances[instance_id] = instance
    with open(filename, "w+") as f:
        f.write(json.dumps(instances, indent=4))
