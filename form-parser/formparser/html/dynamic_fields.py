# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Find dynamic fields in form
"""
from formparser import utils
from collections import defaultdict
from selenium.webdriver.support.ui import Select
import time


class DynamicFields:
    """Identify dynamic fields in web forms"""

    def __init__(self, url, form):
        """Constructor for DynamicFields

        Args:
            url (`str`): target url.
            form (`lxml.etree._Element`): target form.
        """
        self.browser = utils.open_driver(url)
        self.form_xpath = utils.get_xpath(form)
        self.form_text = self.get_text(self.form_xpath)
        self.dynamic_fields = defaultdict(list)

    def get_text(self, xpath) -> str:
        """Returns the text within a web element

        Args:
            xpath: xpath of the element
        """
        return self.browser.find_element_by_xpath(xpath).text

    def get_dynamic_fields(self, fields_dict):
        """Calls check_fields for each field type to be checked

        Args:
            fields_dict: {'str': [<lxml.etree._Element>]}
        """
        field_types = fields_dict.keys()
        for field_type in field_types:
            self.check_fields(fields_dict[field_type], field_type)

    def check_fields(self, field_list, field_type):
        """Triggers field changes and detect dynamic fields

        Args:
            field_list: 'lxml.etree._Element'
            field_type: str
        """
        for field in field_list:
            xpath = utils.get_xpath(field)
            element = self.browser.find_element_by_xpath(xpath)
            if not element.is_displayed():
                continue
            text_before_click = self.get_text(self.form_xpath)
            if field_type == 'select':
                self.change_select_field(element)
            else:
                element.click()
            time.sleep(0.5)
            self.check_change(text_before_click, field, field_type)
            self.browser.refresh()

    def check_change(self, text_before_action, field, field_type):
        """Detects if text changed after action and fills dict with fields

        Args:
            text_before_action: url of webpage where the form is (if not
                                provided when constructing the object
                                HTMLParser)
            field: 'lxml.etree._Element'
            field_type: str
        """
        if text_before_action != self.get_text(self.form_xpath):
            self.dynamic_fields[field_type].append(field)

    @staticmethod
    def change_select_field(element):
        """Selects second option in a select field by index

        Args:
            element: Select element
        """
        select = Select(element)
        select.select_by_index(1)
