# Scrapy and Twister libs
import scrapy
from scrapy.linkextractors import LinkExtractor

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
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}

class StaticPageSpider(BaseSpider):
    name = 'static_page'

    def start_requests(self):
        print("At StaticPageSpider.start_requests")

        for req in self.generate_initial_requests():

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
                },
                errback=self.errback_httpbin)

    def get_url_info(self, url: str) -> tuple:
        """Retrieves the type of URL content and its size"""
        res = self.request_session.head(url, allow_redirects=True, headers=HTTP_HEADERS)

        content_type = res.headers.get('Content-Type')
        content_lenght = int(res.headers.get('Content-Length', '0'))
        content_disposition = res.headers.get('Content-Disposition', '')

        return url, content_lenght, content_type, content_disposition

    def filter_urls_by_regex(self, urls, pattern):
        """Filter a list of urls according to a regex pattern."""
        def allow(url):
            search_results = re.search(pattern, url)
            return bool(search_results)
        return list(filter(allow, urls))

    def filter_urls_by_content_type(self, urls_info: list, content_types: set) -> list:
        def allow(url_info: tuple):
            url, _, ctype, cdisp = url_info
            guesseds_content_type = self.detect_file_extensions(url, ctype, cdisp)
            common_content_types = content_types.intersection(guesseds_content_type)
            return len(common_content_types) > 0
        return list(filter(allow, urls_info))

    def extract_links(self, response):
        """Filter and return a set with links found in this response."""
        links_extractor = LinkExtractor(
            allow_domains=self.config["link_extractor_allow_domains"],
            tags=self.config["link_extractor_tags"],
            attrs=self.config["link_extractor_attrs"],
            process_value=self.config["link_extractor_process_value"],
        )

        urls_found = set(i.url for i in links_extractor.extract_links(response))

        pattern = self.config["link_extractor_allow_url"]
        if bool(pattern):
            urls_found = self.filter_urls_by_regex(urls_found, pattern)

        if self.config["link_extractor_check_type"]:
            urls_info = list(self.get_url_info(url) for url in urls_found)
            urls_info_filtered = self.filter_urls_by_content_type(urls_info, {'html'})
            urls_found = set(url for url, _, _, _ in urls_info_filtered)
        
        else:
            urls_found = set(urls_found)

        print(f"+{len(urls_found)} urls found...")

        return urls_found

    def extract_files(self, response):
        """Filter and return a set with links found in this response."""

        links_extractor = LinkExtractor(
            allow_domains=self.config["download_files_allow_domains"],
            tags=self.config["download_files_tags"],
            attrs=self.config["download_files_attrs"],
            process_value=self.config["download_files_process_value"],
            deny_extensions=self.config["download_files_deny_extensions"]
        )

        urls_found = set(link.url for link in links_extractor.extract_links(response))

        exclude_html_and_php_regex_pattern = r"(.*\.[a-z]{3,4}$)(.*(?<!\.html)$)(.*(?<!\.php)$)" 
        urls_found = self.filter_urls_by_regex(urls_found, exclude_html_and_php_regex_pattern)

        pattern = self.config["download_files_allow_url"]
        if bool(pattern):
            urls_found = self.filter_urls_by_regex(urls_found, pattern)

        urls_info = None 

        if self.config["download_files_check_type"]:
            urls_info = list(self.get_url_info(url) for url in urls_found)
            urls_info = self.filter_urls_by_content_type(urls_info, self.download_allowed_extensions)

        if self.config.get("download_files_check_large_content", False):
            if urls_info is None:
                urls_info = list(self.get_url_info(url) for url in urls_found)

            urls_small_content = set()
            urls_large_content = set()

            for url, lenght, _, _ in urls_info:
                if lenght > LARGE_CONTENT_LENGTH:
                    urls_large_content.add(url)
                else:
                    urls_small_content.add(url)

            print(f"+{len(urls_small_content)} small files detected...")
            print(f"+{len(urls_large_content)} large files detected...")

            return urls_small_content, urls_large_content

        else:
            if urls_info is None:
                return urls_found, set()

            urls_found = set(url for url, _, _, _ in urls_info)
            print(f"+{len(urls_found)} small files detected...")

            return urls_found, set()

    def extract_imgs(self, response):
        url_domain = crawling_utils.get_url_domain(response.url)

        src = []
        for img in response.xpath("//img"):
            img_src = img.xpath('@src').extract_first()
            if img_src[0] == '/':
                img_src = url_domain + img_src[1:]
            src.append(img_src)

        print(f"+{len(src)}imgs found at page {response.url}")
        
        return set(src)

    def parse(self, response):
        """
        Parse responses of static pages.
        Will try to follow links if config["explore_links"] is set.
        """
        response_type = response.headers['Content-type']
        print(f"Parsing {response.url}, type: {response_type}")

        if self.stop():
            return

        if b'text/html' not in response_type:
            self.store_small_file(response)
            return

        self.store_html(response)
        
        urls = set()
        urls_large_file_content = []
        if "explore_links" in self.config and self.config["explore_links"]:
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
                },
                errback=self.errback_httpbin
            )