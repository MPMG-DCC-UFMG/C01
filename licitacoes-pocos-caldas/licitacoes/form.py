"""
Rúbia Reis Guerra
rubia-rg@github
Fills 'Licitaçoes' search form at https://pocosdecaldas.mg.gov.br/
"""
import time
import logging

from licitacoes import config, utils
from selenium.common import exceptions


class SearchForm:
    def __init__(self, sort_button=config.SORT_BUTTON, max_results_field=config.MAX_RESULTS_FIELD,
                 submit_button=config.SUBMIT_BUTTON):
        self.sort_button = sort_button
        self.max_results_field = max_results_field
        self.submit_button = submit_button

    def sort_results(self, driver):
        try:
            driver.find_element_by_xpath(self.sort_button).click()
        except exceptions.NoSuchElementException:
            time.sleep(5)
            try:
                driver.find_element_by_xpath(self.sort_button).click()
            except exceptions.NoSuchElementException:
                logging.error('Website has not loaded properly')
        except exceptions.ElementClickInterceptedException:
            element = driver.find_element_by_xpath(self.sort_button).click()
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()

    def set_max_displayed_results(self, driver):
        driver.find_element_by_xpath(self.max_results_field).clear()
        driver.find_element_by_xpath(self.max_results_field).send_keys(config.MAX_PROCESSES)

    def submit_results(self, driver):
        submit_button = driver.find_element_by_xpath(self.submit_button)
        submit_button.click()

    def fill_form(self, driver):
        self.sort_results(driver)
        self.set_max_displayed_results(driver)
        self.submit_results(driver)
        utils.wait_page_load(driver, element_xpath=config.FIRST_RESULT, delay=config.WEBDRIVER_DELAY)
        return driver
