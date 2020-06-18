import json
import logging
import os
import time
import scrapy

from scrapy.http import TextResponse

from scrapy.crawler import CrawlerProcess

COLLECTION_URL = "https://muriae.mg.gov.br/licitacao/"
FOLDER_PATH = "coleta"
ID_FORMAT = "{:03d}"

class MuriaeCrawler(scrapy.Spider):
    name = "licitacoes_muriae"
    start_urls = [
        COLLECTION_URL,
    ]
    
    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.WARNING)

        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)

        # list of css selectors used to advance from one "layer" to the next
        self.follow_list = [\
            '#projects-archive article a.header-button.callout-btn::attr("href")',
            'a.attachment-link::attr("href")']
        # list of css collectors used to advance from one page to the next in
        # the same "layer"
        self.pagination_list = ['li.nav-previous a::attr("href")', None, None]
        # list of folders to store each layer in
        self.folder_list = [\
            os.path.join(FOLDER_PATH, "listas"),
            os.path.join(FOLDER_PATH, "paginas"),
            os.path.join(FOLDER_PATH, "anexos")
        ]

        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)

        for folder_path in self.folder_list:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    def parse(self, response):
        # get the full path to the current branch we're crawling
        current_path = response.meta.get('crawl_path', '[1]')
        current_path = json.loads(current_path)
        # our current scraping "layer"
        current_layer = int(response.meta.get('layer', 0))
        # our current page in this scraping "layer"
        current_page = int(response.meta.get('page', 1))

        file_name_pre = ""
        for part in current_path:
            if len(file_name_pre) > 0:
                file_name_pre += "-"
            file_name_pre += ID_FORMAT.format(part)

        # Detect if file is an html or an attachment
        is_attachment = ("download" in response.headers.get("Content-Type").decode("utf-8"))

        if not isinstance(response, TextResponse) or is_attachment:
            # Binary response or marked as attachment, download it

            file_name = file_name_pre + "--"
            if "Content-Disposition" in response.headers:
                file_data = response.headers["Content-Disposition"].decode("utf-8").split(";")
                for d in file_data:
                    d_entry = d.split("=")
                    if len(d_entry) > 1:
                        name, value = d_entry
                        if name.strip() == "filename":
                            file_name += value

            file_name = os.path.join(self.folder_list[current_layer], file_name)

            with open(file_name, 'wb') as f:
                f.write(response.body)
        else:
            # Text response (suppose it's html)

            # check if there is pagination at this layer
            if current_layer < len(self.pagination_list) and \
                self.pagination_list[current_layer] is not None:
                # go to the next page in this layer if it exists
                next_page = response.css(self.pagination_list[current_layer])
                if next_page is not None and len(next_page) > 0:
                    next_page = next_page[0].get()
                    request = scrapy.Request(next_page, callback=self.parse)
                    request.meta['layer'] = current_layer
                    request.meta['page'] = current_page + 1
                    # Update the current layer in the crawling tree
                    updated_path = current_path.copy()
                    updated_path[-1] = current_page + 1
                    request.meta['crawl_path'] = json.dumps(updated_path)
                    yield request

            # write current file
            file_name = file_name_pre + ".html"
            file_name = os.path.join(self.folder_list[current_layer], file_name)

            with open(file_name, 'wb') as f:
                f.write(response.body)

            # request all pages for next layer contained in this page
            count = 1
            if current_layer < len(self.follow_list) and \
                self.follow_list[current_layer] is not None:
                entry_links = response.css(self.follow_list[current_layer])
                # Insert another layer into the crawling tree
                updated_path = current_path.copy()
                updated_path.append(1)
                # If next layer has multiple pages
                multi_page = current_layer + 1 < len(self.pagination_list) and \
                    self.pagination_list[current_layer + 1] is not None
                if multi_page:
                    # Insert a new counter into the crawling tree for that
                    updated_path.append(0)

                for entry in entry_links:
                    curr_link = entry.get()
                    request = scrapy.Request(curr_link, callback=self.parse)
                    request.meta['page'] = 1
                    request.meta['layer'] = current_layer + 1
                    if multi_page:
                        updated_path[-2] = count
                        updated_path[-1] = 1
                    else:
                        updated_path[-1] = count
                    request.meta['crawl_path'] = json.dumps(updated_path)
                    count += 1
                    yield request

def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'
    })

    process.crawl(MuriaeCrawler)
    process.start()

if __name__ == "__main__":
    main()
