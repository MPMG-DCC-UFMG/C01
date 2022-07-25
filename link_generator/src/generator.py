from datetime import datetime
import itertools
import json

import tldextract
from redis import Redis

from crawling_utils import notify_new_page_found

import settings
from injector_tools import create_probing_object, create_parameter_generators

REDIS_CONN = Redis(host=settings.REDIS_HOST,
                   port=settings.REDIS_PORT,
                   db=settings.REDIS_DB,
                   password=settings.REDIS_PASSWORD,
                   decode_responses=True,
                   socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                   socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT)

try:
    REDIS_CONN.info()

except:
    raise Exception("Failed to connect to Redis")


def format_request(url: str, crawler_id: str, instance_id: str,
                   templated_param_combination: list) -> dict:
    """Formats a collection request according to Scrapy Cluster standards

    Args:
        - Config: Scraper configuration to be processed

    Returns:

        Returns a scraping request in the Scrapy Cluster pattern
    """

    return {
        "url": url,
        "appid": instance_id,
        "crawlid": crawler_id,
        "spiderid": crawler_id,
        "attrs": {
            "referer": "start_requests",
            "instance_id": instance_id,
            "templated_param_combination": templated_param_combination
        },
        "priority": 1,
        "maxdepth": 0,
        "domain_max_pages": None,
        "allowed_domains": None,
        "allow_regex": None,
        "deny_regex": None,
        "deny_extensions": None,
        "expires": 0,
        "useragent": None,
        "cookie": None,
        "ts": datetime.now().timestamp()
    }


def get_redis_queue_key(base_url: str, crawler_id: str) -> str:
    extractor = tldextract.TLDExtract()
    ex_res = extractor(base_url)
    key = "{sid}:{dom}.{suf}:queue".format(
        sid=crawler_id,
        dom=ex_res.domain,
        suf=ex_res.suffix)
    return key


def push_crawl_request_to_redis(redis_queue_key: str, url: str,
                                crawler_id: str, instance_id: str,
                                templated_param_combination:list):
    req = format_request(url, crawler_id, instance_id,
        templated_param_combination)
    val = json.dumps(req)
    REDIS_CONN.zadd(redis_queue_key, {val: -req['priority']})

    print(f'\t\tSent request "{url}" to redis...')
    notify_new_page_found(instance_id)


def generate_templated_urls(base_url, crawler_id, instance_id,
                            templated_url_response_handlers,
                            templated_url_parameter_handlers):

    crawler_id = str(crawler_id)
    instance_id = str(instance_id)

    redis_queue_key = get_redis_queue_key(base_url, crawler_id)

    has_placeholder = "{}" in base_url
    templated_url_generator = [[None]]
    templated_url_probe = create_probing_object(base_url, 'GET')

    if has_placeholder:
        templated_url_probe = create_probing_object(base_url, 'GET',
            templated_url_response_handlers)

        # Instantiate the parameter injectors for the URL
        url_injectors = create_parameter_generators(templated_url_probe,
            templated_url_parameter_handlers)

        # Generate the requests
        templated_url_generator = itertools.product(*url_injectors)

    for param_combination in templated_url_generator:
        if templated_url_probe.check_entry(url_entries=param_combination):
            # Insert parameters into URL and request body
            curr_url = base_url.format(*param_combination)
            push_crawl_request_to_redis(redis_queue_key, curr_url, crawler_id,
                instance_id, param_combination)

    print('\tDone')
    REDIS_CONN.close()


def generate_requests(config: dict):
    generate_templated_urls(**config)
