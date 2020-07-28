"""
This module tests the classes which abstract the entry probing requests
"""
import unittest
from unittest import mock

import pyppeteer
import requests.exceptions
import urllib3.exceptions

from entry_probing import GETProbingRequest, POSTProbingRequest,\
                          PyppeteerProbingRequest


# Helper functions
def create_mock_pyp_page(content_type: str = None,
                         status_code: int = None,
                         text: str = None,
                         trigger_response: bool = True) -> mock.MagicMock:
    """
    Generates a mock of a Pyppeteer page and response. If the trigger_response
    parameter is True, the response event is triggered as soon as it is set.
    This simulates the user accessing a page.

    :param content_type:     content-type to be inserted in the response header
    :param status_code:      HTTP status code for the response
    :param text:             text data received
    :param trigger_response: whether or not to immediatly trigger the response
                             event after it is set
    """

    # response.text is an awaitable, so we wrap the text value in a coroutine
    async def return_async_text(text):
        return text

    # mock of the Pyppeteer response
    mock_pyp_resp = mock.MagicMock(spec= pyppeteer.network_manager.Response,
                                   headers={'content-type': content_type },
                                   status=status_code,
                                   text=lambda: return_async_text(text))

    on_event = mock.MagicMock(return_value=None)
    if trigger_response:
        # use the callback function as soon as it is set
        on_event_func = lambda _, f: f(mock_pyp_resp)
        # wrap this function in a mock object to be able to check how it is
        # called
        on_event = mock.MagicMock(side_effect=on_event_func)

    # mock of the Pyppeteer page
    mock_page = mock.MagicMock(spec=pyppeteer.page.Page, on=on_event)

    return mock_page


# Tests
class ProbingRequestTest(unittest.IsolatedAsyncioTestCase):
    """
    Testing routines for the entry probing request (uses
    IsolatedAsyncioTestCase to be compatible with Pyppeteer)
    """

    @mock.patch('entry_probing.requests.get')
    def test_succesful_req_get(self, get_mock: unittest.mock.MagicMock):
        """
        Tests if the correct GET requests are sent to the specified URLs with
        the expected parameters

        :param get_mock:  Mock function, called when requests.get is used
                          inside the entry probing module
        """

        # GET request with a parameter
        probe = GETProbingRequest("http://test.com/{}")
        probe.process(10)
        expected = [("http://test.com/10",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with a formatted parameter
        probe = GETProbingRequest("http://test.com/{:03d}")
        probe.process(10)
        expected = [("http://test.com/010",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with no parameter
        probe = GETProbingRequest("http://test.com/")
        probe.process()
        expected = [("http://test.com/",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with placeholder but no parameter
        probe = GETProbingRequest("http://test.com/{}")
        probe.process()
        expected = [("http://test.com/{}",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # If entry is present but URL doesn't have any placeholders it just
        # uses the given url
        probe = GETProbingRequest("http://test.com/")
        probe.process(1)
        expected = [("http://test.com/",), {}]
        self.assertEqual(list(get_mock.call_args), expected)


    @mock.patch('entry_probing.requests.post')
    def test_succesful_req_post(self, post_mock: unittest.mock.MagicMock):
        """
        Tests if the correct POST requests are sent to the specified URLs with
        the expected parameters

        :param post_mock: Mock function, called when requests.post is used
                          inside the entry probing module
        """

        # POST request with a parameter in the request body
        probe = POSTProbingRequest("http://test.com/", "test_prop")
        probe.process(100)
        expected = [('http://test.com/',), {'data': {'test_prop': 100}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with multiple parameters in the request body
        probe = POSTProbingRequest("http://test.com/", "test_prop",
                                   {'extra1': 0, 'extra2': 1})
        probe.process(100)
        expected = [('http://test.com/',), {'data': {'test_prop': 100,
                                                     'extra1': 0,
                                                     'extra2': 1}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with no parameters in the request body
        probe = POSTProbingRequest("http://test.com/")
        probe.process()
        expected = [('http://test.com/',), {'data': {}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request using only the pre-made request body
        probe = POSTProbingRequest("http://test.com/", None, {'extra1': 0})
        probe.process()
        expected = [('http://test.com/',), {'data': {'extra1': 0}}]
        self.assertEqual(list(post_mock.call_args), expected)


    async def test_succesful_req_pyp(self):
        """
        Tests valid requests with Pyppeteer
        """

        # creates a mock of the Pyppeteer page handler
        pyp_handler = create_mock_pyp_page("text/html", 200, "test content")
        probe = PyppeteerProbingRequest(pyp_handler)
        # in a real scenario this is where we would request the URL in
        # pyp_handler, e.g.:
        # await pyp_handler.goto('https://www.example.com')
        result = await probe.process()

        # check if the response event was setup correctly (we need to use name
        # mangling to access the private method for this specific purpose)
        expected = ['response',
                    probe._PyppeteerProbingRequest__intercept_response]
        self.assertEqual(list(pyp_handler.on.call_args.args), expected)

        self.assertEqual(result.headers, {'content-type': 'text/html'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, "test content")

        # Another test with a different response
        pyp_handler = create_mock_pyp_page("text/json", 404, "")
        probe = PyppeteerProbingRequest(pyp_handler)
        result = await probe.process()

        expected = ['response',
                    probe._PyppeteerProbingRequest__intercept_response]
        self.assertEqual(list(pyp_handler.on.call_args.args), expected)

        self.assertEqual(result.headers, {'content-type': 'text/json'})
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.text, "")


    def test_invalid_req_get(self):
        """
        Tests invalid requests with GET
        """

        # Non-existent URL
        probe = GETProbingRequest("http://nonexistenturl1234")
        self.assertRaises(requests.exceptions.ConnectionError, probe.process)

        # URL misses schema (http://)
        probe = GETProbingRequest("nonexistenturl/")
        self.assertRaises(requests.exceptions.MissingSchema, probe.process)


    def test_invalid_req_post(self):
        """
        Tests invalid requests with POST
        """

        # Non-existent URL
        probe = POSTProbingRequest("http://nonexistenturl1234", "test")
        self.assertRaises(urllib3.exceptions.NewConnectionError, probe.process)

        # URL misses schema (http://)
        probe = POSTProbingRequest("nonexistenturl/", "test")
        self.assertRaises(requests.exceptions.MissingSchema, probe.process)

        # Invalid POST property name
        probe = POSTProbingRequest("http://nonexistenturl/", [])
        self.assertRaises(TypeError, probe.process)

        # Invalid POST request body
        self.assertRaises(TypeError, POSTProbingRequest,
                          "http://nonexistenturl/", "test", [])


    async def test_invalid_req_pyp(self):
        """
        Tests invalid requests with Pyppeteer
        """

        # initializing the Probing class with the wrong type
        self.assertRaises(TypeError, PyppeteerProbingRequest, 100)

        # calling the process() method without requesting a page after the
        # constructor is called
        # setting the trigger_response parameter to False we make sure the
        # response callback is not called, simulating this scenario
        pyp_handler = create_mock_pyp_page("text/html", 200, "test content",
                                           trigger_response=False)
        probe = PyppeteerProbingRequest(pyp_handler)

        with self.assertRaises(ValueError):
            # process() should raise a ValueError
            result = await probe.process()


if __name__ == '__main__':
    unittest.main()
