# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Utils for formparser module
"""
import random
import logging
from selenium.webdriver.support.ui import Select
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
import time

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]

FILLERS = {'date': '2014-01-01',
           'search': 'aaa',
           'numeric': 20,
           'text': 'aaa',
           'select': 1}


def request_headers():
    """Build request headers

    Returns:
        Dictionary containing headers
    """
    user_agent = random.choice(USER_AGENT_LIST)
    return {'User-Agent': user_agent}


def set_options():
    """Configures webdriver options

    Returns:
        FirefoxOptions object
    """
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=1920x1080")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--verbose')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    return firefox_options


def open_driver(url, driver_options=set_options()):
    driver = webdriver.Firefox(options=driver_options)
    driver.get(url)
    time.sleep(5)
    return driver


def set_logging():
    """Set logging options"""
    logging.basicConfig(level=logging.INFO)


def get_xpath(element) -> str:
    """Returns an element's xpath.

    Args:
        element: 'lxml.etree._Element'

    Returns:
        element's xpath
    """
    return element.getroottree().getpath(element)


def probing(browser, element="Não há resultado para a pesquisa.") -> bool:
    """Webpage probing to check for a particular element
    TODO: Replace by probing module

    Returns:
        True, if element is found. False, otherwise.
    """
    return element.lower() in str(browser.find_element_by_tag_name('body').text).lower()
