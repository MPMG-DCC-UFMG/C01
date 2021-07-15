from datetime import datetime
import itertools
import json

import requests
import tldextract
import redis

from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest, HTTPStatusProbingResponse, TextMatchProbingResponse, EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference

import settings

def notify_server(instance_id: str, num_pages: int):
    server_notification_url = f'http://localhost:8000/download/pages/found/{instance_id}/{num_pages}'
    req = requests.get(server_notification_url)

    if req.status_code == 200:
        print('Successful server notified of new files')
    
    else:
        print('Error notifying server about new files found')

def format_request(url: str, crawler_id: str, instance_id: str) -> dict:
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

def create_probing_object(base_url, req_type, req_body, resp_handlers):
    """
    Loads the request data and response handlers supplied, and generates
    the respective EntryProbing instance
    """

    # Probing request
    probe = EntryProbing(HTTPProbingRequest(
        base_url, method=req_type, req_data=req_body))

    # Probing response
    for handler_data in resp_handlers:
        resp_handler = None

        handler_type = handler_data['handler_type']
        if handler_type == 'text':
            resp_handler = TextMatchProbingResponse(
                text_match=handler_data['text_match_value'], opposite=handler_data['opposite'])

        elif handler_type == 'http_status':
            resp_handler = HTTPStatusProbingResponse(
                status_code=handler_data['http_status'], opposite=handler_data['opposite'])

        elif handler_type == 'binary':
            resp_handler = BinaryFormatProbingResponse(
                opposite=handler_data['opposite'])

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

                param_gen = ParamInjector.generate_format(code_format=PROCESS_FORMAT, 
                                                            param_limits=subparam_list,
                                                            verif=ParamInjector.process_code_verification,
                                                            verif_index=1)

            elif param_type == "number_seq":
                begin = param['first_num_param']
                end = param['last_num_param']

                if i == 2:
                    # Filter the number range
                    end = RangeInference.filter_numeric_range(begin, end, probe, entries_list, cons_misses=cons_misses)

                param_gen = ParamInjector.generate_num_sequence(first=begin, last=end, step=param['step_num_param'], leading=param['leading_num_param'])

            elif param_type == 'date_seq':
                begin = datetime.date.fromisoformat(param['start_date_date_param'])
                end = datetime.date.fromisoformat(param['end_date_date_param'])

                frequency = param['frequency_date_param']
                date_format = param['date_format_date_param']

                if i == 2:
                    # Filter the date range
                    end = RangeInference.filter_daterange(begin, end, probe, frequency, date_format, entries_list, cons_misses=cons_misses)

                param_gen = ParamInjector.generate_daterange(date_format=date_format, start_date=begin, end_date=end, frequency=frequency)
            
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

def generate_templated_urls(base_url, crawler_id, instance_id, req_type, req_body, response_handlers, parameter_handlers):
    crawler_id = str(crawler_id) 
    instance_id = str(instance_id)
    
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

    except:
        raise Exception("Failed to connect to Redis")

    ex_res = extractor(base_url)
    key = "{sid}:{dom}.{suf}:queue".format(
        sid=crawler_id,
        dom=ex_res.domain,
        suf=ex_res.suffix)
    
    has_placeholder = "{}" in base_url
    if has_placeholder:
        probe = create_probing_object(base_url, req_type, req_body, response_handlers)
        
        # Instantiate the parameter injectors for the URL
        url_injectors = create_parameter_generators(probe, parameter_handlers)
        # Generate the requests
        param_generator = itertools.product(*url_injectors)

        for param_combination in param_generator:
            if probe.check_entry(param_combination):
                curr_url = base_url.format(*param_combination)
                req = format_request(curr_url, crawler_id, instance_id)
                val = json.dumps(req)
                redis_conn.zadd(key, {val: -req['priority']})

                notify_server(instance_id, 1)                
                print(f'\t\tSent request "{curr_url}" to redis...')

    else:
        req = format_request(base_url, crawler_id, instance_id)
        val = json.dumps(req)
        redis_conn.zadd(key, {val: -req['priority']})

        notify_server(instance_id, 1)                
        print(f'\t\tSent request "{base_url}" to redis...')

    print('\tDone')
    redis_conn.close()

def generate_requests(config: dict):
    generate_templated_urls(**config)