import os
import scrapy
from scrapy.http import Request

from scrapy.crawler import CrawlerProcess

COLLECTION_URL = "https://www.araguari.mg.gov.br/assets/uploads/correio/"
FOLDER_PATH = "diario-oficial-araguari-scrapy"


class DOMAraguari(scrapy.Spider):

    name = "diario-oficial-araguari"
    start_urls = [COLLECTION_URL]

    def __init__(self):
        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)

    def parse(self, response):
        links = [a.attrib["href"] for a in response.css('td > a:not([href *= "assets"])')]
        for link in links:
            yield Request(url=response.urljoin(link), callback=self.save_file)

    def save_file(self, response):
        file_name = response.url.split('/')[-1]
        directory = os.path.join(FOLDER_PATH, "{}".format(file_name[-3:]))

        if not os.path.exists(directory):
            os.makedirs(directory)

        path = os.path.join(directory, file_name)
        self.logger.info('Saving file %s', file_name)
        with open(path, 'wb') as f:
            f.write(response.body)

def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'DOWNLOAD_TIMEOUT': 1800,
        'DOWNLOAD_WARNSIZE': 500000000,
        'RETRY_TIMES': 5
    })

    process.crawl(DOMAraguari)
    process.start()

if __name__ == "__main__":
    main()
