"""
This module tests the classes which abstract the entry probing response
handling
"""
import unittest
from unittest import mock

from entry_probing import HTTPStatusProbingResponse, TextMatchProbingResponse,\
    BinaryFormatProbingResponse, ResponseData


class ProbingResponseTest(unittest.TestCase):
    """
    Testing routines for the entry probing response handling
    """

    def test_http_status(self):
        """
        Tests the HTTP status response handler
        """

        # Mock responses with 200 and 404 HTTP status codes
        status200 = mock.MagicMock(spec=ResponseData, status_code=200)
        status404 = mock.MagicMock(spec=ResponseData, status_code=404)

        # Validates the entry with an HTTP status of 200
        resp_handler = HTTPStatusProbingResponse(200)
        self.assertTrue(resp_handler.process(status200))

        # Invalidates the entry with any HTTP status besides 200
        self.assertFalse(resp_handler.process(status404))

        # Validates the entry with any HTTP status besides 404
        resp_handler = HTTPStatusProbingResponse(404, opposite=True)
        self.assertTrue(resp_handler.process(status200))

        # Invalidates the entry with an HTTP status of 404
        self.assertFalse(resp_handler.process(status404))


    def test_text_match(self):
        """
        Tests the text-matching response handler
        """

        # Mock responses with different text contents
        text_found = mock.MagicMock(spec=ResponseData,
                                    text="Page found in our database")
        text_not_found = mock.MagicMock(spec=ResponseData,
                                        text="Sorry, page not found")

        # Validates response with a given text
        resp_handler = TextMatchProbingResponse("Page found")
        self.assertTrue(resp_handler.process(text_found))

        # Invalidates response where the text is not present
        self.assertFalse(resp_handler.process(text_not_found))

        # The search is case-insensitive
        resp_handler = TextMatchProbingResponse("page found")
        self.assertTrue(resp_handler.process(text_found))

        # Validates response where text is not present
        resp_handler = TextMatchProbingResponse("page not found", opposite=True)
        self.assertTrue(resp_handler.process(text_found))

        # Invalidates response where text is present
        self.assertFalse(resp_handler.process(text_not_found))



    def test_binary_format(self):
        """
        Tests the binary format detection response handler
        """

        # Mock text and binary responses
        text_header = {'Content-Type': 'text/json'}
        text_resp = mock.MagicMock(spec=ResponseData, headers=text_header)
        binary_header = {'Content-Type': 'application/vnd.ms-excel'}
        binary_resp = mock.MagicMock(spec=ResponseData, headers=binary_header)

        # Validates binary response
        resp_handler = BinaryFormatProbingResponse()
        self.assertTrue(resp_handler.process(binary_resp))

        # Invalidates text response
        self.assertFalse(resp_handler.process(text_resp))

        # Validates text response
        resp_handler = BinaryFormatProbingResponse(opposite=True)
        self.assertTrue(resp_handler.process(text_resp))

        # Invalidates binary response
        self.assertFalse(resp_handler.process(binary_resp))


    def test_invalid_params(self):
        """
        Tests the handling of invalid parameters
        """

        # Invalid "opposite" flag
        self.assertRaises(TypeError, BinaryFormatProbingResponse, opposite=5)

        # No text to match supplied
        self.assertRaises(TypeError, TextMatchProbingResponse)

        # No status code supplied
        self.assertRaises(TypeError, HTTPStatusProbingResponse)


if __name__ == '__main__':
    unittest.main()
