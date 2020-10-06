import scrapy
from scrapy.exceptions import CloseSpider

import crawling_utils
import datetime
import itertools
import json
import logging
import os
import random
import re
import requests
import time

from crawlers.constants import *
from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
                          HTTPStatusProbingResponse, TextMatchProbingResponse,\
                          EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference
import parsing_html
import binary

from lxml.html.clean import Cleaner
import codecs

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, instance_id, data_path, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """

        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.instance_id = instance_id
        self.stop_flag = False

        self.data_folder = f"{data_path}/data/"
        config_file_path = f"{data_path}/config/{instance_id}.json"
        self.flag_folder = f"{data_path}/flags/"

        with open(config_file_path, "r") as f:
            self.config = json.loads(f.read())

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
                    req_body = json.loads(templated_url_config['post_dictionary'])

                param_key = templated_url_config['post_key']"""

            # Configure the probing process

            # Probing request
            probe = EntryProbing(HTTPProbingRequest(base_url, method=req_type,
                                                    req_data=req_body))

            # Probing response
            for handler_data in self.config['templated_url_response_handlers']:
                resp_handler = None

                handler_type = handler_data['handler_type']
                if handler_type == 'text':
                    resp_handler = TextMatchProbingResponse(
                        text_match=handler_data['text_match_value'],
                        opposite = handler_data['opposite']
                    )
                elif handler_type == 'http_status':
                    resp_handler = HTTPStatusProbingResponse(
                        status_code=handler_data['http_status'],
                        opposite = handler_data['opposite']
                    )
                elif handler_type == 'binary':
                    resp_handler = BinaryFormatProbingResponse(
                        opposite = handler_data['opposite']
                    )
                else:
                    raise AssertionError

                probe.add_response_handler(resp_handler)

            # Instantiate the parameter injectors for the URL
            url_injectors = []
            for param in self.config['parameter_handlers']:
                param_type = param['parameter_type']
                param_gen = None
                if param_type == "formatted_str":
                    # Formatted string generator
                    #TODO
                    pass
                elif param_type == "number_seq":
                    # Number sequence generator
                    param_gen = ParamInjector.generate_num_sequence(
                        first=param['first_num_param'],
                        last=param['last_num_param'],
                        step=param['step_num_param'],
                        leading=param['leading_num_param'],
                    )
                elif param_type == 'date_seq':
                    # Date sequence generator
                    begin = datetime.date.fromisoformat(
                        param['start_date_date_param']
                    )
                    end = datetime.date.fromisoformat(
                        param['end_date_date_param']
                    )

                    param_gen = ParamInjector.generate_daterange(
                        date_format=param['date_format_date_param'],
                        start_date=begin,
                        end_date=end,
                        frequency=param['frequency_date_param'],
                    )
                elif param_type == 'alpha_seq':
                    # Alphabetic search parameter generator
                    param_gen = ParamInjector.generate_alpha(
                        length=param['length_alpha_param'],
                        num_words=param['num_words_alpha_param'],
                        no_upper=param['no_upper_alpha_param'],
                    )
                else:
                    raise ValueError(f"Invalid parameter type: {param_type}")

                url_injectors.append(param_gen)

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


    def stop(self):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """

        flag_file = f"{self.flag_folder}/{self.instance_id}.json"

        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response, content):
        """
        Try to extract a json/csv from response data.
        """

        config = response.meta['config']

        file_format = self.get_format(response.headers['Content-type'])
        hsh = self.hash_response(response)

        success = False

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if config["save_csv"] and ".csv" not in output_filename:
            output_filename += ".csv"

        if b'text/html' in response.headers['Content-type']:
            try:
                if self.config["table_attrs"] is None:
                    parsing_html.content.html_detect_content(
                        f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                        is_string=False,
                        output_file=output_filename,
                        to_csv=self.config["save_csv"]
                    )
                else:
                    extra_config = extra_config_parser(self.config["table_attrs"])
                    parsing_html.content.html_detect_content(
                        f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                        is_string=False, output_file=output_filename,
                        match=extra_config['table_match'], flavor=extra_config['table_flavor'],
                        header=extra_config['table_header'], index_col=extra_config['table_index_col'],
                        skiprows=extra_config['table_skiprows'], attrs=extra_config['table_attributes'],
                        parse_dates=extra_config['table_parse_dates'], thousands=extra_config['table_thousands'],
                        encoding=extra_config['table_encoding'], decimal=extra_config['table_decimal'],
                        na_values=extra_config['table_na_values'], keep_default_na=extra_config['table_default_na'],
                        displayed_only=extra_config['table_displayed_only'], to_csv=self.config["save_csv"]
                    )

                success = True

            except Exception as e:
                print(
                    f"Could not extract csv from {response.url} -",
                    f"message: {str(type(e))}-{e}"
                )
        else:
            new_file = f"{self.data_folder}/files/{hsh}.{file_format}"

            try:
                out = binary.extractor.Extractor(new_file)
                out.extractor()
                success = True

            except Exception as e:
                print(
                    f"Could not extract csv files from {hsh}.{file_format} -",
                    f"message: {str(type(e))}-{e}"
                )

        content["type"] = "csv"
        file_description_file = f"{self.data_folder}/csv/" \
            "file_description.jsonl"

        if success:
            with open(file_description_file, "a+") as f:
                f.write(json.dumps(content) + '\n')


    def store_raw(
            self, response, file_format=None, binary=True, save_at="files"):
        """Save response content."""

        if file_format is None:
            file_format = self.get_format(response.headers['Content-type'])

        print(f'Saving file from {response.url}, file_format: {file_format}')

        if binary:
            file_mode = "wb"
            body = response.body
            encoding = None
        else:
            cleaner = Cleaner(
                style=True, links=False, scripts=True,
                comments=True, page_structure=False
            )

            file_mode = "w+"
            body = cleaner.clean_html(
                response.body.decode('utf-8', errors='ignore'))

        hsh = self.hash_response(response)

        folder = f"{self.data_folder}/{save_at}"

        content = {
            "file_name": f"{hsh}.{file_format}",
            "url": response.url,
            "crawler_id": self.crawler_id,
            "instance_id": self.instance_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        with open(f"{folder}/file_description.jsonl", "a+") as f:
            f.write(json.dumps(content) + '\n')

        with open(
            file=f"{folder}/{hsh}.{file_format}",
            mode=file_mode,
        ) as f:
            f.write(body)

        self.extract_and_store_csv(response, content)

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        self.store_raw(
            response, file_format="html", binary=False, save_at="raw_pages")

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
