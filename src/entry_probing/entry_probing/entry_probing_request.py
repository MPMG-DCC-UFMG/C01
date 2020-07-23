"""
This module contains the classes which describe the requesting procedure for
the entry probing process
"""

from typing import Any, Hashable, Optional

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
    def process(self, entry: Optional[Any] = None) -> ResponseData:
        """
        Abstract method: sends a request to the desired URL and returns the
        response

        :param entry: entry parameter to be used by the request, if necessary
        """
        pass


class GETProbingRequest(ProbingRequest):
    """
    Description of a GET request with possible placeholders for data in the URL
    """

    def __init__(self, url: str):
        """
        Constructor for the GET request.

        :param url: URL to be requested, with possible placeholders for entry
                    parameters
        """
        super().__init__()
        self.__url = url

    def process(self, entry: Optional[Any] = None) -> ResponseData:
        """
        Sends a GET request to the desired URL, inserting the entry information
        if the entry parameter is not None. Returns the response to this
        request.

        :param entry: entry parameter to be inserted in the URL, if necessary

        :returns: Response obtained from GET request
        """
        if entry is None:
            return requests.get(self.__url)
        resp = requests.get(self.__url.format(entry))
        return ResponseData().create_from_requests(resp)


class POSTProbingRequest(ProbingRequest):
    """
    Description of a POST request with entry data sent in the request body
    """

    def __init__(self,
                 url: str,
                 property_name: Hashable = None,
                 data: dict = None):
        """
        Constructor for the POST request.

        :param url:           URL to be requested
        :param property_name: name of property in which to store the entry's
                              data within the request body
        :param data:          dictionary of extra data to be sent in the
                              request body, if necessary
        """
        super().__init__()
        self.__url = url
        self.__data = data if data is not None else {}
        self.__property_name = property_name

        if data is not None and not isinstance(data, dict):
            raise TypeError("POST data must be a dictionary")

    def process(self, entry: Optional[Any] = None) -> ResponseData:
        """
        Sends a POST request to the desired URL, inserting the entry
        information in the request body, along with any other data supplied.
        Returns the response to this request.

        :param entry: entry's identifier to be sent

        :returns: Response obtained from POST request
        """

        if self.__property_name is not None:
            self.__data[self.__property_name] = entry

        resp = requests.post(self.__url, data=self.__data)
        return ResponseData().create_from_requests(resp)


class PyppeteerProbingRequest(ProbingRequest):
    """
    Description of a request which consists of using the currently open page in
    Pyppeteer as the response. The process() method is defined as a coroutine
    so it can be properly integrated with the Pyppeteer driver.

    The desired page must be requested after the constructor is called and
    before the call to the process() method
    """

    def __intercept_response(self,
                             response: pyppeteer.network_manager.Response):
        """
        Intercepts a response to a request made by the Pyppeteer page
        configured in the constructor and stores it

        :param response: Response received by Pyppeteer
        """
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

    async def process(self, *_) -> ResponseData:
        """
        Returns the received response data from a request done using Pyppeteer

        Defined as a coroutine to be properly integrated with the Pyppeteer
        driver

        The Pyppeteer page must have gotten a response between the constructor
        call and this one

        :returns: Response received from Pyppeteer
        """

        if self.__response is None:
            # No response was received since the constructor was called
            raise ValueError("The page hasn't received any responses")

        return await ResponseData().create_from_pyppeteer(self.__response)
