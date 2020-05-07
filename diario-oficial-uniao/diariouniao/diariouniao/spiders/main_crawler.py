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

class SeleniumSpider(scrapy.Spider):
    name = 'main_crawler'    

    def __init__(self, *a, **kw):
        super(SeleniumSpider, self).__init__(*a, **kw)

    def save_page(self, response):
        metadata = response.request.meta
        metadata["data"] = metadata["data"].replace("/", "-")
        name = "jornais/" + "_".join([
            metadata["data"], metadata["jornal"], 
            metadata["totalArquivos"], metadata["page"]]
        ) + ".pdf"
        with open(name, "wb") as f:
            f.write(response.body)

    def start_requests(self):
        today = datetime.datetime.today()

        # for date in pandas.date_range("2020-05-02", today.strftime('%Y-%m-%d')):
        for date in pandas.date_range("2014-01-01", today.strftime('%Y-%m-%d')):
            url = f"http://www.in.gov.br/leiturajornal?data={date.strftime('%d-%m-%Y')}#daypicker"
            metadata = {"date": date.strftime('%Y-%m-%d')}
            yield SeleniumRequest(url=url, meta=metadata, callback=self.parse, dont_filter=True)

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

    def parse(self, response):
        self.logger.info(str(response.request.meta.keys()))
        driver = response.request.meta['driver']

        full_btn_xpath = "//div[1]/div[2]/main/div[2]/section/div/div/div/div/div[4]/section/" \
        "div/div[2]/div/div[1]/div[3]/button[4]"

        if not self.wait_element(driver, full_btn_xpath):
            return {}
        driver.find_element_by_xpath(full_btn_xpath).click()

        if not self.wait_element(driver, "//div/form/center"):
            return {}
        center = driver.find_element_by_xpath("//div/form/center")

        if center.text == "Nenhum registro encontrado para a pesquisa.":
            self.logger.info(f">>>>> {response.request.meta['date']} - No documents for date")
            return {}

        table_rows_xpath = "//*[@id=\"ResultadoConsulta\"]/tbody/tr"
        if not self.wait_element(driver, table_rows_xpath):
            return {}
        table_rows = driver.find_elements_by_xpath(table_rows_xpath)

        self.logger.info(f">>>>> {response.request.meta['date']} - No. of rows: {len(table_rows)}")
        for tr in table_rows:
            anchor = tr.find_element_by_xpath("td[1]/a")
            link = anchor.get_attribute("onclick")
            args = {}

            for i in link.split('?')[1][:-3].split('&'):
                key, value = i.split('=')
                args[key] = value

            for p in range(int(args['totalArquivos'])):
                url = f"http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={args['jornal']}" \
                    f"&pagina={p + 1}&data={args['data']}&captchafield=firstAccess"
                
                url_data = args.copy()
                url_data["page"] = str(p + 1)
                yield scrapy.Request(url=url, callback=self.save_page, meta=url_data) 
                if p == 5:
                    break       
        return

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
