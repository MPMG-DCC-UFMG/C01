import scrapy
from scrapy.crawler import CrawlerProcess
import json

class MySpider(scrapy.Spider):
    name = 'ammg-spider'
    start_urls = [
        'https://stackoverflow.com/questions/57245315/using-scrapy-how-to-download-pdf-files-from-some-extracted-links'
    ]

    def parse(self, response):
        f = open("links_ammg.json", 'r') 
        links = json.loads(f.read())
        f.close()

        for link in links:
            # print(link[2])
            yield {
               'file_urls': [link['url']]
            }

c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',

    # save in file as CSV, JSON or XML
    # 'FEED_FORMAT': 'csv',     # csv, json, xml
    # 'FEED_URI': 'output.csv', # 

    # download files to `FILES_STORE/full`
    # it needs `yield {'file_urls': [url]}` in `parse()`
    'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},
    'FILES_STORE': '.',
    'DNS_TIMEOUT': 180
})
c.crawl(MySpider)
c.start()
