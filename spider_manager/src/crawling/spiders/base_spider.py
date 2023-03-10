# Scrapy and Twister libs
import mimetypes
import re
import string

import requests
import scrapy
import ujson
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError

import crawling_utils
from crawling.spiders.redis_spider import RedisSpider

PUNCTUATIONS = "[{}]".format(string.punctuation)

class BaseSpider(RedisSpider):
    name = 'base_spider'
    request_session = requests.sessions.Session() 

    def __init__(self, config: dict, *args, **kwargs):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        super(BaseSpider, self).__init__(*args, **kwargs)

        self.config = ujson.loads(config)
        self.get_format = lambda i: str(i).split("/")[1][:-1].split(";")[0]

        if bool(self.config.get("download_files_allow_extensions")):
            normalized_allowed_extensions = self.config["download_files_allow_extensions"].replace(" ", "")
            normalized_allowed_extensions = normalized_allowed_extensions.lower()
            self.download_allowed_extensions = set(normalized_allowed_extensions.split(","))
        
        else:
            self.download_allowed_extensions = set()
            
        self.preprocess_link_configs()
        self.preprocess_download_configs()

    async def parse(self, response):
        """
        A function to treat the responses from a request.
        Should check self.stop() at every call.
        """
        raise NotImplementedError

    # # based on: https://github.com/steveeJ/python-wget/blob/master/wget.py
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
        if mimetype is None:
            return [""]

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
            value = tuple(value.split(","))
        
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
