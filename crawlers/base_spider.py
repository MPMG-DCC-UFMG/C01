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
from crawlers.injector_tools import create_probing_object,\
    create_parameter_generators
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
        form_req_type = self.config['form_request_type']

        has_placeholder = "{}" in base_url
        templated_url_generator = [[None]]
        templated_url_probe = create_probing_object(base_url, req_type)

        if has_placeholder:
            # Configure the probing process
            templated_url_probe = create_probing_object(base_url, req_type,
                self.config['templated_url_response_handlers']
            )

            # Instantiate the parameter injectors for the URL
            url_injectors = create_parameter_generators(templated_url_probe,
                self.config['templated_url_parameter_handlers']
            )

            # Generate the requests
            templated_url_generator = itertools.product(*url_injectors)

        use_static_forms = self.config['static_form_parameter_handlers']
        static_form_generator = [[None]]
        static_form_probe = create_probing_object(base_url, form_req_type)

        if use_static_forms:
            # Configure the probing process
            static_form_probe = create_probing_object(base_url, form_req_type,
                self.config['static_form_response_handlers']
            )

            # Instantiate the parameter injectors for the forms
            static_injectors = create_parameter_generators(static_form_probe,
                self.config['static_form_parameter_handlers']
            )

            # Generate the requests
            static_form_generator = itertools.product(*static_injectors)

        parameter_keys = list(map(lambda x: x['parameter_key'],
            self.config['static_form_parameter_handlers']))
        for templated_param_combination in templated_url_generator:
            # Check if this entry hits a valid page

            is_valid = templated_url_probe.check_entry(
                url_entries=templated_param_combination
            )
            if is_valid:

                # Copy the generator (we'd need to "rewind" if we used the
                # original)
                cp_result = itertools.tee(static_form_generator)
                static_form_generator, static_form_generator_cp = cp_result

                # Iterate through the form data now
                for form_param_combination in static_form_generator_cp:

                    req_entries = dict(zip(parameter_keys,
                        form_param_combination))

                    # Check if once again we hit a valid page
                    is_valid = static_form_probe.check_entry(
                        url_entries=templated_param_combination,
                        req_entries=req_entries
                    )

                    if is_valid:
                        # Insert parameters into URL and request body
                        curr_url = base_url\
                            .format(*templated_param_combination)

                        method = form_req_type
                        if not use_static_forms:
                            # If no form data is injected, use the regular
                            # request method set
                            method = req_type

                        yield {
                            'url': curr_url,
                            'method': method,
                            'body': req_entries
                        }

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
