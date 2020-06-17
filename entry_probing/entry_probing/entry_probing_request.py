"""
This module contains the classes which describe the requesting procedure for the
entry probing process
"""

from typing import Any, Hashable, Optional

import abc
import requests

class ProbingRequest():
    """
    Abstract parent class for request definitions. Child classes implement the
    process method, which should send an appropriate request to the target's
    URL and return the response, which is a requests.models.Response object.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self) -> requests.models.Response:
        """
        Abstract method: sends a request to the desired URL and returns the
        response
        """
        pass


class GETProbingRequest(ProbingRequest):
    """
    Description of a GET request with possible placeholders for data in the URL
    """

    def __init__(self, url: str, entry: Optional[Any] = None):
        """
        Constructor for the GET request.

        :param url:   URL to be requested, with possible placeholders for entry
                      parameters
        :param entry: entry parameter to be inserted in the URL, if necessary
        """
        super().__init__()
        self.url = url
        self.entry = entry

    def process(self) -> requests.models.Response:
        """
        Sends a GET request to the desired URL, inserting the entry information
        if the entry property is not None. Returns the response to this request.

        :returns: Response obtained from GET request
        """
        if self.entry is None:
            return requests.get(self.url)
        return requests.get(self.url.format(self.entry))


class POSTProbingRequest(ProbingRequest):
    """
    Description of a POST request with entry data sent in the request body
    """

    def __init__(self,
                 url: str,
                 property_name: Hashable = None,
                 entry: Any = None,
                 data: dict = None):
        """
        Constructor for the POST request.

        :param url:           URL to be requested
        :param property_name: name of property in which to store the entry's
                              data within the request body
        :param entry:         entry's identifier to be sent
        :param data:          dictionary of extra data to be sent in the request
                              body, if necessary
        """
        super().__init__()
        self.url = url
        self.data = data if data is not None else {}

        if data is not None and not isinstance(data, dict):
            raise TypeError("POST data must be a dictionary")

        if property_name is not None:
            self.data[property_name] = entry

    def process(self) -> requests.models.Response:
        """
        Sends a POST request to the desired URL, inserting the entry information
        in the request body, along with any other data supplied. Returns the
        response to this request.

        :returns: Response obtained from POST request
        """
        return requests.post(self.url, data=self.data)
