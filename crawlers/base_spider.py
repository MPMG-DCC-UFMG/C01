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
import pandas
import time
from lxml.html.clean import Cleaner
import urllib.parse as urlparse
import mimetypes
import requests
import string

# Project libs
import crawling_utils

from binary import Extractor
from crawlers.constants import *
from crawlers.file_descriptor import FileDescriptor
from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
    HTTPStatusProbingResponse, TextMatchProbingResponse,\
    EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference
import parsing_html

PUNCTUATIONS = "[{}]".format(string.punctuation)


class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    request_session = requests.sessions.Session()

    def __init__(self, config, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """

        print("At BaseSpider.init")
        self.stop_flag = False

        self.config = json.loads(config)

        self.data_folder = f"{self.config['data_path']}/data/"
        self.flag_folder = f"{self.config['data_path']}/flags/"

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

        self.get_format = lambda i: str(i).split("/")[1][:-1].split(";")[0]


        if bool(self.config.get("download_files_allow_extensions")):
            normalized_allowed_extensions = self.config["download_files_allow_extensions"].replace(" ", "")
            normalized_allowed_extensions = normalized_allowed_extensions.lower()
            self.download_allowed_extensions = set(normalized_allowed_extensions.split(","))

        else:
            self.download_allowed_extensions = set()

        self.preprocess_link_configs()
        self.preprocess_download_configs()

    def start_requests(self):
        """
        Should be implemented by child class.
        Should yield the firsts urls to scrape.
        """
        raise NotImplementedError

    def parse(self, response):
        """
        A function to treat the responses from a request.
        Should check self.stop() at every call.
        """
        raise NotImplementedError

    def generate_initial_requests(self):
        """
        Generates the initial requests to be done from the templated requests
        configuration. Yields the base URL if no template is used. Should be
        called by start_requests.
        """

        base_url = self.config['base_url']
        req_type = self.config['request_type']

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
                self.config['templated_url_response_handlers']
            )

            # Instantiate the parameter injectors for the URL
            url_injectors = self.create_parameter_generators(probe,
                self.config['parameter_handlers']
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

                elif param_type == 'value_list':
                    # No filtering applied to this parameter
                    list_values = param['value_list_param']

                    param_gen = ParamInjector.generate_list(
                        elements=list_values
                    )
                elif param_type == 'const_value':
                    # No filtering applied to this parameter
                    const_value = param['value_const_param']

                    param_gen = ParamInjector.generate_constant(
                        value=const_value
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

    def stop(self):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """

        flag_file = f"{self.flag_folder}/{self.config['instance_id']}.json"

        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response, description):
        """Try to extract a json/csv from page html."""
        hsh = self.hash_response(response)

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if self.config["save_csv"]:
            output_filename += ".csv"

        success = False
        try:
            table_attrs = self.config["table_attrs"]
            if table_attrs is None or table_attrs == "":
                parsing_html.content.html_detect_content(
                    description["relative_path"],
                    is_string=False,
                    output_file=output_filename,
                    to_csv=self.config["save_csv"]
                )
            else:
                extra_config = self.extra_config_parser(
                    self.config["table_attrs"])
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
                    to_csv=self.config["save_csv"]
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
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        extracted_files = self.extract_and_store_csv(
            response, description.copy())
        description["extracted_files"] = extracted_files

        self.feed_file_description(
            self.data_folder + "raw_pages", description)

    # based on: https://github.com/steveeJ/python-wget/blob/master/wget.py
    def filetype_from_url(self, url: str) -> str:
        """Detects the file type through its URL"""
        extension = url.split('.')[-1]
        if 0 < len(extension) < 6:
            return extension
        return ""

    def filetype_from_filename_on_server(self, content_disposition: str) -> str:
        """Detects the file extension by its name on the server"""

        # content_disposition is a string with the following format: 'attachment; filename="filename.extension"'
        # the following operations are to extract only the extension
        extension = content_disposition.split(".")[-1]

        # removes any kind of accents
        return re.sub(PUNCTUATIONS, "", extension)

    def filetypes_from_mimetype(self, mimetype: str) -> str:
        """Detects the file type using its mimetype"""
        extensions = mimetypes.guess_all_extensions(mimetype)
        if len(extensions) > 0:
            return [ext.replace(".", "") for ext in extensions]
        return [""]

    def detect_file_extensions(self, url, content_type: str, content_disposition: str) -> list:
        """detects the file extension, using its mimetype, url or name on the server, if available"""
        extension = self.filetype_from_url(url)
        if len(extension) > 0:
            return [extension]

        extension = self.filetype_from_filename_on_server(content_disposition)
        if len(extension) > 0:
            return [extension]

        return self.filetypes_from_mimetype(content_type)

    def convert_binary(self, url: str, filetype: str, filename: str):
        if filetype != "pdf":
            return

        url_hash = crawling_utils.hash(url.encode())
        source_file = f"{self.data_folder}files/{filename}"

        success = False
        results = None
        try:
            # single DataFrame or list of DataFrames
            results = Extractor(source_file).extra().read()
        except Exception as e:
            print(
                f"Could not extract csv files from {source_file} -",
                f"message: {str(type(e))}-{e}"
            )
            return []

        if type(results) == pandas.DataFrame:
            results = [results]

        extracted_files = []
        for i in range(len(results)):
            relative_path = f"{self.data_folder}csv/{url_hash}_{i}.csv"
            results[i].to_csv(relative_path, encoding='utf-8', index=False)

            extracted_files.append(relative_path)

            item_desc = {
                "file_name": f"{url_hash}_{i}.csv",
                "type": "csv",
                "extracted_from": source_file,
                "relative_path": relative_path
            }

            FileDescriptor.feed_description(f"{self.data_folder}csv/", item_desc)

        return extracted_files

    def get_download_filename(self, url: str, extension: str) -> tuple:
        url_hash = crawling_utils.hash(url.encode())
        file_name = url_hash
        file_name += '.' + extension if extension else ''

        return file_name

    def store_large_file(self, url: str, referer: str):
        print(f"Saving large file {url}")

        # Head type request to obtain the mimetype and/or file name to be downloaded on the server
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
        response = requests.head(url, allow_redirects=True, headers=headers)

        content_type = response.headers.get("Content-type", "")
        content_disposition = response.headers.get("Content-Disposition", "")

        response.close()

        extension = self.detect_file_extensions(url, content_type, content_disposition)[0]

        file_name = self.get_download_filename(url, extension)
        relative_path = f"{self.data_folder}files/{file_name}"

        # The stream parameter is not to save in memory
        with requests.get(url, stream=True, allow_redirects=True, headers=headers) as req:
            with open(relative_path, "wb") as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)

        self.create_and_feed_file_description(url, file_name, referer, extension)

    def store_small_file(self, response):
        print(f"Saving small file {response.url}")

        content_type = response.headers.get("Content-Type", b"").decode()
        content_disposition = response.headers.get("Content-Disposition", b"").decode()

        extension = self.detect_file_extensions(response.url, content_type, content_disposition)[0]

        file_name = self.get_download_filename(response.url, extension)
        relative_path = f"{self.data_folder}files/{file_name}"

        with open(relative_path, "wb") as f:
            f.write(response.body)

        self.create_and_feed_file_description(response.url, file_name, response.meta["referer"], extension)

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

    def feed_file_description(self, destination: str, content: dict):
        FileDescriptor.feed_description(destination, content)

    def create_and_feed_file_description(self, url: str, file_name: str, referer: str, extension: str):
        """Creates the description file of the downloaded files and saves them"""

        description = {
            "url": url,
            "file_name": file_name,
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": referer,
            "type": extension,
        }

        extracted_files = self.convert_binary(url, extension, file_name)
        description["extracted_files"] = extracted_files

        self.feed_file_description(f"{self.data_folder}files/", description)

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

    def preprocess_listify(self, value, default):
        """Converts a string of ',' separaded values into a list."""
        if value is None or len(value) == 0:
            value = default

        elif type(value) == str:
            value = tuple(value.replace(" ", "").split(","))

        return value

    def preprocess_download_configs(self):
        """Process download_files configurations."""
        defaults = [
            ("download_files_tags", ('a', 'area')),
            ("download_files_allow_domains", None),
            ("download_files_attrs", ('href',))
        ]

        for attr, default in defaults:
            self.config[attr] = self.preprocess_listify(self.config[attr], default)

        deny = "download_files_deny_extensions"
        if len(self.download_allowed_extensions) > 0:
            extensions = [ext for ext in scrapy.linkextractors.IGNORED_EXTENSIONS]
            self.config[deny] = [ext for ext in extensions if ext not in self.download_allowed_extensions]
        
        else:
            self.config[deny] = []
        
        attr = "download_files_process_value"
        if self.config[attr] is not None and len(self.config[attr]) > 0 and type(self.config[attr]) is str:
            self.config[attr] = eval(self.config[attr])

    def preprocess_link_configs(self):
        """Process link_extractor configurations."""

        defaults = [
            ("link_extractor_tags", ('a', 'area')),
            ("link_extractor_allow_domains", None),
            ("link_extractor_attrs", ('href',))
        ]
        for attr, default in defaults:
            self.config[attr] = self.preprocess_listify(self.config[attr], default)
