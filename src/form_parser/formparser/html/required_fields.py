# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Find required fields in form
"""
import logging

from formparser import utils
from multiprocessing import Pool, cpu_count
from pyppeteer import launch
from syncer import sync


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

    @sync
    async def get_page(self):
        """Wrapper for async get page"""
        browser = await launch(headless=True, dumpio=True)
        page = await browser.newPage()
        await page.goto(self.url)
        return page

    @sync
    async def page_wait(self, page, xpath=None, time_to_wait=30):
        """Wrapper for async page wait"""
        if xpath:
            await page.waitForXpath(xpath, {'timeout': time_to_wait})
        else:
            await page.waitFor(time_to_wait)

    @sync
    async def page_close(self, page):
        """Wrapper for async page close"""
        await page.close()

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

        page = self.get_page()
        self.page_wait(page, xpath=submit_button_xpath, time_to_wait=30)

        self.submit_clear(page, submit_button_xpath)
        if utils.probing(page, probing_element):
            self.page_close(page)
        else:
            self.parallel_search(fields, submit_button_xpath,
                                 probing_element, include_hidden)

    def submit_clear(self, page, submit_button_xpath: str, time_to_wait=5):
        """Submits a form without filling fields"""
        submit_button = self.element_from_xpath(page, submit_button_xpath)
        self.click(submit_button)
        self.page_wait(page, time_to_wait=time_to_wait)

    def parallel_search(self, fields: list, submit_button_xpath: str,
                        probing_element, include_hidden: bool):
        """Parallel search for required fields

        Args:
            submit_button_xpath: xpath to form's submit button
            fields: list of form fields
            probing_element: element to look for in page after submitting
            the form, check entry_probing module for details
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

    @sync
    async def is_displayed(self, page, xpath: str, timeout=30) -> bool:
        """Returns whether the element is displayed or not

        Args:
            page: pyppeteer page
            xpath: element xpath
            timeout: (int|float) time to wait in miliseconds
        """
        try:
            await page.waitForXpath(xpath, options={'visible': True,
                                                    'timeout': timeout})
            return True
        except TimeoutError:
            return False

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
            the form, check entry_probing module for details
            index: index of field to skip while submitting the form
            include_hidden: if true, processes fields that are not displayed
        """
        fields_copy = fields.copy()
        target_field = fields_copy[index]
        if target_field not in self.required_fields:
            del fields_copy[index]
            del types[index]
            page = self.get_page()
            self.page_wait(page, submit_button_xpath)

            if include_hidden or self.is_displayed(target_field):
                self.submit_filled_form(page, fields_copy, types,
                                        submit_button_xpath,
                                        include_hidden)

                probing_response = utils.probing(page, probing_element)

                if probing_response:
                    if not fields[index] in self.required_fields:
                        self.required_fields.append(fields[index])
            page.quit()

    def submit_filled_form(self, page, fields: list, types: list,
                           submit_button_xpath: str, include_hidden: bool,
                           time_to_wait=5):
        """Submits a form with filled fields"""
        for xpath, field_type in zip(fields, types):
            if field_type in "submit":
                continue
            if field_type in 'select':
                select = self.element_from_xpath(xpath)
                self.change_select_field(page, select, include_hidden, xpath)
            elif field_type in list(self.fillers.keys()):
                filler = self.fillers[field_type]
                self.fill(page, xpath, filler, field_type, page,
                          include_hidden)
            else:
                logging.info("[WARNING] Type not supported: " + field_type +
                             " Skipping.")
                continue

        submit_button = self.element_from_xpath(page, submit_button_xpath)
        self.click(submit_button)
        self.page_wait(page, time_to_wait=time_to_wait)

    @staticmethod
    def get_type(element):
        """Get field type from html tag"""
        if isinstance(element, str):
            return element
        if element.tag in 'input':
            return element.attrib['type']
        else:
            return element.tag

    def fill(self, page, xpath: str, filler: str, type_: str,
             include_hidden: bool):
        """Fills a field with specified content"""
        if include_hidden:
            self.element_type_text(page, xpath, "")
            self.element_type_text(page, xpath, filler)
        else:
            if self.is_displayed(page, xpath):
                self.element_type_text(page, xpath, "")
                self.element_type_text(page, xpath, filler)
                self.check_for_alerts(page, include_hidden, xpath, type_)

    def check_for_alerts(self, page, include_hidden: bool, xpath=None,
                         type_=None):
        """Treat JavaScript alerts when filling out form"""
        utils.check_for_alert(page)
        if type_ == 'text' and xpath is not None:
            self.fill(page, xpath, '001', type_, include_hidden)
        else:
            if xpath is not None:
                logging.info('[WARNING] Could not fill field at xpath ' +
                             xpath)
            else:
                logging.info('[WARNING] A JavaScript alert could not be '
                             'treated.')

    @sync
    async def click(self, element):
        """Click on element

        Args:
            element: pyppeteer element
        """
        await element.click()

    @sync
    async def change_select_field(self, page, element, include_hidden: bool,
                                  xpath: str, wait_for=30):
        """Selects first option from select field

        Args:
            element: pyppeteer element
            wait_for: time to wait while element loads
            page: pyppeteer page
            include_hidden: whether to include hidden fields or not
            xpath: field xpath
        """
        if include_hidden:
            await element.click()
            await page.waitFor(wait_for)
            await page.keyboard.press('ArrowDown')
            await page.keyboard.press('Enter')
        else:
            if self.is_displayed(page, xpath):
                await element.click()
                await page.waitFor(wait_for)
                await page.keyboard.press('ArrowDown')
                await page.keyboard.press('Enter')

    @sync
    async def element_from_xpath(self, page, xpath: str):
        """Wrapper for async get element from xpath"""
        element = await page.xpath(xpath)
        try:
            return element[0]
        except IndexError:
            return element

    @sync
    async def element_type_text(self, page, xpath: str, text: str):
        """Wrapper for async fill text input"""
        element = self.element_from_xpath(page, xpath)
        await element.type(text)
