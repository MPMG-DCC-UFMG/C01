"""
This module tests the entry probing process as a whole
"""
import unittest

from unittest import mock

from entry_probing import EntryProbing, GETProbingRequest,\
    PyppeteerProbingRequest, HTTPStatusProbingResponse,\
    TextMatchProbingResponse,\
    BinaryFormatProbingResponse, ResponseData

# helper function to create a mock of a Pyppeteer.page.Page entry
from .test_entry_probing_request import create_mock_pyp_page


class EntryProbingTest(unittest.IsolatedAsyncioTestCase):
    """
    Testing routines for the entry probing process
    """

    def response_200(*_) -> mock.Mock:
        """
        Function used to return a mock of an HTTP response with status 200 and
        "entry found" in the text body
        """

        return mock.Mock(headers={'Content-Type': 'text/html'},
                         text="entry found",
                         status_code=200)


    def response_404(*_) -> mock.Mock:
        """
        Function used to return a mock of an HTTP response with status 404 and
        "entry not found" in the text body
        """

        return mock.Mock(headers={'Content-Type': 'text/html'},
                         text="entry not found",
                         status_code=404)


    def response_binary(*_) -> mock.Mock:
        """
        Function used to return a mock of an HTTP response with status 200 and
        a MIME type of application/octet-stream, simulating a binary response.
        A text value of "entry found" is included so we can check if it is
        properly discarded
        """

        return mock.Mock(headers={'Content-Type': 'application/octet-stream'},
                         status_code=200, text="entry found")


    @mock.patch('entry_probing.requests.get', response_200)
    def test_probing_found_sync(self):
        """
        Tests the general working cases for probing a found entry using a non
        asynchronous method. We only use GET requests, since the tests for
        different request methods is done in a separate test file.
        """

        # checks the URL for a 200 code, the string "entry found" and a text
        # type
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertTrue(probe.check_entry())

        # the same as above but checks for a binary file
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse())\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(probe.check_entry())

        # checks the URL for a non-404 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertTrue(probe.check_entry())

        # checks the URL for a 404 code, a 200 code, and the string
        # "entry found" (should always fail)
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(probe.check_entry())

        # just requests without any checks (should default to True)
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertTrue(probe.check_entry())

        # check if response is stored properly
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertIsNone(probe.response)
        probe.check_entry()
        self.assertTrue(isinstance(probe.response, ResponseData))


    async def test_probing_found_async(self):
        """
        Tests the general working cases for probing a found entry using an
        asynchronous method with Pyppeteer
        """

        # mock of the page to be accessed
        page = create_mock_pyp_page("text/html", 200, "entry found")

        # checks the page for a 200 code, the string "entry found" and a text
        # type
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(BinaryFormatProbingResponse(opposite=True))\
             .add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))

        self.assertTrue(await probe.async_check_entry())

        # the same as above but checks for a binary file
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse())\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(await probe.async_check_entry())

        # checks the page for a non-404 code and the string "entry found"
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertTrue(await probe.async_check_entry())

        # checks the page for a 404 code, a 200 code, and the string
        # "entry found" (should always fail)
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(await probe.async_check_entry())

        # just requests without any checks (should default to True)
        probe = EntryProbing(PyppeteerProbingRequest(page))
        self.assertTrue(await probe.async_check_entry())

        # check if response is stored properly
        probe = EntryProbing(PyppeteerProbingRequest(page))
        self.assertIsNone(probe.response)
        await probe.async_check_entry()
        self.assertTrue(isinstance(probe.response, ResponseData))


    @mock.patch('entry_probing.requests.get', response_binary)
    def test_probing_binary_sync(self):
        """
        Tests the general cases for probing a page with binary content using a
        non asynchronous method.
        """

        # checks the URL for a 200 code and binary content
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse())
        self.assertTrue(probe.check_entry())

        # the same as above but checks for text content
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse(opposite=True))
        self.assertFalse(probe.check_entry())

        # checks for the string "entry found" in the content (should fail
        # since the text is ignored)
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(probe.check_entry())


    async def test_probing_binary_async(self):
        """
        Tests the general working cases for probing a page with binary content
        using an asynchronous method with Pyppeteer
        """

        # mock of the page to be accessed, with a binary MIME type and a 200
        # status code (the text value of "entry found" is included so we can
        # check if it is properly discarded)
        page = create_mock_pyp_page("application/octet-stream", 200,
                                    "entry found")

        # checks the page for a 200 code and binary content
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse())
        self.assertTrue(await probe.async_check_entry())

        # the same as above but checks for text content
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse(opposite=True))
        self.assertFalse(await probe.async_check_entry())

        # checks for the string "entry found" in the content (should fail
        # since the text is ignored)
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertFalse(await probe.async_check_entry())


    @mock.patch('entry_probing.requests.get', response_404)
    def test_probing_not_found_sync(self):
        """
        Tests the general working cases for probing a not found entry using a
        non asynchronous method
        """

        # checks the URL for a 200 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # checks the URL for a non-404 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # checks the URL for a 404 code and the string "not found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(TextMatchProbingResponse("not found"))
        self.assertEqual(probe.check_entry(), True)

        # checks the URL for a non-503 code
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(503,
                                                             opposite=True))
        self.assertEqual(probe.check_entry(), True)

        # check if response is stored properly
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertIsNone(probe.response)
        probe.check_entry()
        self.assertTrue(isinstance(probe.response, ResponseData))


    async def test_probing_not_found_async(self):
        """
        Tests the general working cases for probing a not found entry using an
        asynchronous method
        """

        # mock of the page to be accessed
        page = create_mock_pyp_page("text/html", 404, "entry not found")

        # checks the page for a 200 code and the string "entry found"
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(await probe.async_check_entry(), False)

        # checks the page for a non-404 code and the string "entry found"
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(await probe.async_check_entry(), False)

        # checks the page for a 404 code and the string "not found"
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(TextMatchProbingResponse("not found"))
        self.assertEqual(await probe.async_check_entry(), True)

        # checks the page for a non-503 code
        probe = EntryProbing(PyppeteerProbingRequest(page))
        probe.add_response_handler(HTTPStatusProbingResponse(503,
                                                             opposite=True))
        self.assertEqual(await probe.async_check_entry(), True)

        # check if response is stored properly
        probe = EntryProbing(PyppeteerProbingRequest(page))
        self.assertIsNone(probe.response)
        await probe.async_check_entry()
        self.assertTrue(isinstance(probe.response, ResponseData))


    def test_probing_param_errors(self):
        """
        Tests the passing of invalid parameters to the probing methods
        """

        # invalid request handler
        self.assertRaises(TypeError, EntryProbing, [1])

        # invalid response handler
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertRaises(TypeError, probe.add_response_handler, [1])


if __name__ == '__main__':
    unittest.main()
