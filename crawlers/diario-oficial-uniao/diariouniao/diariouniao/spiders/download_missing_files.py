import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import logging
import os
import re
import time
import datetime
from shutil import which

from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 

from PyPDF2.utils import PdfReadError
from PyPDF2 import PdfFileReader

import pandas # for date_range
import json

class SeleniumSpider(scrapy.Spider):
    name = 'download_missing_files'    

    def __init__(self, *a, **kw):
        super(SeleniumSpider, self).__init__(*a, **kw)

    def start_requests(self):   
        files = {}

        with open("list_of_files.txt", "r") as f:
            file_names = {}
            with open("list_of_files.txt", "r") as f:
                for line in f:
                    f_dict = json.loads(line)
                    file_names[f_dict["file_name"]] = f_dict

            files_downloaded = []
            for f in os.listdir("jornais-completos"):
                files_downloaded.append(f)
            files_downloaded = set(files_downloaded)

            for f in file_names:
                if f not in files_downloaded:
                    for p in range(int(file_names[f]['totalArquivos'])):
                        url_data = file_names[f].copy()
                        url = f"http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={url_data['jornal']}" \
                            f"&pagina={p + 1}&data={url_data['data']}&captchafield=firstAccess"

                        url_data["pagina"] = str(p + 1)
                        
                        self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> spawning {url_data} {url}")
                        yield scrapy.Request(
                            url=url, callback=self.save_page, meta=url_data,
                            priority=1 # min(1, 1000 - int(args['totalArquivos'])) # give priority to shorter documents
                        ) 

    def save_page(self, response):
        metadata = response.request.meta
        self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At save_page {metadata}")
        metadata["data"] = metadata["data"].replace("/", "-")
        name = "jornais/" + "_".join([
            metadata["date"],
            metadata["jornal"], 
            "%04d" % (int(metadata["totalArquivos"])),
            "%04d" % (int(metadata["pagina"]))
        ]) + ".pdf"
        with open(name, "wb") as f:
            f.write(response.body)

# c = CrawlerProcess({
#     'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},
#     'SELENIUM_DRIVER_NAME': 'chrome',
#     'SELENIUM_DRIVER_EXECUTABLE_PATH': which("../chromedriver_win32_chr_81.exe"),
#     'SELENIUM_DRIVER_ARGUMENTS': [],
#     # 'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],  # '--headle   ss' if using chrome instead of firefox,
#     'DOWNLOADER_MIDDLEWARES': {'scrapy_selenium.SeleniumMiddleware': 800},
# })
# c.crawl(SeleniumSpider)
# c.start()
