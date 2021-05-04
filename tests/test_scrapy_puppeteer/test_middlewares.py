import os
import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.trial.unittest import TestCase

import unittest
import scrapy_puppeteer

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class ScrapyPuppeteerTestCase(unittest.TestCase):
    """Test case for the ``scrapy-puppeteer`` package"""

    class PuppeteerSpider(scrapy.Spider):
        name = 'puppeteer_crawl_spider'
        allowed_domains = ['ufmg.br']
        handle_httpstatus_list = [0]
        items = []

        def start_requests(self):
            yield scrapy.Request(
                "file://" + os.path.join(THIS_DIR, "test_files", "test1.html"),
                wait_until='networkidle2'
            )

        def parse(self, response):
            for selector_item in response.selector.xpath('//*[@id="lista-itens"]/li'):
                self.items.append(selector_item)

    def setUp(self):
        """Store the Scrapy runner to use in the tests"""
        self.settings = custom_settings = {
                'DOWNLOADER_MIDDLEWARES': {
                    'scrapy_puppeteer.PuppeteerMiddleware': 800
                }
            }
        self.process = CrawlerProcess(settings=self.settings)

    def test_items_number(self):
        crawler = self.process.create_crawler(self.PuppeteerSpider)
        self.process.crawl(crawler)
        self.process.start()
        self.assertEqual(len(crawler.spider.items), 10)