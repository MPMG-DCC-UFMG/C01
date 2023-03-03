"""
Sub-class of the general anti-blocking module for requests made with the Python Requests library.
"""
import requests

from .antiblock_general import AntiblockDriver


class AntiblockRequests(AntiblockDriver):
    """
    Implementation of anti-blocking procedures with the Requests library.
    The methods in this class are direct wrappers around the methods in the
    library, and forward all the parameters supplied.
    """

    def request(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.request method, with anti-blocking measures.
        """
        return self._send_request(requests.request, *args, **kwargs)

    def get(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.get method, with anti-blocking measures.
        """
        return self._send_request(requests.get, *args, **kwargs)

    def post(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.post method, with anti-blocking measures.
        """
        return self._send_request(requests.post, *args, **kwargs)

    def put(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.put method, with anti-blocking measures.
        """
        return self._send_request(requests.put, *args, **kwargs)

    def delete(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.delete method, with anti-blocking measures.
        """
        return self._send_request(requests.delete, *args, **kwargs)

    def head(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.head method, with anti-blocking measures.
        """
        return self._send_request(requests.head, *args, **kwargs)

    def patch(self, *args, **kwargs) -> requests.models.Response:
        """
        Wrapper for the requests.patch method, with anti-blocking measures.
        """
        return self._send_request(requests.patch, *args, **kwargs)
