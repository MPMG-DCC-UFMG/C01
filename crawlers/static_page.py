import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

from crawlers.base_spider import BaseSpider

import requests
import logging
import os
import re
import json
import random
import datetime
import hashlib


class StaticPageSpider(BaseSpider):
    name = 'static_page'

    def start_requests(self):
        print("At StaticPageSpider.start_requests")
        urls = [self.config["base_url"]]

        self.convert_allow_extesions()

        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse,
                meta={"referer": "start_requests",
                      "config": self.config},
                errback=self.errback_httpbin
            )

    def convert_allow_extesions(self):
        """Converts 'allow_extesions' configuration into 'deny_extesions'."""
        allow_extension = f"link_extractor_allow_extensions"
        if (
            allow_extension in self.config and
            self.config[allow_extension] is not None and
            self.config[allow_extension] != ""
        ):
            allowed_extensions = set(self.config[allow_extension].split(","))
            extensions = [i for i in scrapy.linkextractors.IGNORED_EXTENSIONS]
            self.config[f"link_extractor_deny_extensions"] = [
                i for i in extensions if i not in allowed_extensions
            ]

    def extract_links(self, response):
        """Filter and return a set with links found in this response."""
        pfx = "link_extractor_"

        config = response.meta['config']

        # function to get other keys from dictionary
        def get_link_config(key, default):
            key = pfx + key
            if key in config:
                return config[key]
            return default

        links_extractor = LinkExtractor(
            # TODO: cant make regex tested on https://regexr.com/ work
            # here for some reason
            # allow=get_link_config("allow", ())
            deny=get_link_config("deny", ()),
            allow_domains=get_link_config("allow_domains", ()),
            deny_domains=get_link_config("deny_domains", ()),
            # Note here: changed the default value. It would ignore all
            # links with extensions
            deny_extensions=get_link_config("deny_extensions", []),
            restrict_xpaths=get_link_config("restrict_xpaths", ()),
            restrict_css=get_link_config("restrict_css", ()),
            tags=get_link_config("tags", 'a'),
            attrs=get_link_config("attrs", 'href'),
            canonicalize=get_link_config("canonicalize", False),
            unique=get_link_config("unique", True),
            process_value=get_link_config("process_value", None),
            strip=get_link_config("strip", True)
        )

        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["link_extractor_allow"]
        if pattern != "":
            def allow(url):
                if re.search(pattern, url) is not None:
                    print(f"ADDING link (passed regex filter) - {url}")
                    return True
                print(f"DISCARDING link (filtered by regex) - {url}")
                return False

            urls_filtered = set(filter(allow, urls_found))

            for url in urls_found:
                this_url = response.url

            urls_found = urls_filtered

        return urls_found

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explor_links"] is set.
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
        else:
            self.store_raw(response)
