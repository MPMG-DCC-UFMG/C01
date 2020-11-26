"""
This module contains the classes which describe the response handling procedure
for the entry probing process
"""

import abc
import requests
import pyppeteer
from typing import Any, Dict, Hashable, List, Optional

# Helper class


class ResponseData():
    """
    Data class to store the response to a request in a more general form.
    Contains class methods to generate a correct instance from another
    library's response format.
    """

    def __init__(self,
                 headers,
                 status_code,
                 text):
        """
        Response constructor. Should be called from the create_from_* methods.
        :param headers:     HTTP headers for the response
        :param status_code: HTTP status code for the response
        :param text:        text data received
        """
        self.headers = headers
        self.status_code = status_code
        self.text = text

    @classmethod
    def create_from_requests(cls,
                             resp: requests.models.Response) -> 'ResponseData':
        """
        Create an appropriate object from a requests.models.Response object
        :param resp: response received from the use of the requests library
        :returns: an instance of ResponseData with the information in resp
        """
        text = ""
        if 'text' in resp.headers['Content-Type'].split('/')[0]:
            text = resp.text

        return cls(headers=resp.headers,
                   status_code=resp.status_code,
                   text=text)

    @classmethod
    async def create_from_pyppeteer(cls,
                                    resp: pyppeteer.network_manager.Response
                                    ) -> 'ResponseData':
        """
        Create an appropriate object from a pyppeteer.network_manager.Response
        object
        Defined as a coroutine to be propeprly integrated with the Pyppeteer
        driver
        :param resp: response received from the use of the Pyppeteer library
        :returns: an instance of ResponseData with the information in resp
        """
        text = ""

        no_redir = (not 300 <= resp.status < 400)
        is_text = ('text' in resp.headers['content-type'].split('/')[0])
        if no_redir and is_text:
            # The following method only works when the content is text and the
            # page status is not in the 3XX range (redirects)
            text = await resp.text()

        return cls(headers=resp.headers,
                   status_code=resp.status,
                   text=text)


# ProbingResponse entries

class ProbingResponse():
    """
    Abstract parent class for response handler definitions. Child classes
    implement the _validate_resp method, which should receive a
    ResponseData object and return a boolean indicating if the desired
    condition is met. The process method should be called externally, and
    accounts for the possible negation of the result.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, opposite):
        """
        Constructor for a response handler
        :param opposite: inverts the output of the response handler if set to
                         true
        """
        if not isinstance(opposite, bool):
            raise TypeError("Opposite flag must be a boolean")

        self.opposite = opposite

    @abc.abstractmethod
    def _validate_resp(self, response):
        """
        Abstract method: checks if the response meets the desired condition
        :param response: ResponseData object to be validated
        """
        pass

    def process(self, response):
        """
        Uses the _validate_resp method to check if the response meets the
        desired condition, and inverts the result if the opposite flag is set
        :param response: ResponseData object to be validated
        :returns: a boolean indicating if the specified condition was met,
                  taking the opposite flag into consideration
        """
        valid = self._validate_resp(response)
        return valid if not self.opposite else (not valid)


class HTTPStatusProbingResponse(ProbingResponse):
    """
    Response handler which checks for a specific HTTP status code
    """

    def __init__(self, status_code, *args, **kwargs):
        """
        HTTP status response constructor
        :param status_code: HTTP status code to check for
        """
        super().__init__(*args, **kwargs)
        self.status_code = status_code

    def _validate_resp(self, response):
        """
        Checks if the response has the specified HTTP status code
        :param response: ResponseData object to be validated
        :returns: True if the response has the specified HTTP status code,
                  false otherwise
        """
        return response.status_code == self.status_code


class TextMatchProbingResponse(ProbingResponse):
    """
    Response handler which checks for the presence of a specified string within
    the response body
    """

    def __init__(self, text_match, *args, **kwargs):
        """
        Text matching response constructor
        :param text_match: string to be found within the response body
        """
        super().__init__(*args, **kwargs)
        self.text_match = text_match

    def _validate_resp(self, response):
        """
        Checks if the response.text property has the specified string within
        it, using a case-insensitive comparison
        :param response: ResponseData object to be validated
        :returns: True if the response contains the specified string, false
                  otherwise
        """
        return self.text_match.lower() in response.text.lower()


class BinaryFormatProbingResponse(ProbingResponse):
    """
    Response handler which checks if the MIME-type received is a non-textual
    one
    """

    def _validate_resp(self, response):
        """
        Checks if the response's MIME-type does not contain the word 'text'
        in the first part (before the backslash)
        :param response: ResponseData object to be validated
        :returns: True if the response is non-textual, false otherwise
        """

        # deal with different capitalizations of the content-type header name
        if 'Content-Type' in response.headers:
            # Usual capitalization
            header_name = 'Content-Type'
        elif 'content-type' in response.headers:
            # Pyppeteer capitalization
            header_name = 'content-type'

        return 'text' not in response.headers[header_name].split('/')[0]
