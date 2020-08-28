import scrapy
from scrapy.exceptions import CloseSpider

import crawling_utils
import datetime
import json
import logging
import os
import parsing_html
import random
import re
import requests
import time

from crawlers.constants import *
from param_injector import ParamInjector
from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
                          HTTPStatusProbingResponse, TextMatchProbingResponse,\
                          EntryProbing

from lxml.html.clean import Cleaner
import codecs


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.stop_flag = False

        self.data_folder = f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}"

        cofig_file_path = f"{CURR_FOLDER_FROM_ROOT}/config/{crawler_id}.json"
        with open(cofig_file_path, "r") as f:
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
        templated_url_config = self.config['templated_url_config']

        has_placeholder = "{}" in base_url
        if has_placeholder:
            # Instantiate the parameter injector
            param_type = templated_url_config['template_parameter_type']
            param_gen = None
            if param_type == "formatted_str":
                # Formatted string generator
                #TODO
                pass
            elif param_type == "number_seq":
                # Number sequence generator
                param_gen = ParamInjector.generate_num_sequence(
                    first=templated_url_config['first_num_param'],
                    last=templated_url_config['last_num_param'],
                    step=templated_url_config['step_num_param'],
                    leading=templated_url_config['leading_num_param'],
                )
            elif param_type == 'date_seq':
                # Date sequence generator
                param_gen = ParamInjector.generate_daterange(
                    date_format=templated_url_config['date_format_date_param'],
                    start_date=templated_url_config['start_date_date_param'],
                    end_date=templated_url_config['end_date_date_param'],
                    frequency=templated_url_config['frequency_date_param'],
                )
            elif param_type == 'alpha_seq':
                # Alphabetic search parameter generator
                param_gen = ParamInjector.generate_alpha(
                    length=templated_url_config['length_alpha_param'],
                    num_words=templated_url_config['num_words_alpha_param'],
                    no_upper=templated_url_config['no_upper_alpha_param'],
                )
            else:
                raise ValueError(f"Invalid parameter type: {param_type}")

            # Request body (only used in POST requests)
            req_body = {}
            param_key = None
            if req_type == 'POST':
                if len(templated_url_config['post_dictionary']) > 0:
                    req_body = json.loads(templated_url_config['post_dictionary'])

                param_key = templated_url_config['post_key']

            # Configure the probing process

            # Probing request
            probe = EntryProbing(HTTPProbingRequest(base_url, method=req_type,
                                                    req_data=req_body))

            # Probing response
            for handler_data in templated_url_config['response_handlers']:
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

            # Generate the requests
            for param_value in param_gen:
                # Check if this entry hits a valid page
                if probe.check_entry([param_value]):
                    curr_url = base_url

                    # Insert parameter into URL
                    curr_url = base_url.format(param_value)
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
        flag_file = f"{CURR_FOLDER_FROM_ROOT}/flags/{self.crawler_id}.json"
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
        file_format = self.get_format(response.headers['Content-type'])
        hsh = crawling_utils.hash(response.url.encode() + response.body)

        success = False

        if b'text/html' in response.headers['Content-type']:
            try:
                parsing_html.content.html_detect_content(
                    f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                    is_string=False,
                    output_file=f"{self.data_folder}/csv/{hsh}",
                )
                success = True

            except Exception as e:
                print(
                    f"Could not extract csv from {response.url} -",
                    f"message: {str(type(e))}-{e}"
                )
        else:
            # TODO call binary_extractor
            pass

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
            file_format = self.get_format(
                response.headers['Content-type']
            )
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
            body = cleaner.clean_html(response.body.decode('utf-8-sig'))
            encoding = "utf-8-sig"

        # POST requests may access the same URL with different parameters, so
        # we hash the URL with the response body
        hsh = crawling_utils.hash(response.url.encode() + response.body)

        folder = f"{self.data_folder}/{save_at}"

        content = {
            "file_name": f"{hsh}.{file_format}",
            "url": response.url,
            "crawler_id": self.crawler_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        with open(f"{folder}/file_description.jsonl", "a+") as f:
            f.write(json.dumps(content) + '\n')

        with open(
            file=f"{folder}/{hsh}.{file_format}",
            mode=file_mode,
            encoding=encoding,
        ) as f:
            f.write(body)

        self.extract_and_store_csv(response, content)

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        self.store_raw(
            response, file_format="html", binary=False, save_at="raw_pages")
