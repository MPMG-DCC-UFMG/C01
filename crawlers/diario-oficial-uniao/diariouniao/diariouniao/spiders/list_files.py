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

import json

import pandas # for date_range

class SeleniumSpider(scrapy.Spider):
    name = 'list_files'    

    def __init__(self, *a, **kw):
        super(SeleniumSpider, self).__init__(*a, **kw)

    # def file_exists(file_name):
    #     try:
    #         with open(file_name) as f:
    #             pass
    #     except FileNotFoundError:
    #         return False
    #     return True

    def gen_base_url(self):
        today = datetime.datetime.today()

        # for date in pandas.date_range("2020-05-02", today.strftime('%Y-%m-%d')):
        # for date in pandas.date_range("2014-01-01", today.strftime('%Y-%m-%d')):
        for date in pandas.date_range("2014-01-01", "2020-05-15"):
            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At gen_base_url")
            url = f"http://www.in.gov.br/leiturajornal?data={date.strftime('%d-%m-%Y')}#daypicker"
            metadata = {"date": date.strftime('%Y-%m-%d')}

            yield (url, metadata)

    def next_call(self, gen):
        self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At next_call")
        try:
            url, metadata = next(gen)
            metadata["generator"] = gen
            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Calling {url}")
            return SeleniumRequest(url=url, meta=metadata, callback=self.parse, dont_filter=True)
        except StopIteration:
            return []

    def start_requests(self):   
        gen = self.gen_base_url()
        yield self.next_call(gen)

    def parse(self, response):
        self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At parser")
        driver = response.request.meta['driver']
        date = response.request.meta['date']

        list_files = open("list_of_files.txt", "a+")

        if self.move_to_document_list(driver) and self.there_is_documents(driver, date):
            table_rows = self.get_document_table(driver)
            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {date} - No. of rows: {len(table_rows)}")

            for tr in table_rows:
                anchor = tr.find_element_by_xpath("td[1]/a")
                link = anchor.get_attribute("onclick")
                args = {"date": date}

                for i in link.split('?')[1][:-3].split('&'):
                    key, value = i.split('=')
                    args[key] = value

                args["file_name"] = f"{date}_{args['jornal']}.pdf" 
                list_files.write(json.dumps(args) + "\n")

                # for p in range(int(args['totalArquivos'])):
                #     url = f"http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={args['jornal']}" \
                #         f"&pagina={p + 1}&data={args['data']}&captchafield=firstAccess"
                #     url_data = args.copy()

                #     url_data["pagina"] = str(p + 1)
                    
                #     self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> spawning {url_data} {url}")
                #     yield scrapy.Request(
                #         url=url, callback=self.save_page, meta=url_data,
                #         priority=1 # min(1, 1000 - int(args['totalArquivos'])) # give priority to shorter documents
                #     ) 
        
        list_files.close()
        yield self.next_call(response.request.meta['generator'])        

    def wait_element(self, driver, xpath):
        attempt = 1
        while attempt <= 8:
            try:
                driver.find_element_by_xpath(xpath)
                return True
            except NoSuchElementException:
                attempt += 1
                time.sleep(1)
        self.logger.info("Unable to locate element at " + xpath)
        return False

    def move_to_document_list(self, driver):
        full_btn_xpath = "//div[1]/div[2]/main/div[2]/section/div/div/div/div/div[4]/section/" \
        "div/div[2]/div/div[1]/div[3]/button[4]"

        if not self.wait_element(driver, full_btn_xpath):
            return False

        driver.find_element_by_xpath(full_btn_xpath).click()
        return True

    def there_is_documents(self, driver, date):
        if not self.wait_element(driver, "//div/form/center"):
            return False

        center = driver.find_element_by_xpath("//div/form/center")

        self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {date} TEXT - " + center.text)
        if center.text == "Nenhum registro encontrado para a pesquisa.":            
            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {date} - No documents for date")
            return False            
        
        return True

    def get_document_table(self, driver):
        time.sleep(2) # making sure the table is filled before checking
        table_rows_xpath = "//*[@id=\"ResultadoConsulta\"]/tbody/tr"
        if not self.wait_element(driver, table_rows_xpath):
            return []
        table_rows = driver.find_elements_by_xpath(table_rows_xpath)
        return table_rows

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
