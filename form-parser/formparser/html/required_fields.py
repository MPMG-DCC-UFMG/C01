# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Find required fields in form
"""
import logging

from formparser import utils
from multiprocessing import Pool, cpu_count
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class RequiredFields:
    """Identify required fields in web forms"""

    def __init__(self, url: str, fillers):
        """Constructor for RequiredFields

        Args:
            url (`str`): target url.
            fillers (`dict`): dictionary of field types and values use as
            fillers for testing
        """
        self.url = url
        self.required_fields = list()
        self.fillers = fillers

    def get_required_fields(self, fields: list, submit_button_xpath: str,
                            probing_element, tagged_fields=None,
                            include_hidden=False):
        """Checks form required fields by two strategies. First, check for
        tagged HTML input fields. Then, try a parallel leave-one-out form
        submission strategy.

        Args:
            submit_button_xpath: xpath to form's submit button
            fields: list of form fields
            probing_element: element to look for in page after submitting
            the form
            tagged_fields: list of HTML fields with the 'required' tag
            include_hidden: if True, processes fields that are not displayed
        """
        if tagged_fields is not None:
            tagged_fields_xpath = utils.to_xpath(tagged_fields)
            self.required_fields = tagged_fields_xpath

        browser = utils.open_driver(self.url)
        wait = WebDriverWait(browser, 3)
        wait.until(ec.visibility_of_element_located((By.XPATH,
                                                     submit_button_xpath)))
        try:
            self.submit_clear(browser, submit_button_xpath)
            if utils.probing(browser, probing_element):
                browser.quit()
            else:
                self.parallel_search(fields, submit_button_xpath,
                                     probing_element, include_hidden)
        except exceptions.UnexpectedAlertPresentException:
            utils.check_for_alert(browser)
            browser.quit()
            self.parallel_search(fields, submit_button_xpath,
                                 probing_element, include_hidden)

    @staticmethod
    def submit_clear(browser, submit_button_xpath: str, browser_wait=0.5):
        """Submits a form without filling fields"""
        submit_button = browser.find_element_by_xpath(submit_button_xpath)
        try:
            submit_button.click()
        except exceptions.ElementClickInterceptedException:
            browser.execute_script("arguments[0].scrollIntoView();",
                                   submit_button)
            submit_button.click()
        browser.implicitly_wait(browser_wait)

    def parallel_search(self, fields: list, submit_button_xpath: str,
                        probing_element, include_hidden: bool):
        """Parallel search for required fields

        Args:
            submit_button_xpath: xpath to form's submit button
            fields: list of form fields
            probing_element: element to look for in page after submitting
            the form
            include_hidden: if true, processes fields that are not displayed
        """
        fields_xpath = utils.to_xpath(fields)
        types = [self.get_type(element) for element in fields]
        if len(fields_xpath) > len(types):
            logging.info('[WARNING] Length of fields list is different from '
                         'length of types list.')
        args = [(fields_xpath, types, submit_button_xpath, probing_element,
                 index, include_hidden) for index in range(len(fields))]
        pool = Pool(cpu_count())
        pool.map(self.wrapped_check_fields, args)

    def wrapped_check_fields(self, args):
        """Auxiliary function to unwrap arguments for parallel execution

            Args:
                args: self.check_field's arguments
        """
        self.check_fields(*args)

    def check_fields(self, fields: list, types: list, submit_button_xpath: str,
                     probing_element, index: int, include_hidden: bool):
        """Leave-one-out search of required fields

        Args:
            submit_button_xpath: xpath to form's submit button
            fields: list of form fields
            types: list of form fields types
            probing_element: element to look for in page after submitting
            the form
            index: index of field to skip while submitting the form
            include_hidden: if true, processes fields that are not displayed
        """
        fields_copy = fields.copy()
        target_field = fields_copy[index]
        if target_field not in self.required_fields:
            del fields_copy[index]
            del types[index]
            browser = utils.open_driver(self.url)
            wait = WebDriverWait(browser, 3)
            wait.until(ec.visibility_of_element_located((By.XPATH,
                                                         submit_button_xpath)))
            if include_hidden or browser.find_element_by_xpath(
                    target_field).is_displayed():
                self.submit_filled_form(browser, fields_copy, types,
                                        submit_button_xpath,
                                        include_hidden)
                try:
                    probing_response = utils.probing(browser, probing_element)
                except exceptions.UnexpectedAlertPresentException:
                    probing_response = True
                    utils.check_for_alert(browser)
                if probing_response:
                    if not fields[index] in self.required_fields:
                        self.required_fields.append(fields[index])
            browser.quit()

    def submit_filled_form(self, browser, fields: list, types: list,
                           submit_button_xpath: str, include_hidden: bool,
                           browser_wait=0.5):
        """Submits a form with filled fields"""
        for xpath, field_type in zip(fields, types):
            if field_type in "submit":
                continue
            if field_type in 'select':
                select = browser.find_element_by_xpath(xpath)
                utils.change_select_field(select, include_hidden)
            elif field_type in list(self.fillers.keys()):
                filler = self.fillers[field_type]
                self.fill(xpath, filler, field_type, browser, include_hidden)
            else:
                logging.info("[WARNING] Type not supported: " + field_type +
                             " Skipping.")
                continue
        submit_button = browser.find_element_by_xpath(submit_button_xpath)
        browser.execute_script("arguments[0].scrollIntoView();",
                               submit_button)
        submit_button.click()
        browser.implicitly_wait(browser_wait)

    @staticmethod
    def get_type(element):
        if isinstance(element, str):
            return element
        if element.tag in 'input':
            return element.attrib['type']
        else:
            return element.tag

    def fill(self, xpath: str, filler: str, type_: str, browser,
             include_hidden: bool):
        """Fills a field with specified content"""
        if include_hidden:
            browser.find_element_by_xpath(xpath).clear()
            browser.find_element_by_xpath(xpath).send_keys(filler)
            self.check_for_alerts(browser, include_hidden, xpath, type_)
        else:
            if browser.find_element_by_xpath(xpath).is_displayed():
                browser.find_element_by_xpath(xpath).clear()
                browser.find_element_by_xpath(xpath).send_keys(filler)
                self.check_for_alerts(browser, include_hidden, xpath, type_)

    def check_for_alerts(self, browser, include_hidden: bool, xpath=None,
                         type_=None):
        """Treat JavaScript alerts when filling out form"""
        if utils.check_for_alert(browser):
            if type_ == 'text' and xpath is not None:
                self.fill(xpath, '001', type_, browser, include_hidden)
            else:
                if xpath is not None:
                    logging.info('[WARNING] Could not fill field at xpath ' +
                                 xpath)
                else:
                    logging.info('[WARNING] A JavaScript alert could not be '
                                 'treated.')
