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
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select

from PyPDF2.utils import PdfReadError

import pandas
import unidecode

class SeleniumSpider(scrapy.Spider):
    name = 'main_crawler'    

    def __init__(self, *a, **kw):
        super(SeleniumSpider, self).__init__(*a, **kw)
        self.city_name_xpath = "//form/div[3]/section/div[1]/table/tbody/tr/td/span/div/table/tbody/tr[5]/td[3]/div/" \
            "div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/" \
            "tr/td/div/div/span[2]"

        self.month_name = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }

        self.org_name = {
            1: "Legislativo",
            2: "Executivo",
            3: "Município",
        }

        self.base_table_xpath = "//form/div[3]/section/div[1]/table/tbody/tr/td/span/div/table/tbody/tr[5]/td[3]/" \
            "div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[13]/td[2]/table/" \
            "tbody/tr/td/table/tbody/tr"

        self.tables = {
            "Despesa_Total_com_Pessoal": "[4]/td[3]/table",
            "Exclusoes_da_Despesa_Total_com_Pessoal": "[6]/td[3]/table",
            "APURAÇÃO_DO_CUMPRIMENTO_DO_LIMITE_LEGAL": "[8]/td[2]/table",
        }

        self.org_select = "ctl00_MainContent_RVRemoto_ctl04_ctl03_ddValue"
        self.month_select = "ctl00_MainContent_RVRemoto_ctl04_ctl07_ddValue"
        self.search_btn_id = "ctl00_MainContent_RVRemoto_ctl04_ctl00"

    def gen_base_url(self):
        codes = []
        with open("cod_cidade_ibge.txt", "r") as f:
            for code in f:
                codes.append(int(code))

        url = "https://reportviewer.tce.mg.gov.br/default.aspx?server=relatorios.tce.mg.gov.br&" \
            "relatorio=SICOM_Consulta%2fModulo_LRF%2fRelatoriosComuns%2fUC02-ConsultarDespesaPessoalPoder-RL&"

        with open("last_call.txt", "r") as f:
            last_call = int(f.read())

        i = 0
        count = len(codes)
        for code in codes:
            for year in range(2014, 2019):# 2020):
                if i >= last_call:
                    with open("last_call.txt", "w+") as f:
                        f.write(str(i))
                    
                    self.logger.info(
                        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Next: city {i} of {count} - year {year}"
                    )
                    yield  (url + f"municipioSelecionado={code}&exercicioSelecionado={year}", {"year": year})
                i += 1

    def next_call(self, gen):
        try:
            url, metadata = next(gen)
            metadata["generator"] = gen
            metadata["url"] = url
            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Calling {url}")
            return SeleniumRequest(url=url, meta=metadata, callback=self.parse, dont_filter=True)
        except StopIteration:
            pass

    def start_requests(self):   
        gen = self.gen_base_url()
        yield self.next_call(gen)

    def parse(self, response):
        driver = response.request.meta['driver']
        year = response.request.meta['year']
        base_url = response.request.meta['url']

        self.wait_element(driver, self.city_name_xpath)
        city = driver.find_element_by_xpath(self.city_name_xpath).text
        city = unidecode.unidecode(city.replace(" ", ""))

        self.wait_element(driver, el_id=self.month_select)
        select = Select(driver.find_element_by_id(self.month_select))
        if select.first_selected_option.text == "Envio Incompleto":
            self.export_error(city, driver, year, base_url)
        else:
            self.get_tables(city, driver, year, base_url)
        
        yield self.next_call(response.request.meta['generator'])        

    def export_error(self, city, driver, year, base_url):
        self.prepare_path(city, year)
        with open(f"tabelas_de_despesa/{city}/{year}/ERROR.log", "w+") as f:
            f.write("Um ou mais Órgãos está com envio incompleto no Período/Data Base/Exercício!!!\n")
            f.write(base_url)

    def get_tables(self, city, driver, year, base_url):
        for org in range(3, 0, -1):
            self.select_org(driver, str(org))
            time.sleep(1)

            self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At org {self.org_name[org]}")

            self.prepare_path(city, year, self.org_name[org])

            for month in range(1, 13):
                fname = f"tabelas_de_despesa/{city}/{year}/{self.org_name[org]}/{self.month_name[month]}-"
                
                self.wait_element(driver, el_id=self.month_select)
                select = Select(driver.find_element_by_id(self.month_select))
                try:
                    select.select_by_value(str(month))
                except NoSuchElementException:
                    for tid in self.tables:
                        self.logger.info(
                            f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Mes {self.month_name[month]} não existe"
                        )
                        with open(fname + tid + ".csv", "w+") as f:
                            f.write(f"Mes não existe\n{base_url}")
                    continue

                time.sleep(1)

                self.click_element(driver, self.search_btn_id)
                
                self.logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> At month {self.month_name[month]}")

                time.sleep(1)

                self.wait_results_to_load(driver, self.org_name[org], self.month_name[month])

                for tid in self.tables:
                    self.wait_element(driver, self.base_table_xpath + self.tables[tid])

                for tid in self.tables:
                    table_html = driver.find_element_by_xpath(
                        self.base_table_xpath + self.tables[tid]
                    ).get_attribute('outerHTML')
                    df = pandas.read_html(table_html)[0]
                    df.to_csv(fname + tid + ".csv", index=False)
                
                time.sleep(0.3)

    def click_element(self, driver, btn_id):
        attempt = 1
        while attempt <= 8:
            try:
                btn = driver.find_element_by_id(btn_id)
                btn.click()
                return True
            except StaleElementReferenceException:
                attempt += 1
                time.sleep(1)
        self.logger.info("Unable to get hold of element " + btn_id)
        return False        

    def select_org(self, driver, org):
        attempt = 1
        while attempt <= 8:
            try:
                select = Select(driver.find_element_by_id(self.org_select))
                select.select_by_value(org)
                return True
            except StaleElementReferenceException:
                attempt += 1
                time.sleep(1)
        self.logger.info("Unable to get hold of org select")
        return False        

    def prepare_path(self, city, year, org=None):
        self.create_folder(f"tabelas_de_despesa/{city}")
        self.create_folder(f"tabelas_de_despesa/{city}/{year}")
        if org is not None:
            self.create_folder(f"tabelas_de_despesa/{city}/{year}/{org}")

    def create_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    def wait_element(self, driver, xpath=None, el_id=None):
        attempt = 1
        while attempt <= 8:
            try:
                if xpath is not None:
                    driver.find_element_by_xpath(xpath)
                    return True
                elif el_id is not None:
                    driver.find_element_by_id(el_id)
                    return True
                else:
                    raise TypeError
            except NoSuchElementException:
                attempt += 1
                time.sleep(1)
        self.logger.info("Unable to locate element at " + str(xpath) + "-" + str(el_id))
        return False

    def wait_results_to_load(self, driver, target_org, target_month):
        info_path = "//form/div[3]/section/div[1]/table/tbody/tr/td/span/div/table/tbody/tr[5]/td[3]/div/div[1]/div/" \
            "table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[9]/td[3]/table/tbody/tr/td/div/" \
            "div/span"
        attempt = 0
        while attempt < 16:
            try:
                org_span = driver.find_element_by_xpath(info_path + "[3]")
                self.logger.debug(f"$$$$$$$$$$$$$ curr = <{org_span.text}> / target = <{target_org}>")
                if org_span.text == target_org:
                    month_span = driver.find_element_by_xpath(info_path + "[5]")    
                    self.logger.debug(f"$$$$$$$$$$$$$ curr = <{month_span.text}> / target = <{target_month}>")
                    if month_span.text == target_month:
                        return True
                        
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            attempt += 1
            time.sleep(1)
    
    def file_exists(self, file_name):
        try:
            with open(file_name) as f:
                pass
        except FileNotFoundError:
            return False
        return True
