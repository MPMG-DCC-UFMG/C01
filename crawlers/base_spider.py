# Scrapy and Twister libs
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

# Other external libs
import datetime
import json
import logging
import os
import re
import time
from lxml.html.clean import Cleaner

# Project libs
import crawling_utils
from crawlers.file_descriptor import FileDescriptor
from crawlers.file_downloader import FileDownloader
import parsing_html
import binary
from crawlers.constants import *


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, config, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        config = json.loads(config)

        print("At BaseSpider.init")
        self.stop_flag = False

        self.data_folder = f"{config['data_path']}/data/"
        self.flag_folder = f"{config['data_path']}/flags/"

        self.config = config

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

        flag_file = f"{self.flag_folder}/{self.config['instance_id']}.json"

        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response, description):
        """Try to extract a json/csv from page html."""
        hsh = crawling_utils.hash(response.url)

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if self.config["save_csv"] and ".csv" not in output_filename:
            output_filename += ".csv"

        success = False
        try:
            parsing_html.content.html_detect_content(
                f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                is_string=False,
                output_file=output_filename,
                to_csv=self.config["save_csv"]
            )
            success = True

        except Exception as e:
            print(
                f"Could not extract csv from {response.url} -",
                f"message: {str(type(e))}-{e}"
            )

        description["type"] = "csv"
        if success:
            self.feed_file_description(f"{self.data_folder}/csv/", description)

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        print(f'Saving html page {response.url}')
        
        cleaner = Cleaner(
            style=True, links=False, scripts=True,
            comments=True, page_structure=False
        )
        body = cleaner.clean_html(
            response.body.decode('utf-8', errors='ignore'))

        hsh = crawling_utils.hash(response.url)

        with open(
            file=f"{self.data_folder}/raw_pages/{hsh}.html",
            mode="w+", errors='ignore'
        ) as f:
            f.write(body)      

        description = {
            "file_name": f"{hsh}.html",
            "url": response.url,
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        self.feed_file_description(self.data_folder + "/raw_pages", description)

        self.extract_and_store_csv(response, description)
        
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

    def feed_file_downloader(self, url, response_origin):
        description = {
            "url": url,
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response_origin.url
        }
        FileDownloader.feed_downloader(url, self.data_folder, description)

    def feed_file_description(self, destination, content):
        FileDescriptor.feed_description(destination, content)
