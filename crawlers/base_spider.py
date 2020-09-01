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

from lxml.html.clean import Cleaner
import codecs


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, output_path, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.stop_flag = False

        # # print("caminho: ",self.config["output_path"] )
        # print("config: ", self.config)
        # if self.config["output_path"] is None:
        #     output_path = CURR_FOLDER_FROM_ROOT
        # else:
        #     output_path = self.config["output_path"]

        self.data_folder = f"{output_path}/data/{crawler_id}"
        cofig_file_path = f"{output_path}/config/{crawler_id}.json"
        self.flag_folder = f"{output_path}/flags/"

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

    def stop(self):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """
        flag_file = f"{self.flag_folder}/{self.crawler_id}.json"
        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response, output_filename, save_csv):
        """
        Try to extract a json/csv from response data.
        """
        file_format = self.get_format(response.headers['Content-type'])
        hsh = crawling_utils.hash(response.url)

        if output_filename is None:
            output_filename = f"{self.data_folder}/csv/{hsh}"
        else:
            output_filename = f"{self.data_folder}/csv/" + output_filename
        if save_csv and (".csv" not in output_filename):
            output_filename += ".csv"

        try:
            parsing_html.content.html_detect_content(
                f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                is_string=False,
                # output_file=f"{self.data_folder}/csv/{hsh}",
                output_file=output_filename,
                to_csv=save_csv,
            )
        except Exception as e:
            print(
                f"Could not extract csv from {response.url} -",
                f"message: {str(type(e))}-{e}"
            )

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

        hsh = crawling_utils.hash(response.url)

        folder = f"{self.data_folder}/{save_at}"

        content = {
            "file_name": f"{hsh}.{file_format}",
            "url": response.url,
            "crawler_id": self.crawler_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
        }

        with open(f"{folder}/file_description.jsonl", "a+") as f:
            f.write(json.dumps(content) + '\n')

        with open(
            file=f"{folder}/{hsh}.{file_format}",
            mode=file_mode,
            encoding=encoding,
        ) as f:
            f.write(body)

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        self.store_raw(
            response, file_format="html", binary=False, save_at="raw_pages")
