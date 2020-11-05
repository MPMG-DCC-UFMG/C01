import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy_puppeteer import PuppeteerRequest

from crawlers.base_spider import BaseSpider

import requests
import logging
import os
import re
import json
import random
import datetime
import hashlib


class FormPageSpider(BaseSpider):
    name = 'form_page'

    def start_requests(self):
        url = self.config["base_url"]
        steps = self.config["steps"]
        print("form_page.start_requests")
        
        yield PuppeteerRequest(url=url, callback=self.parse, dont_filter=True, steps=steps)

    def parse(self, response):
        print(vars(response))
        print(len(response.request.meta["pages"]))
        print(response.request.meta["pages"].keys())
        pass

        