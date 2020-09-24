import scrapy
from scrapy.exceptions import CloseSpider

import requests
import logging
import os
import re
import json
import random
import datetime
import time
import crawling_utils

from crawlers.constants import *
import parsing_html
import binary

from lxml.html.clean import Cleaner
import codecs

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, instance_id, output_path, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """

        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.instance_id = instance_id
        self.stop_flag = False

        self.data_folder = f"{output_path}/data/{instance_id}"
        config_file_path = f"{output_path}/config/{instance_id}.json"
        self.flag_folder = f"{output_path}/flags/"

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

        file_format = self.get_format(response.headers['Content-type'])
        hsh = crawling_utils.hash(response.url)

        success = False

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if self.config["save_csv"] and ".csv" not in output_filename:
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
                    extra_config = json.loads(self.config["table_attrs"]) 
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
                    parsing_html.content.html_detect_content(
                        f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                        is_string=False, output_file=output_filename,
                        match=extra_config['table_match'], flavor=extra_config['table_flavor'],
                        header=extra_config['table_header'], index_col=extra_config['table_index_col'],
                        skiprows=extra_config['table_skiprows'], attrs=extra_config['table_attributes'],
                        parse_dates=extra_config['table_parse_dates'], thousands=extra_config['table_thousands'],
                        encoding=extra_config['table_encoding'], decimal=extra_config['table_decimal'],
                        na_values=extra_config['table_na_values'], keep_default_na=extra_config['table_default_na'],
                        displayed_only=extra_config['table_displayed_only'],to_csv=self.config["save_csv"]
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

        hsh = crawling_utils.hash(response.url)

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
