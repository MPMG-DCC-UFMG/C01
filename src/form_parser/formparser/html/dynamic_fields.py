# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Find dynamic fields in form
"""
import logging
import time

from syncer import sync
from formparser import utils
from collections import defaultdict
from pyppeteer import launch


class DynamicFields:
    """Identify dynamic fields in web forms"""

    def __init__(self, url: str, form):
        """Constructor for DynamicFields

        Args:
            url (`str`): target url.
            form (`lxml.etree._Element`): target form.
        """
        self.url = url
        self.form_xpath = utils.get_xpath(form)

        self.page = self.get_page()

        self.form_text = self.get_text(xpath=self.form_xpath)
        self.dynamic_fields = defaultdict(list)

    @sync
    async def get_page(self):
        """Returns loaded page"""
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(self.url)
        await page.waitForXPath(self.form_xpath)
        return page

    @sync
    async def get_text(self, xpath: str) -> str:
        """Returns the text within a web element

        Args:
            xpath: xpath of the element
        """
        element = await self.page.xpath(xpath)

        if isinstance(element, list):
            element = element[0]

        return await self.page.evaluate('''element => element.textContent''',
                                        element)

    @sync
    async def is_enabled(self, element) -> bool:
        """Returns whether the element is enabled or not

        Args:
            element: pyppeteer webelement
        """
        return await self.page.evaluate(
            """element => {
                return element.disabled;
            }""",
            element
        )

    @sync
    async def is_displayed(self, xpath: str, timeout=30) -> bool:
        """Returns whether the element is displayed or not

        Args:
            xpath: element xpath
            timeout: (int|float) time to wait in miliseconds
        """
        try:
            await self.page.waitForXpath(xpath,
                                         options={'visible': True,
                                                  'timeout': timeout})
            return True
        except TimeoutError:
            return False

    @sync
    async def get_current_url(self):
        """Returns current url"""
        return await self.page.url

    def get_dynamic_fields(self, fields_dict):
        """Calls check_fields for each field type to be checked

        Args:
            fields_dict: {'field1_xpath': ['field2_xpath', 'field3_xpath']}
        """
        field_types = fields_dict.keys()
        for field_type in field_types:
            self.check_fields(fields_dict[field_type], field_type)

    def check_fields(self, field_list: list, field_type: str, sleep_time=0.5):
        """Triggers field changes and detect dynamic fields

        Args:
            sleep_time:
            field_list: ['lxml.etree._Element']
            field_type: str
        """
        for field in field_list:
            xpath = utils.get_xpath(field)
            element = self.element_from_xpath(xpath)
            if not self.is_displayed(xpath):
                continue
            status_before_change = self.get_status(field_list=field_list)
            text_before_change = self.get_text(xpath=self.form_xpath)
            if field_type == 'select':
                self.change_select_field(element)
            else:
                self.click(element)

            time.sleep(sleep_time)
            status_after_change = self.get_status(field_list=field_list)
            changed_fields = self.dictionary_diff(status_before_change,
                                                  status_after_change)
            self.check_changed_fields(changed_fields, xpath,
                                      text_before_change)
            self.page_reload()

    @sync
    async def element_from_xpath(self, xpath):
        """Find element in page using xpath

        Args:
            xpath: target xpath
        """
        element = await self.page.xpath(xpath)
        if isinstance(element, list):
            return element[0]
        else:
            return element

    @sync
    async def click(self, element):
        """Click on element

        Args:
            element: pyppeteer element
        """
        await element.click()

    @sync
    async def change_select_field(self, element, wait_for=30):
        """Selects first option from select field

        Args:
            element: pyppeteer element
            wait_for: time to wait while element loads
        """
        await element.click()
        await self.page.waitFor(wait_for)
        await self.page.keyboard.press('ArrowDown')
        await self.page.keyboard.press('Enter')

    @sync
    async def page_reload(self):
        """Reloads current webpage"""
        await self.page.reload()

    def check_changed_fields(self, changed_fields: list, xpath: str,
                             text_before_change: str):
        """Check which fields changed after modifying a form field

        Args:
            changed_fields: list of fields that were changed
            xpath: xpath of element that triggered change
            text_before_change: string containing target text before change
        """
        if len(changed_fields) > 0:
            for changed_field in changed_fields:
                self.dynamic_fields[xpath].append(changed_field)
        elif self.check_text_change(text_before_change):
            self.dynamic_fields[xpath].append('')

    def check_text_change(self, text_before_action: str) -> bool:
        """Detects if text changed after action and fills dict with fields

        Args:
            text_before_action: text extracted from page before performing
                                an action

        Returns
            True, if text changes.
        """
        return text_before_action != self.get_text(xpath=self.form_xpath)

    @sync
    async def get_status(self, field_list: list,
                         attribute='is_displayed') -> dict:
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
            element = await self.page.xpath(xpath)
            if attribute == 'is_displayed':
                status[xpath] = self.is_displayed(xpath)
            elif attribute == 'is_enabled':
                status[xpath] = self.is_enabled(element)
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
