#needs to be imported before scrapy
from scrapy_puppeteer import PuppeteerRequest

# Scrapy and Twister libs
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse

# Other external libs
import logging
import re
import json
import requests
import time

# Project libs
from crawlers.base_spider import BaseSpider
import crawling_utils

LARGE_CONTENT_LENGTH = 1e9


class PageSpider(BaseSpider):
    name = 'page_spider'

    def start_requests(self):
        print("At StaticPageSpider.start_requests")

        for req in self.generate_initial_requests():
            if self.config.get("dynamic_processing", False):
                steps = json.loads(self.config["steps"])

                yield PuppeteerRequest(url=req['url'],
                    callback=self.dynamic_parse,
                    dont_filter=True,
                    meta={
                        "referer": "start_requests",
                        "config": self.config
                    },
                    steps=steps)
            else:
                # Don't send an empty dict, may cause spider to be blocked
                body_contents = None
                if bool(req['body']):
                    body_contents = json.dumps(req['body'])

                yield scrapy.Request(url=req['url'],
                    method=req['method'],
                    body=body_contents,
                    callback=self.parse,
                    meta={
                        "referer": "start_requests",
                        "config": self.config
                },
                    errback=self.errback_httpbin)

    def convert_allow_extesions(self, config):
        """Converts 'allow_extesions' configuration into 'deny_extesions'."""
        allow = "download_files_allow_extensions"
        deny = "download_files_deny_extensions"
        if (
            allow in config and
            config[allow] is not None and
            config[allow] != "" and
            deny not in config
        ):
            allowed_extensions = set(config[allow].split(","))
            extensions = [i for i in scrapy.linkextractors.IGNORED_EXTENSIONS]
            config[deny] = [
                i for i in extensions if i not in allowed_extensions
            ]
        return config

    def get_url_content_type_and_lenght(self, url) -> tuple:
        """Retrieves the type of URL content and its size"""
        
        # TODO: Use antiblock mechanisms here 
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
        response = requests.head(url, allow_redirects=True, headers=headers)

        content_type = response.headers.get('Content-Type')
        content_lenght = int(response.headers.get('Content-Length', '0'))

        response.close()

        return url, content_type, content_lenght

    def filter_list_of_urls(self, url_list, pattern):
        """Filter a list of urls according to a regex pattern."""
        def allow(url):
            if (re.search(pattern, url) is not None):
                # print(f"ADDING link (passed regex filter) - {url}")
                return True
            # print(f"DISCARDING link (filtered by regex) - {url}")
            return False

        urls_filtered = set(filter(allow, url_list))

        return urls_filtered

    def filter_type_of_urls_and_split_small_content(self, url_list, page_flag, split_large_content=True):
        """Filter a list of urls according to the Content-Type and split urls with small content (avoiding send too many requests
        to the server to verify if the content is large or not)
        """
        def allow_type(url_with_type_and_lenght):
            req_head = url_with_type_and_lenght[1]
            if (('html' in req_head) and page_flag) or (('html' not in req_head) and not page_flag):
                return True
            return False

        urls_with_type_and_lenght = [self.get_url_content_type_and_lenght(url) for url in url_list]
        urls_with_type_and_lenght_filtered = set(filter(allow_type, urls_with_type_and_lenght))

        urls = set(url_type_lenght[0] for url_type_lenght in urls_with_type_and_lenght_filtered)         
        if split_large_content:
            urls_with_small_content = set(url_type_lenght[0] 
                                            for url_type_lenght in urls_with_type_and_lenght
                                            if url_type_lenght[2] < LARGE_CONTENT_LENGTH)

            return urls_with_small_content, urls.difference(urls_with_small_content)

        return urls

    def split_urls_in_small_content(self, url_list):
        def is_small_content(url):
            # TODO: Use antiblock mechanisms here 
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
            response = requests.head(url, allow_redirects=True, headers=headers)
            content_lenght = int(response.headers.get('Content-Length', '0'))
            response.close()

            return content_lenght < LARGE_CONTENT_LENGTH

        urls_small_content = set(url for url in url_list if is_small_content(url))
        return urls_small_content, set(url_list).difference(urls_small_content)

    def preprocess_listify(self, value, default):
        """Converts a string of ',' separaded values into a list."""
        if value is None or len(value) == 0:
            value = default
        elif type(value) == str:
            value = tuple(value.split(","))
        return value

    def preprocess_link_configs(self, config):
        """Process link_extractor configurations."""
        if "link_extractor_processed" in config:
            return config

        defaults = [
            ("link_extractor_tags", ('a', 'area')),
            ("link_extractor_allow_domains", None),
            ("link_extractor_attrs", ('href',))
        ]
        for attr, default in defaults:
            config[attr] = self.preprocess_listify(config[attr], default)

        config["link_extractor_processed"] = True

        return config

    def extract_links(self, response):
        """Filter and return a set with links found in this response."""
        config = self.preprocess_link_configs(response.meta["config"])

        links_extractor = LinkExtractor(
            allow_domains=config["link_extractor_allow_domains"],
            tags=config["link_extractor_tags"],
            attrs=config["link_extractor_attrs"],
            process_value=config["link_extractor_process_value"],
        )

        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["link_extractor_allow_url"]
        if pattern is not None and pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        if config["link_extractor_check_type"]:
            urls_found = self.filter_type_of_urls_and_split_small_content(urls_found, True, False)

        print("Links kept: ", urls_found)

        return urls_found

    def preprocess_download_configs(self, config):
        """Process download_files configurations."""
        if "download_files_processed" in config:
            return config

        defaults = [
            ("download_files_tags", ('a', 'area')),
            ("download_files_allow_domains", None),
            ("download_files_attrs", ('href',))
        ]
        for attr, default in defaults:
            config[attr] = self.preprocess_listify(config[attr], default)

        config = self.convert_allow_extesions(config)

        attr = "download_files_process_value"
        if config[attr] is not None and len(config[attr]) > 0 and type(config[attr]) is str:
            config[attr] = eval(config[attr])

        config["download_files_processed"] = True

        return config

    def extract_files(self, response):
        """Filter and return a set with links found in this response."""
        config = self.preprocess_download_configs(response.meta["config"])

        links_extractor = LinkExtractor(
            allow_domains=config["download_files_allow_domains"],
            tags=config["download_files_tags"],
            attrs=config["download_files_attrs"],
            process_value=config["download_files_process_value"],
            deny_extensions=config["download_files_deny_extensions"]
        )
        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["download_files_allow_url"]

        if pattern is not None and pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        
        urls_small_content = set()
        urls_large_content = set()
        
        if config["download_files_check_type"]:
            urls_small_content, urls_large_content = self.filter_type_of_urls_and_split_small_content(urls_found, False)

        urls_files = self.filter_list_of_urls(
            urls_found, r"(.*\.[a-z]{3,4}$)(.*(?<!\.html)$)(.*(?<!\.php)$)")

        urls_files = urls_files.difference(urls_small_content)
        urls_files = urls_files.difference(urls_large_content)

        urls_small_content_b, urls_large_content_b = self.split_urls_in_small_content(urls_files)

        urls_small_content = urls_small_content.union(urls_small_content_b)
        urls_large_content = urls_large_content.union(urls_large_content_b)

        print(f"+{len(urls_small_content)} small files detected: ", urls_small_content)
        print(f"+{len(urls_large_content)} large files detected: ", urls_large_content)

        return urls_small_content, urls_large_content

    def extract_imgs(self, response):
        url_domain = crawling_utils.get_url_domain(response.url)

        src = []
        for img in response.xpath("//img"):
            img_src = img.xpath('@src').extract_first()
            if type(img_src) is str:
                if img_src[0] == '/':
                    img_src = url_domain + img_src[1:]
                src.append(img_src)

        print(f"imgs found at page {response.url}", src)
        return set(src)

    def dynamic_parse(self, response):
        for page in list(response.request.meta["pages"].values()):
            dynamic_response = HtmlResponse(
                response.url,
                status=response.status,
                headers=response.headers,
                body=page,
                encoding='utf-8',
                request=response.request
            )

            for request in self.parse(dynamic_response):
                yield request

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explore_links"] is set.
        """
        response_type = response.headers['Content-type']
        print(f"Parsing {response.url}, type: {response_type}")

        config = response.request.meta['config']

        if self.stop():
            return

        if b'text/html' not in response_type:
            self.store_small_file(response)
            return

        self.store_html(response)

        urls = set()
        urls_large_file_content = []
        if "explore_links" in config and config["explore_links"]:
            this_url = response.url
            urls = self.extract_links(response)

        if "download_files" in self.config and self.config["download_files"]:
            urls_small_file_content, urls_large_file_content = self.extract_files(response)
            urls = urls.union(urls_small_file_content)

        if "download_imgs" in self.config and self.config["download_imgs"]:
            urls = self.extract_imgs(response).union(urls)

        if len(urls_large_file_content) > 0:
            size = len(urls_large_file_content)
            for idx, url in enumerate(urls_large_file_content, 1):
                print(f"Downloading large file {url} {idx} of {size}")
                self.store_large_file(url, response.meta["referer"])

                # So that the interval between requests is concise between Scrapy and downloading large files
                if self.config["antiblock_download_delay"]:
                    print(f"Waiting {self.config['antiblock_download_delay']}s for the next download...")
                    time.sleep(self.config["antiblock_download_delay"])

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "referer": response.url,
                    "config": config
                },
                errback=self.errback_httpbin
            )