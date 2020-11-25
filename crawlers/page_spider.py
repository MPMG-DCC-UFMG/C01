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
from scrapy_puppeteer import PuppeteerRequest

class PageSpider(BaseSpider):
    name = 'page_spider'

    def start_requests(self):
        print("At StaticPageSpider.start_requests")

        self.convert_allow_extesions()

        for req in self.generate_initial_requests():
            if self.config.get("dynamic_processing", False):
                steps = json.loads(self.config["steps"])

                yield PuppeteerRequest(url=req['url'],
                    callback=self.form_parse,
                    dont_filter=True,
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
            if (re.search(pattern, url) is not None):
                # print(f"ADDING link (passed regex filter) - {url}")
                return True
            # print(f"DISCARDING link (filtered by regex) - {url}")
            return False

        urls_filtered = set(filter(allow, url_list))

        return urls_filtered

    def filter_type_of_urls(self, url_list, page_flag):
        """Filter a list of urls according to the Content-Type."""
        def allow(url):
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
            req_head = requests.head(url, allow_redirects=True, headers=headers).headers['Content-Type']
            if (('html' in req_head) and page_flag) or (('html' not in req_head) and not page_flag):
                # print(f"ADDING link (correct type) - {url}")
                return True
            # print(f"DISCARDING link (incorrect type) - {url}")
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

        urls_found = self.filter_type_of_urls(urls_found, True)

        print("Links kept: ", urls_found)

        return urls_found

    def extract_files(self, response):
        """Filter and return a set with links found in this response."""
        config = response.meta['config']
        # TODO: cant make regex tested on https://regexr.com/ work
        # here for some reason
        links_extractor = LinkExtractor(
            deny_extensions=self.config["donwload_files_deny_extensions"]
            #    allow = self.config["download_files_allow_url"], ())
        )
        urls_found = {i.url for i in links_extractor.extract_links(response)}

        pattern = config["download_files_allow_url"]

        if pattern != "":
            urls_found = self.filter_list_of_urls(urls_found, pattern)

        urls_found_a = self.filter_type_of_urls(urls_found, False)

        urls_found_b = self.filter_list_of_urls(
            urls_found, r"(.*\.[a-z]{3,4}$)(.*(?<!\.html)$)(.*(?<!\.php)$)")

        urls_found = urls_found_a.union(urls_found_b)

        print("Files kept: ", urls_found)

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

    def form_parse(self, response):
        for page in response.request.meta["pages"].values():
            response.body = str.encode(page)
            self.parse(response)

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

        if "download_files" in self.config and self.config["download_files"]:
            for file in self.extract_files(response):
                self.feed_file_downloader(file, response)

        print("download_imgs", self.config["download_imgs"])
        if "download_imgs" in self.config and self.config["download_imgs"]:
            for img_url in self.extract_imgs(response):
                print("feeding", img_url)
                self.feed_file_downloader(img_url, response)
