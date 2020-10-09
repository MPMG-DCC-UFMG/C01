# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Utils for formparser module
"""
import random
import logging
import collections
import entry_probing
import asyncio

from syncer import sync

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 '
    '(KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]

FILLERS = {'date': '2014-01-01',
           'search': 'aaa',
           'numeric': 20,
           'text': 'aaa',
           'select': 1}

FORM_TAGS = ['input', 'textarea', 'button', 'select', 'option',
             'optgroup', 'fieldset', 'output']


def request_headers():
    """Build request headers

    Returns:
        Dictionary containing headers
    """
    user_agent = random.choice(USER_AGENT_LIST)
    return {'User-Agent': user_agent}


def set_logging():
    """Set logging options"""
    logging.basicConfig(level=logging.INFO)


def get_xpath(element) -> str:
    """Returns an element's xpath

    Args:
        element: 'lxml.etree._Element'

    Returns:
        element's xpath
    """
    return element.getroottree().getpath(element)

@sync
async def probing(page, probing_element="Não há resultado para a pesquisa.")\
        -> bool:
    """Webpage probing to check for a particular element

    Returns:
        True, if element is found. False, otherwise.
    """
    if isinstance(probing_element, str):
        return probing_element.lower() in str(get_page_text(page)).lower()
    elif isinstance(probing_element, entry_probing.EntryProbing):
        return await probing_element.async_check_entry()


@sync
async def get_page_text(page) -> str:
    return await page.plainText()


def to_xpath(data_structure):
    """Converts an lxml.etree._Element data structure to the corresponding
    xpath structure
    Example:
        Input: [<Element input at 0x108277c30>, <Element input at 0x108277a50>]
        Output: ['/html/body/div[2]/div/div/form/input[1]',
        '/html/body/div[2]/div/div/form/input[2]']

    Args:
        data_structure: elements to be converted to xpath. Can be list,
        dictionary or single element.

    Returns:
        Data structure with xpaths instead of lxml.etree._Element instances
    """
    type_ = type(data_structure)
    if type_ is list:
        return list_to_xpath(data_structure)
    elif type_ is dict or isinstance(type_, collections.defaultdict):
        return dict_to_xpath(data_structure)
    else:
        return get_xpath_safe(data_structure)


def list_to_xpath(element_list: list):
    """Converts lxml.etree._Element in a list to an xpath list

    Args:
        element_list: list of elements to be converted to xpath

    Returns:
        List of xpaths
    """
    return list(map(lambda x: get_xpath_safe(x), element_list))


def dict_to_xpath(element_dict: dict):
    """Converts an lxml.etree._Element dict to an xpath list

    Args:
        element_dict: dict with elements to be converted to xpath

    Returns:
        Dictionary with elements' xpaths
    """
    keys_xpath = list_to_xpath(list(element_dict.keys()))
    values_xpath = []
    for value in element_dict.values():
        values_xpath.append(list_to_xpath(list(value)))
    return dict(zip(keys_xpath, values_xpath))


def get_xpath_safe(element) -> str:
    """Returns an element's xpath, returns the same element in case the
    xpath cannot be obtained

    Args:
        element: 'lxml.etree._Element'

    Returns:
        element's xpath
    """
    try:
        return element.getroottree().getpath(element)
    except AttributeError:
        logging.error('AttributeError: returning unchanged element')
        return element


@sync
async def check_for_alert(page):
    async def close_dialog(dialog):
        await dialog.dismiss()

    await page.on(
        'dialog',
        lambda dialog: asyncio.ensure_future(close_dialog(dialog))
    )
