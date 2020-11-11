# Scrapy and Twister libs
import scrapy
from scrapy.linkextractors import LinkExtractor

# Other external libs
import logging
import re
import json
import requests

# Project libs
from crawlers.base_spider import BaseSpider
import crawling_utils


class StaticPageSpider(BaseSpider):
    name = 'static_page'
    
    def __init__(self, *args, **kwargs):
        super(StaticPageSpider, self).__init__(*args, **kwargs)
        print("////////////////////////////////////////////")

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
        #    allow=config["link_extractor_allow_url"])

        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["link_extractor_allow_url"]
        if pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        return urls_found

    def extract_files(self, response):
        """Filter and return a set with links found in this response."""
        config = response.meta['attrs']
        # TODO: cant make regex tested on https://regexr.com/ work
        # here for some reason
        links_extractor = LinkExtractor(
            deny_extensions = config["donwload_files_deny_extensions"]
        #    allow = config["download_files_allow_url"], ())
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

    def extract_imgs(self, response):
        url_domain = crawling_utils.get_url_domain(response.url)

        src = []
        for img in response.xpath("//img"):
            img_src = img.xpath('@src').extract_first()
            if img_src[0] == '/':
                img_src = url_domain + img_src[1:]
            src.append(img_src)

        print(f"imgs found at page {response.url}", src)
        return set(src)

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explore_links"] is set.
        """
        response_type = response.headers['Content-type']
        print(f"Parsing {response.url}, type: {response_type}")

        config = response.meta['attrs']

        if self.stop():
            return

        if b'text/html' not in response_type:
            self.store_raw(response)
            return

        self.store_html(response)
        if "explore_links" in config and config["explore_links"]:
            this_url = response.url
            for url in self.extract_links(response):
                yield scrapy.Request(
                    url=url, callback=self.parse,
                    meta={"referer": response.url, "config": config},
                    errback=self.errback_httpbin
                )

        if "download_files" in config and config["download_files"]:
            for file in self.extract_files(response):
                self.feed_file_downloader(file, response, config)

        print("download_imgs", config["download_imgs"])
        if "download_imgs" in config and config["download_imgs"]:
            for img_url in self.extract_imgs(response):
                print("feeding", img_url)
                self.feed_file_downloader(img_url, response, config)