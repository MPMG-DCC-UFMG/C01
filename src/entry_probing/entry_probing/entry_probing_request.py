"""
This module contains the classes which describe the requesting procedure for
the entry probing process
"""

from enum import Enum
from typing import Any, Dict, Hashable, List, Optional

import asyncio
import abc
import requests
import pyppeteer

from .entry_probing_response import ResponseData


class ProbingRequest():
    """
    Abstract parent class for request definitions. Child classes implement the
    process method, which can receive an entry identifier. It should send an
    appropriate request to the target's URL and return the response, as a
    ResponseData object.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self,
                url_entries,
                req_entries):
        """
        Abstract method: sends a request to the desired URL and returns the
        response
        :param url_entries: list of parameters to be inserted in the URL
        :param req_entries: dictionary of parameters to be inserted in the
                            request body
        """
        pass


class HTTPProbingRequest(ProbingRequest):
    """
    Description of an HTTP request with possible placeholders for data in the
    URL and in the request body
    """

    REQUEST_METHODS = {
        "GET": requests.get,
        "POST": requests.post
    }

    def __init__(self, url, method, req_data):
        """
        Constructor for the HTTP request handler.
        :param url:      URL to be requested, with possible placeholders for
                         entry parameters
        :param method:   HTTP method to use for the request
        :param req_data: dictionary of extra data to be sent in the request
                         body, if necessary
        """
        super().__init__()
        self.__url    = url
        self.__method = method.upper()
        self.__req_data = req_data if req_data is not None else {}

        if req_data is not None and not isinstance(req_data, dict):
            raise TypeError("Request data to be sent must be a dictionary")

        if self.__method not in self.REQUEST_METHODS:
            raise ValueError(f"HTTP method not supported: {method}")

    def process(self,
                url_entries,
                req_entries):
        """
        Sends an HTTP request to the desired URL, formmated according to the
        url_entries parameter. The entries in req_entries are included in the
        request body. Returns the response to this request.
        :param url_entries: list of parameters to be inserted in the URL
        :param req_entries: dictionary of parameters to be inserted in the
                            request body
        :returns: Response obtained from the HTTP request
        """

        # Formats the URL with the url_entries list
        formatted_url = self.__url
        if url_entries is not None and len(url_entries) > 0:
            formatted_url = self.__url.format(*url_entries)

        # Inserts required values in the request body
        for key in req_entries:
            self.__req_data[key] = req_entries[key]

        # Does the request with the supplied method
        resp = self.REQUEST_METHODS[self.__method](formatted_url,
                                                   data=self.__req_data)

        return ResponseData.create_from_requests(resp)


class PyppeteerProbingRequest(ProbingRequest):
    """
    Description of a request which consists of using the currently open page in
    Pyppeteer as the response. The process() method is defined as a coroutine
    so it can be properly integrated with the Pyppeteer driver.
    The desired page must be requested after the constructor is called and
    before the call to the process() method. IMPORTANT: The HTTP headers and
    status code are captured from the first response received by the Pyppeteer
    page after the constructor is called, but the text is collected from the
    page contents when the process() method is called. This may cause
    synchronization issues if multiple pages are requested in sequence between
    these calls (e.g.: it will analyse the response to the first page request,
    and the text contents of the last page).
    """

    def __intercept_response(self,
                             response):
        """
        Intercepts the response to the first request made by the Pyppeteer page
        configured in the constructor and stores it
        :param response: Response received by Pyppeteer
        """

        # Ignore all responses but the first
        if self.__response is None:
            self.__response = response

    def __init__(self,
                 page: pyppeteer.page.Page):
        """
        Constructor for the Pyppeteer request process
        :param page: Reference to the page where we'll request the content
        """
        super().__init__()
        self.__page = page
        self.__response = None

        if page is None or not isinstance(page, pyppeteer.page.Page):
            raise TypeError("A valid Pyppeteer page must be supplied")

        page.on('response', self.__intercept_response)

    async def process(self, *_):
        """
        Returns the received response data from a request done using Pyppeteer,
        overwriting the text property to get the current contents of the page
        Defined as a coroutine to be properly integrated with the Pyppeteer
        driver
        The Pyppeteer page must have gotten a response between the constructor
        call and this one. IMPORTANT: The HTTP headers and status code are
        captured from the first response received by the Pyppeteer page after
        the constructor is called, but the text is collected from the page
        contents when the process() method is called. This may cause
        synchronization issues if multiple pages are requested in sequence
        between these calls (e.g.: it will analyse the response to the first
        page request, and the text contents of the last page).
        :returns: Response received from Pyppeteer
        """

        if self.__response is None:
            # No response was received since the constructor was called
            raise ValueError("The page hasn't received any responses")

        result = await ResponseData.create_from_pyppeteer(self.__response)

        # Update the text contents of the response with the current page
        # contents, if it has a text type
        if 'text' in result.headers['content-type'].split('/')[0]:
            result.text = await self.__page.content()

        return result
