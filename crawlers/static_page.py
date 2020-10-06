# Scrapy and Twister libs
import scrapy
from scrapy.linkextractors import LinkExtractor

# Other external libs
import logging
import re
import requests

# Project libs
from crawlers.base_spider import BaseSpider


class StaticPageSpider(BaseSpider):
    name = 'static_page'

    def start_requests(self):
        print("At StaticPageSpider.start_requests")

        self.convert_allow_extesions()

        for req in self.generate_initial_requests():
            yield scrapy.Request(url=req['url'],
                method=req['method'],
                body=json.dumps(req['body']),
                callback=self.parse,
                meta={
                    "referer": "start_requests",
                    "config": self.config
                },
                errback=self.errback_httpbin)

    def convert_allow_extesions(self):
        """Converts 'allow_extesions' configuration into 'deny_extesions'."""
        allow_extension = f"download_files_allow_extensions"
        if (
            allow_extension in self.config and
            self.config[allow_extension] is not None and
            self.config[allow_extension] != ""
        ):
            allowed_extensions = set(self.config[allow_extension].split(","))
            extensions = [i for i in scrapy.linkextractors.IGNORED_EXTENSIONS]
            self.config[f"donwload_files_deny_extensions"] = [
                i for i in extensions if i not in allowed_extensions
            ]

    def filter_list_of_urls(self, url_list, pattern):
        """Filter a list of urls according to a regex pattern."""
        def allow(url):
            if re.search(pattern, url) is not None:
                print(f"ADDING link (passed regex filter) - {url}")
                return True
            print(f"DISCARDING link (filtered by regex) - {url}")
            return False

        urls_filtered = set(filter(allow, url_list))

        return urls_filtered

    def extract_links(self, response):
        """Filter and return a set with links found in this response."""

        config = response.meta['config']
        # TODO: cant make regex tested on https://regexr.com/ work
        # here for some reason
        links_extractor = LinkExtractor()
        #    allow=self.config["link_extractor_allow_url"])

        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["link_extractor_allow_url"]
        if pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        return urls_found

    def extract_files(self, response):
        """Filter and return a set with links found in this response."""
        config = response.meta['config']
        # TODO: cant make regex tested on https://regexr.com/ work
        # here for some reason
        links_extractor = LinkExtractor(
            deny_extensions = self.config["donwload_files_deny_extensions"]
        #    allow = self.config["download_files_allow_url"], ())
        )
        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["download_files_allow_url"]

        if pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        # removing non-file urls 
        # (ends with '.' + 3 or 4 chars and does not ends with ".html" or
        # ".php")
        urls_found = self.filter_list_of_urls(
            urls_found, r"(.*\.[a-z]{3,4}$)(.*(?<!\.html)$)(.*(?<!\.php)$)")

        return urls_found

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explore_links"] is set.
        """
        response_type = response.headers['Content-type']
        print(f"Parsing {response.url}, type: {response_type}")

        config = response.meta['config']

        if self.stop():
            return

        if b'text/html' in response_type:
            self.store_html(response)
            if "explore_links" in config and config["explore_links"]:
                this_url = response.url
                for url in self.extract_links(response):
                    yield scrapy.Request(
                        url=url, callback=self.parse,
                        meta={"referer": response.url,
                              "config": config},
                        errback=self.errback_httpbin
                    )

            if self.config["download_files"]:
                for file in self.extract_files(response):
                    self.feed_file_downloader(file, response)
        else:
            self.store_raw(response)
