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
import itertools

# Project libs
import crawling_utils.crawling_utils as crawling_utils
from crawlers.constants import *
from file_descriptor.file_descriptor import FileDescriptor
from file_downloader.file_downloader import FileDownloader
from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
    HTTPStatusProbingResponse, TextMatchProbingResponse,\
    EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference

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
    sys.stdout = open(f"crawlers/log/file_downloader.out", "w+", buffering=1)
    sys.stderr = open(f"crawlers/log/file_downloader.err", "w+", buffering=1)
    FileDownloader.download_consumer()


def file_descriptor_process():
    """Redirects descriptor output and starts descriptor consumer loop."""
    crawling_utils.check_file_path("crawlers/log/")
    sys.stdout = open(f"crawlers/log/file_descriptor.out", "w+", buffering=1)
    sys.stderr = open(f"crawlers/log/file_descriptor.err", "w+", buffering=1)
    FileDescriptor.description_consumer()


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
        data = {
            "url": config['base_url'],
            "appid": config['instance_id'],
            "crawlid": str(config['crawler_id']),
            "spiderid": config['crawler_type'],
            "attrs": config
        }

    def update_database():
        # TODO: get port as variable
        port = 8000
        requests.get(
            f'http://localhost:{port}/detail/stop_crawl/{crawler_id}')

    for crawler in process.crawlers:
        crawler.signals.connect(
            update_database, signal=scrapy.signals.spider_closed)

    url = 'http://0.0.0.0:5343/feed'
    headers = {'content-type': 'application/json'}

    if config['parameter_handlers']:
        print('\nGenerating Initial Requests...\n')
        for ini_req in generate_initial_requests(config):
            print('Feeding API with ' + ini_req['url'])
            req = requests.post(url, data=json.dumps(ini_req), headers=headers)
            print(req.json())
    else:
        print('\nFeeding API\n')
        req = requests.post(url, data=json.dumps(data), headers=headers)
        print(req.json())


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

def generate_initial_requests(config):
    """
    Generates the initial requests to be done from the templated requests
    configuration. Yields the base URL if no template is used. Should be
    called by start_requests.
    """

    base_url = config['base_url']
    req_type = config['request_type']

    has_placeholder = "{}" in base_url
    if has_placeholder:
        # Request body (TODO)
        req_body = {}
        """
        param_key = None
        if req_type == 'POST':
            if len(templated_url_config['post_dictionary']) > 0:
                req_body = json.loads(
                    templated_url_config['post_dictionary']
                )

            param_key = templated_url_config['post_key']"""

        # Configure the probing process
        probe = create_probing_object(base_url, req_type, req_body,
            config['templated_url_response_handlers']
        )

        # Instantiate the parameter injectors for the URL
        url_injectors = create_parameter_generators(probe,
            config['parameter_handlers']
        )

        # Generate the requests
        param_generator = itertools.product(*url_injectors)
        for param_combination in param_generator:
            # Check if this entry hits a valid page
            if probe.check_entry(param_combination):
                curr_url = base_url

                # Insert parameter into URL
                curr_url = base_url.format(*param_combination)
                req_body = {}

                yield {
                    'url': curr_url,
                    # 'method': req_type,
                    # 'body': req_body,
                    "appid": config['instance_id'],
                    "crawlid": str(config['crawler_id']),
                    "spiderid": config['crawler_type'],
                    "attrs": config
                }

    else:
        # By default does a request to the base_url
        yield {
            'url': base_url,
            # 'method': req_type,
            # 'body': {},
            "appid": config['instance_id'],
            "crawlid": str(config['crawler_id']),
            "spiderid": config['crawler_type'],
            "attrs": config
        }

def create_probing_object(base_url, req_type, req_body,
                            resp_handlers):
    """
    Loads the request data and response handlers supplied, and generates
    the respective EntryProbing instance
    """

    # Probing request
    probe = EntryProbing(HTTPProbingRequest(base_url, method=req_type,
                                            req_data=req_body))

    # Probing response
    for handler_data in resp_handlers:
        resp_handler = None

        handler_type = handler_data['handler_type']
        if handler_type == 'text':
            resp_handler = TextMatchProbingResponse(
                text_match=handler_data['text_match_value'],
                opposite=handler_data['opposite']
            )
        elif handler_type == 'http_status':
            resp_handler = HTTPStatusProbingResponse(
                status_code=handler_data['http_status'],
                opposite=handler_data['opposite']
            )
        elif handler_type == 'binary':
            resp_handler = BinaryFormatProbingResponse(
                opposite=handler_data['opposite']
            )
        else:
            raise AssertionError

        probe.add_response_handler(resp_handler)

    return probe

def create_parameter_generators(probe, parameter_handlers):
    """
    Loads the parameter information and creates a list of the respective
    generators from the ParamInjector module, while filtering the ranges as
    necessary
    """

    url_injectors = []
    initial_values = []

    for i in [1, 2]:
        # We run this code twice: the first pass will get the initial
        # values for each parameter, which is used in the second pass to
        # filter the ends of the limits as required
        # I couldn't find a nicer way to do this

        for param_index, param in enumerate(parameter_handlers):
            param_type = param['parameter_type']
            param_gen = None

            if i == 2 and not param['filter_range']:
                # We are running the "filtering" pass but this parameter
                # should not be filtered
                continue

            entries_list = []
            cons_misses = None
            if i == 2:
                # Configure the list of extra parameters for the range
                # inference
                entries_list = initial_values.copy()
                entries_list[param_index] = None
                cons_misses = int(param['cons_misses'])

            if param_type == "process_code":
                PROCESS_FORMAT = '{:07d}-{:02d}.{:04d}.{}.{:02d}.{:04d}'

                first_year = int(param['first_year_proc_param'])
                last_year = int(param['last_year_proc_param'])
                segment_ids = param['segment_ids_proc_param'].split(",")
                court_ids = param['court_ids_proc_param'].split(",")
                origin_ids = param['origin_ids_proc_param'].split(",")

                # turn string lists into integers
                segment_ids = list(map(int, segment_ids))
                court_ids = list(map(int, court_ids))
                origin_ids = list(map(int, origin_ids))

                max_seq = 9999999
                if i == 2:
                    # Filter the process_code range
                    max_seq = RangeInference.filter_process_code(
                        first_year, last_year, segment_ids, court_ids,
                        origin_ids, probe, entries_list,
                        cons_misses=cons_misses
                    )

                subparam_list = [
                    # sequential identifier
                    (0, max_seq),
                    # year
                    (first_year, last_year),
                    # segment identifiers
                    segment_ids,
                    # court identifiers
                    court_ids,
                    # origin identifiers
                    origin_ids
                ]

                param_gen = ParamInjector.generate_format(
                    code_format=PROCESS_FORMAT,
                    param_limits=subparam_list,
                    verif=ParamInjector.process_code_verification,
                    verif_index=1
                )

            elif param_type == "number_seq":
                begin = param['first_num_param']
                end = param['last_num_param']

                if i == 2:
                    # Filter the number range
                    end = RangeInference.filter_numeric_range(begin, end,
                                probe, entries_list, cons_misses=cons_misses)

                param_gen = ParamInjector.generate_num_sequence(
                    first=begin,
                    last=end,
                    step=param['step_num_param'],
                    leading=param['leading_num_param'],
                )
            elif param_type == 'date_seq':
                begin = datetime.date.fromisoformat(
                    param['start_date_date_param']
                )
                end = datetime.date.fromisoformat(
                    param['end_date_date_param']
                )
                frequency = param['frequency_date_param']
                date_format = param['date_format_date_param']

                if i == 2:
                    # Filter the date range
                    end = RangeInference.filter_daterange(begin, end,
                                probe, frequency, date_format, entries_list,
                                cons_misses=cons_misses)

                param_gen = ParamInjector.generate_daterange(
                    date_format=date_format,
                    start_date=begin,
                    end_date=end,
                    frequency=frequency,
                )
            else:
                raise ValueError(f"Invalid parameter type: {param_type}")

            if i == 2 and param_gen is not None:
                # We have filtered the range for this parameter, and should
                # update the generator in the list
                url_injectors[param_index] = param_gen
            else:
                # Create a copy of the generator, to extract the first
                # value. After that, add to the list of parameter
                # generators
                param_gen, param_gen_first = itertools.tee(param_gen)
                initial_values.append(next(param_gen_first))
                url_injectors.append(param_gen)

    return url_injectors