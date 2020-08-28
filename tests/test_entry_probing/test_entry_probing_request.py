"""
This module tests the classes which abstract the entry probing requests
"""
import unittest
from unittest import mock

import pyppeteer
import requests.exceptions
import urllib3.exceptions

from entry_probing import HTTPProbingRequest, PyppeteerProbingRequest


# Helper functions
def create_mock_pyp_page(content_type: str = None,
                         status_code: int = None,
                         text: str = None,
                         trigger_response: bool = True) -> mock.Mock:
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
    mock_pyp_resp = mock.Mock(spec=pyppeteer.network_manager.Response,
                                   headers={'content-type': content_type},
                                   status=status_code,
                                   text=lambda: return_async_text(text))

    on_event = mock.Mock(return_value=None)
    if trigger_response:
        # use the callback function as soon as it is set
        def on_event_func(_, f): return f(mock_pyp_resp)
        # wrap this function in a mock object to be able to check how it is
        # called
        on_event = mock.Mock(side_effect=on_event_func)

    # mock of the Pyppeteer page
    mock_page = mock.Mock(spec=pyppeteer.page.Page, on=on_event,
                               content=lambda: return_async_text(text))

    return mock_page


# Tests
class ProbingRequestTest(unittest.IsolatedAsyncioTestCase):
    """
    Testing routines for the entry probing request (uses
    IsolatedAsyncioTestCase to be compatible with Pyppeteer)
    """

    def test_succesful_req_http(self):
        """
        Tests if the correct HTTP requests are sent to the specified URLs with
        the expected parameters
        """

        # Changes the method used by the HTTPProbingRequest when requesting to
        # use our mock
        mock_response = mock.Mock(headers= {'Content-Type': 'text/html'})

        get_mock = mock.Mock(return_value=mock_response)
        post_mock = mock.Mock(return_value=mock_response)
        HTTPProbingRequest.REQUEST_METHODS["GET"] = get_mock
        HTTPProbingRequest.REQUEST_METHODS["POST"] = post_mock

        # GET request with a parameter in the URL
        probe = HTTPProbingRequest("http://test.com/{}", "GET")
        probe.process([10])
        expected = [("http://test.com/10",), {'data':{}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # POST request with a parameter in the URL
        probe = HTTPProbingRequest("http://test.com/{}", "POST")
        probe.process([10])
        expected = [("http://test.com/10",), {'data':{}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # GET request with a formatted parameter in the URL
        probe = HTTPProbingRequest("http://test.com/{:03d}", "GET")
        probe.process([10])
        expected = [("http://test.com/010",), {'data':{}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with no parameter
        probe = HTTPProbingRequest("http://test.com/", "GET")
        probe.process()
        expected = [("http://test.com/",), {'data':{}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with placeholder but no parameter
        probe = HTTPProbingRequest("http://test.com/{}", "GET")
        probe.process()
        expected = [("http://test.com/{}",), {'data':{}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # If entry is present but URL doesn't have any placeholders it just
        # uses the given url
        probe = HTTPProbingRequest("http://test.com/", "GET")
        probe.process([1])
        expected = [("http://test.com/",), {'data':{}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with one parameter in the request body
        probe = HTTPProbingRequest("http://test.com/", "GET")
        probe.process([], {'test1': 100})
        expected = [("http://test.com/",), {'data':{'test1': 100}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with two parameters in the URL and two in the request
        # body
        probe = HTTPProbingRequest("http://test.com/{}/{}", "GET")
        probe.process([1, 2], {'test1': 10, 'test2': 200})
        expected = [("http://test.com/1/2",), {'data':{'test1': 10,
                                                       'test2': 200}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request using only the pre-made request body
        probe = HTTPProbingRequest("http://test.com/", "GET",
                                   {'test1': 10, 'test2': 200})
        probe.process()
        expected = [("http://test.com/",), {'data':{'test1': 10,
                                                    'test2': 200}}]
        self.assertEqual(list(get_mock.call_args), expected)

        # POST request with a parameter in the request body
        probe = HTTPProbingRequest("http://test.com/", "POST")
        probe.process([], {"test_prop": 100})
        expected = [('http://test.com/',), {'data': {'test_prop': 100}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with multiple parameters in the request body
        probe = HTTPProbingRequest("http://test.com/", "POST",
                                   {'extra1': 0, 'extra2': 1})
        probe.process([], {"test_prop": 100})
        expected = [('http://test.com/',), {'data': {'test_prop': 100,
                                                     'extra1': 0,
                                                     'extra2': 1}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with no parameters in the request body
        probe = HTTPProbingRequest("http://test.com/", "POST")
        probe.process()
        expected = [('http://test.com/',), {'data': {}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request using only the pre-made request body
        probe = HTTPProbingRequest("http://test.com/", "POST", {'extra1': 0})
        probe.process()
        expected = [('http://test.com/',), {'data': {'extra1': 0}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with two parameters in the URL and two in the request
        # body
        probe = HTTPProbingRequest("http://test.com/{}/{}", "POST")
        probe.process([1, 2], {'test1': 10, 'test2': 200})
        expected = [("http://test.com/1/2",), {'data':{'test1': 10,
                                                       'test2': 200}}]
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


    def test_invalid_req_http(self):
        """
        Tests invalid HTTP requests
        """

        # URL misses schema (http://)
        probe = HTTPProbingRequest("nonexistenturl/", "GET")
        self.assertRaises(requests.exceptions.MissingSchema, probe.process)

        # Invalid request body
        self.assertRaises(TypeError, HTTPProbingRequest,
                          "http://nonexistenturl/", "POST", [])


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
