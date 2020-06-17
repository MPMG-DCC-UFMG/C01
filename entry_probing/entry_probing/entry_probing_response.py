"""
This module contains the classes which describe the response handling procedure
for the entry probing process
"""

import abc
import requests.models

class ProbingResponse():
    """
    Abstract parent class for response handler definitions. Child classes
    implement the _validate_resp method, which should receive a
    requests.models.Response object and return a boolean indicating if the
    desired condition is met. The process method should be called externally,
    and accounts for the possible negation of the result.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, opposite: bool = False):
        """
        Constructor for a response handler

        :param opposite: inverts the output of the response handler if set to
                         true
        """
        if not isinstance(opposite, bool):
            raise TypeError("Opposite flag must be a boolean")

        self.opposite = opposite

    @abc.abstractmethod
    def _validate_resp(self, response: requests.models.Response) -> bool:
        """
        Abstract method: checks if the response meets the desired condition

        :param response: Response object to be validated
        """
        pass

    def process(self, response: requests.models.Response) -> bool:
        """
        Uses the _validate_resp method to check if the response meets the
        desired condition, and inverts the result if the opposite flag is set

        :param response: Response object to be validated

        :returns: a boolean indicating if the specified condition was met,
                  taking the opposite flag into consideration
        """
        valid = self._validate_resp(response)
        return valid if not self.opposite else (not valid)


class HTTPStatusProbingResponse(ProbingResponse):
    """
    Response handler which checks for a specific HTTP status code
    """

    def __init__(self, status_code: str, *args, **kwargs):
        """
        HTTP status response constructor

        :param status_code: HTTP status code to check for
        """
        super().__init__(*args, **kwargs)
        self.status_code = status_code

    def _validate_resp(self, response: requests.models.Response) -> bool:
        """
        Checks if the response has the specified HTTP status code

        :param response: Response object to be validated

        :returns: True if the response has the specified HTTP status code, false
                  otherwise
        """
        return response.status_code == self.status_code


class TextMatchProbingResponse(ProbingResponse):
    """
    Response handler which checks for the presence of a specified string within
    the response body
    """

    def __init__(self, text_match: str, *args, **kwargs):
        """
        Text matching response constructor

        :param text_match: string to be found within the response body
        """
        super().__init__(*args, **kwargs)
        self.text_match = text_match

    def _validate_resp(self, response: requests.models.Response) -> bool:
        """
        Checks if the response.text property has the specified string within it

        :param response: Response object to be validated

        :returns: True if the response contains the specified string, false
                  otherwise
        """
        return self.text_match in response.text


class BinaryFormatProbingResponse(ProbingResponse):
    """
    Response handler which checks if the MIME-type received is a non-textual one
    """

    def _validate_resp(self, response: requests.models.Response) -> bool:
        """
        Checks if the response's MIME-type does not contain the word 'text'
        in the first part (before the backslash)

        :param response: Response object to be validated

        :returns: True if the response is non-textual, false otherwise
        """
        return not 'text' in response.headers['Content-Type'].split('/')[0]
