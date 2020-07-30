import scrapy
from scrapy.exceptions import CloseSpider

import requests
import logging
import os
import re
import json
import random
import datetime
import hashlib
import time

from crawlers.constants import *
from src.parsing.html.parsing_html_content import *


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        print("TO NO INIT DO BASE SPIDER")
        self.crawler_id = crawler_id
        self.last_flag_check = int(time.time())
        self.stop_flag = False

        with open(f"{CURR_FOLDER_FROM_ROOT}/config/{crawler_id}.json", "r") as f:
            self.config = json.loads(f.read())

        folders = [
            f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}",
            f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}/raw_pages",
            f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}/csv",
            f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}/files",
        ]
        for f in folders:
            try:
                os.mkdir(f)
            except FileExistsError:
                pass

        with open(f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}/files/file_description.txt", "a+") as f:
            pass

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
        It does so in intervals of at least 5 seconds, to avoid much disk reading.
        Should be called at the begining of every parse operation.
        """
        now = int(time.time())
        if now - self.last_flag_check < 5:
            return self.stop_flag

        self.last_flag_check = now
        with open(f"{CURR_FOLDER_FROM_ROOT}/flags/{self.crawler_id}.json") as f:
            flags = json.loads(f.read())
        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def hash(self, string):
        """Returns the md5 hash of a function."""
        return hashlib.md5(string.encode()).hexdigest()

    def store_raw(self, response):
        """Store file, TODO convert to csv?"""
        assert response.headers['Content-type'] != b'text/html'

        file_format = str(response.headers['Content-type']).split("/")[1][:-1].split(";")[0]
        print('file_format: ', file_format)
        hsh = self.hash(response.url)
        content = {
            "hash": hsh,
            "url": response.url,
            "crawler_id": self.crawler_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
        }

        with open(f"{CURR_FOLDER_FROM_ROOT}/data/{self.crawler_id}/files/{hsh}.{file_format}", "wb") as f:
            f.write(response.body)

        with open(f"{CURR_FOLDER_FROM_ROOT}/data/{self.crawler_id}/files/file_description.txt", "a+") as f:
            f.write(json.dumps(content) + '\n')

    def extract_and_store_csv(self, response):
        """
        Try to extract a csv from response data.
        TODO Chama metodo do Caio
        """
        file_format = str(response.headers['Content-type']).split("/")[1][:-1].split(";")[0]
        hsh = self.hash(response.url)

        html_detect_content(f"{CURR_FOLDER_FROM_ROOT}/data/{self.crawler_id}/files/{hsh}.{file_format}",
                            is_string=False, output_file=f"{CURR_FOLDER_FROM_ROOT}/data/{self.crawler_id}/csv/output",)

    def store_html(self, response):
        """Stores raw html in a json file at data/{self.crawler_id}/raw_pages/."""
        assert response.headers['Content-type'] == b'text/html'

        content = {
            "url": response.url,
            "crawler_id": self.crawler_id,
            "crawled_at_date": str(datetime.datetime.today()),
            "html": str(response.body),
        }

        with open(f"{CURR_FOLDER_FROM_ROOT}/data/{self.crawler_id}/raw_pages/{self.hash(response.url)}.json", "w+") as f:
            f.write(json.dumps(content, indent=2))
