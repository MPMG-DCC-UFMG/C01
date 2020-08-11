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
        print("TO NA START REQUESTS")
        urls = [self.config["base_url"]]
        # if self.config["url"]["type"] == "simple":
        #     urls = [self.config["url"]["url"]]
        # elif self.config["url"]["type"] == "template":
        #     # urls = ParamInjector.generate_format(
        #     #     self.config["url"]["tamplate_params"]["code_format"],
        #     #     self.config["url"]["tamplate_params"]["param_limits"],
        #     #     self.config["url"]["tamplate_params"]["verif"],
        #     #     self.config["url"]["tamplate_params"]["verif_index"],
        #     # )
        #     pass
        # else:
        #     raise ValueError

        if self.config["crawler_type"] == "single_file":
            raise ValueError
        elif self.config["crawler_type"] == "file_bundle":
            raise ValueError
        elif self.config["crawler_type"] == "deep_crawler":
            raise ValueError
        elif self.config["crawler_type"] == "static_page":
            # DO STUFF
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
        else:
            raise ValueError

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explor_links"] is set.
        """


        print(response.url, response.headers['Content-type'])

        if self.stop():
            return

        # self.extract_and_store_csv(response)

        if response.headers['Content-type'] == b'text/html':
            self.store_html(response)

            if "explore_links" in self.config and self.config["explore_links"]:
                pfx = "link_extractor_"

                # convert allow extensions into deny_extensions
                allow_extension = f"{pfx}allow_extensions"
                if allow_extension in self.config and self.config[allow_extension] != "":
                    allowed_extensions = self.config[allow_extension].split(",")
                    self.config[f"{pfx}deny_extensions"] = [
                        i for i in scrapy.linkextractors.IGNORED_EXTENSIONS if i not in allowed_extensions
                    ]

                # function to get other keys from dictionary
                def get_link_config(key, default):
                    key = pfx + key
                    if key in self.config:
                        return self.config[key]
                    return default

                links_extractor = LinkExtractor(
                    # TODO: cant make regex tested on https://regexr.com/ work here for some reason
                    # allow=get_link_config("allow", ())
                    deny=get_link_config("deny", ()),
                    allow_domains=get_link_config("allow_domains", ()),
                    deny_domains=get_link_config("deny_domains", ()),
                    # Note here: changed the default value. It would ignore all links with extensions
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

                # As I could not make the allow parameter work, the code check the regex on the urls here
                for url in links_extractor.extract_links(response):
                    print(url.url)
                    match = False
                    if self.config["link_extractor_allow"] != "":
                        # for pattern in self.config["link_extractor_allow"]:
                        #     match = match or (re.search(pattern, url.url) is not None)
                        match = match or (re.search(self.config["link_extractor_allow"], url.url) is not None)

                    else:
                        match = True

                    if match:
                        print("calling")
                        yield scrapy.Request(url=url.url, callback=self.parse)
                    else:
                        print("ignoring")
                # Fixing the allow parameter, just change the code above by the code commented below
                # for url in links_extractor.extract_links(response):
                #     yield scrapy.Request(url=url.url, callback=self.parse)
                # END CODE
        else:
            self.store_raw(response)
        self.extract_and_store_csv(response)
