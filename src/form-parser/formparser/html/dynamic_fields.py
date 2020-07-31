# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Find dynamic fields in form
"""
import logging
import time

from formparser import utils
from collections import defaultdict
from selenium.webdriver.support.ui import Select
from selenium.common import exceptions
from formparser import html


class DynamicFields:
    """Identify dynamic fields in web forms"""

    def __init__(self, url, form):
        """Constructor for DynamicFields

        Args:
            url (`str`): target url.
            form (`lxml.etree._Element`): target form.
        """
        self.driver = utils.open_driver(url)
        self.form_xpath = utils.get_xpath(form)
        self.form_text = self.get_text(self.form_xpath)
        self.dynamic_fields = defaultdict(list)

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def get_text(self, xpath) -> str:
        """Returns the text within a web element

        Args:
            xpath: xpath of the element
        """
        return self.driver.find_element_by_xpath(xpath).text

    def get_dynamic_fields(self, fields_dict):
        """Calls check_fields for each field type to be checked

        Args:
            fields_dict: {'field1_xpath': ['field2_xpath', 'field3_xpath']}
        """
        field_types = fields_dict.keys()
        for field_type in field_types:
            self.check_fields(fields_dict[field_type], field_type)

    def check_fields(self, field_list, field_type, sleep_time=0.5):
        """Triggers field changes and detect dynamic fields

        Args:
            sleep_time:
            field_list: ['lxml.etree._Element']
            field_type: str
        """
        for field in field_list:
            xpath = utils.get_xpath(field)
            element = self.driver.find_element_by_xpath(xpath)
            if not element.is_displayed():
                continue
            status_before_change = self.get_status(field_list)
            text_before_change = self.get_text(self.form_xpath)
            if field_type == 'select':
                self.change_select_field(element)
            else:
                element.click()
            time.sleep(sleep_time)
            status_after_change = self.get_status(field_list)
            changed_fields = self.dictionary_diff(status_before_change,
                                                  status_after_change)
            if len(changed_fields) > 0:
                for changed_field in changed_fields:
                    self.dynamic_fields[xpath].append(changed_field)
            elif self.check_text_change(text_before_change):
                self.dynamic_fields[xpath].append('')
            self.driver.refresh()

    @staticmethod
    def change_select_field(element):
        """Selects second option in a select field by index

        Args:
            element: Select element
        """
        select = Select(element)
        select.select_by_index(1)

    def check_text_change(self, text_before_action) -> bool:
        """Detects if text changed after action and fills dict with fields

        Args:
            text_before_action: url of webpage where the form is (if not
                                provided when constructing the object
                                HTMLParser)
            field: 'lxml.etree._Element'
            field_type: str

        Returns
            True, if text changes.
        """
        try:
            return text_before_action != self.get_text(self.form_xpath)

        except exceptions.StaleElementReferenceException:
            form = html.HTMLParser(url=self.driver.current_url)
            self.form_xpath = utils.get_xpath(form)
            return text_before_action != self.get_text(self.form_xpath)

    def get_status(self, field_list, attribute='is_displayed') -> dict:
        """Checks status of a web element

        Args:
            field_list: List of elements to check visibility
            attribute: type of attribute to check. Can be either 'is_displayed'
            or 'is_enabled'

        Returns:
            Dictionary of the form {'field_xpath': status}
        """
        status = {}
        for field in field_list:
            xpath = utils.get_xpath(field)
            element = self.driver.find_element_by_xpath(xpath)
            if attribute == 'is_displayed':
                status[xpath] = element.is_displayed()
            elif attribute == 'is_enabled':
                status[xpath] = element.is_enabled()
            else:
                logging.error('[ERROR] InvalidAttribute: method not '
                              'implemented.')
        return status

    @staticmethod
    def dictionary_diff(dict1, dict2) -> list:
        """Compares two dictionaries and return keys with different values

        Args:
            dict1: first dictionary
            dict2: second dictionary

        Returns:
            List of different keys
        """
        diff = [x for x in dict2.keys() if x not in set(dict1.keys())]
        for key in dict1.keys():
            try:
                if dict1[key] != dict2[key]:
                    diff.append(key)
            except KeyError:
                continue
        return diff
