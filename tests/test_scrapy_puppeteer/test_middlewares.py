import asyncio
from twisted.internet import asyncioreactor
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from twisted.internet import defer
from twisted.trial.unittest import TestCase

import scrapy_puppeteer


class ScrapyPuppeteerTestCase(TestCase):
    """Test case for the ``scrapy-puppeteer`` package"""

    class PuppeteerSpider(scrapy.Spider):
        name = 'puppeteer_crawl_spider'
        allowed_domains = ['ufmg.br']
        items = []

        def start_requests(self):
            yield scrapy_puppeteer.PuppeteerRequest(
                'https://ufmg.br',
                wait_until='networkidle2'
            )

        def parse(self, response):
            for selector_item in response.selector.xpath('//*[@id="rodape"]/section[1]/div/div[1]/div/ol/li'):
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
        self.assertEqual(len(crawler.spider.items), 12)