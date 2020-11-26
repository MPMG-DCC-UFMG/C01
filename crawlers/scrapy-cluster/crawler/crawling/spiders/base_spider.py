# Scrapy and Twister libs
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

# Other external libs
import datetime
import json
import itertools
import logging
import os
import re
import time
from lxml.html.clean import Cleaner

# Project libs
import binary
import crawling_utils
from crawling.spiders.constants import *
from file_descriptor.file_descriptor import FileDescriptor
from file_downloader.file_downloader import FileDownloader
from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
    HTTPStatusProbingResponse, TextMatchProbingResponse,\
    EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference
import parsing_html

class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, *args, **kwargs):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        super(BaseSpider, self).__init__(*args, **kwargs)

        print("At BaseSpider.init")
        
        self.stop_flag = False
        self.data_folder = ""
        self.flag_folder = ""
        self.get_format = lambda i: str(i).split("/")[1][:-1].split(";")[0]

    def setup_folders(self, config):
        data_path = config['data_path']
        
        self.data_folder = f"{data_path}/data"
        self.flag_folder = f"{data_path}/flags"
        
        folders = [
            f"{self.data_folder}",
            f"{self.data_folder}/raw_pages",
            f"{self.data_folder}/csv",
            f"{self.data_folder}/files",
        ]
        
        for f in folders:
            try:
                os.mkdir(f)
            except FileExistsError:
                pass

        file = "file_description.jsonl"
        with open(f"{self.data_folder}/files/{file}", "a+") as f:
            pass
        with open(f"{self.data_folder}/raw_pages/{file}", "a+") as f:
            pass

    # def start_requests(self):
    #     """
    #     Should be implemented by child class.
    #     Should yield the firsts urls to scrape.
    #     """
    #     raise NotImplementedError

    def parse(self, response):
        """
        A function to treat the responses from a request.
        Should check self.stop() at every call.
        """
        raise NotImplementedError

    def generate_initial_requests(self, config):
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
            probe = self.create_probing_object(base_url, req_type, req_body,
                config['templated_url_response_handlers']
            )

            # Instantiate the parameter injectors for the URL
            url_injectors = self.create_parameter_generators(probe,
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
                        'method': req_type,
                        'body': req_body
                    }

        else:
            # By default does a request to the base_url
            yield {
                'url': base_url,
                'method': req_type,
                'body': {}
            }

    def create_probing_object(self, base_url, req_type, req_body,
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

    def create_parameter_generators(self, probe, parameter_handlers):
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


    def stop(self, config):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """

        self.setup_folders(config)

        flag_file = f"{self.flag_folder}/{config['instance_id']}.json"

        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response, description):
        """Try to extract a json/csv from page html."""

        config = response.meta['attrs']

        self.setup_folders(config)

        hsh = self.hash_response(response)

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if config["save_csv"]:
            output_filename += ".csv"

        success = False
        try:
            table_attrs = config["table_attrs"]
            if table_attrs is None or table_attrs == "":
                parsing_html.content.html_detect_content(
                    description["relative_path"],
                    is_string=False,
                    output_file=output_filename,
                    to_csv=config["save_csv"]
                )
            else:
                extra_config = self.extra_config_parser(
                    config["table_attrs"])
                parsing_html.content.html_detect_content(
                    description["relative_path"],
                    is_string=False, output_file=output_filename,
                    match=extra_config['table_match'],
                    flavor=extra_config['table_flavor'],
                    header=extra_config['table_header'],
                    index_col=extra_config['table_index_col'],
                    skiprows=extra_config['table_skiprows'],
                    attrs=extra_config['table_attributes'],
                    parse_dates=extra_config['table_parse_dates'],
                    thousands=extra_config['table_thousands'],
                    encoding=extra_config['table_encoding'],
                    decimal=extra_config['table_decimal'],
                    na_values=extra_config['table_na_values'],
                    keep_default_na=extra_config['table_default_na'],
                    displayed_only=extra_config['table_displayed_only'],
                    to_csv=config["save_csv"]
                )
            success = True

        except Exception as e:
            print(
                f"Could not extract csv from {response.url} -",
                f"message: {str(type(e))}-{e}"
            )

        if success:
            description["extracted_from"] = description["relative_path"]
            description["relative_path"] = output_filename
            description["type"] = "csv"
            self.feed_file_description(f"{self.data_folder}csv/", description)
            return [output_filename]

        return []

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        print(f'Saving html page {response.url}')
        
        config = response.meta['attrs']

        self.setup_folders(config)

        cleaner = Cleaner(
            style=True, links=False, scripts=True,
            comments=True, page_structure=False
        )
        body = cleaner.clean_html(
            response.body.decode('utf-8', errors='ignore'))

        hsh = self.hash_response(response)

        relative_path = f"{self.data_folder}raw_pages/{hsh}.html"

        with open(file=relative_path, mode="w+", errors='ignore') as f:
            f.write(body)

        description = {
            "file_name": f"{hsh}.html",
            "relative_path": relative_path,
            "url": response.url,
            "crawler_id": config["crawler_id"],
            "instance_id": config["instance_id"],
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["url"]
        }

        extracted_files = self.extract_and_store_csv(
            response, description.copy())
        description["extracted_files"] = extracted_files

        self.feed_file_description(
            self.data_folder + "raw_pages", description)

    def errback_httpbin(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def feed_file_downloader(self, url, response_origin, config):
        wait_end = config["wait_crawler_finish_to_download"]
        description = {
            "url": url,
            "crawler_id": config["crawler_id"],
            "instance_id": config["instance_id"],
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response_origin.url,
            "wait_crawler_finish_to_download": wait_end,
            "time_between_downloads": config["time_between_downloads"],
        }
        FileDownloader.feed_downloader(url, self.data_folder, description)

    def feed_file_description(self, destination, content):
        FileDescriptor.feed_description(destination, content)

    def extra_config_parser(self, table_attrs):
        # get the json from extra_config and 
        # formats in a python proper standard
        extra_config = json.loads(table_attrs)
        for key in extra_config:
            if extra_config[key] == "":
                extra_config[key] = None
        if extra_config['table_match'] is None:
            extra_config['table_match'] = '.+'
        if extra_config['parse_dates'] is None:
            extra_config['parse_dates'] = False
        if extra_config['keep_default_na'] is None:
            extra_config['keep_default_na'] = True
        if extra_config['displayed_only'] is None:
            extra_config['displayed_only'] = True
        if extra_config['table_thousands'] is None:
            extra_config['table_thousands'] = '.'
        if extra_config['table_decimal'] is None:
            extra_config['table_decimal'] = ', '

        return extra_config

    def hash_response(self, response):
        """
        Turns a response into a hashed value to be used as a file name

        :param response: response obtained from crawling

        :returns: hash of the response's URL and body
        """

        # POST requests may access the same URL with different parameters, so
        # we hash the URL with the response body
        return crawling_utils.hash(response.url.encode() + response.body)
