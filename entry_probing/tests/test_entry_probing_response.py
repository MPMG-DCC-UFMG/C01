"""
This module tests the classes which abstract the entry probing response handling
"""
import unittest

from unittest import mock

from entry_probing import HTTPStatusProbingResponse, TextMatchProbingResponse,\
                          BinaryFormatProbingResponse

class ProbingResponseTest(unittest.TestCase):
    """
    Testing routines for the entry probing response handling
    """

    def test_http_status(self):
        """
        Tests the HTTP status response handler
        """

        # Mock responses with 200 and 404 HTTP status codes
        status200 = mock.MagicMock(status_code=200)
        status404 = mock.MagicMock(status_code=404)

        # Validates the entry with an HTTP status of 200
        resp_handler = HTTPStatusProbingResponse(200)
        self.assertEqual(resp_handler.process(status200), True)

        # Invalidates the entry with any HTTP status besides 200
        self.assertEqual(resp_handler.process(status404), False)

        # Validates the entry with any HTTP status besides 404
        resp_handler = HTTPStatusProbingResponse(404, opposite=True)
        self.assertEqual(resp_handler.process(status200), True)

        # Invalidates the entry with an HTTP status of 404
        self.assertEqual(resp_handler.process(status404), False)


    def test_text_match(self):
        """
        Tests the text-matching response handler
        """

        # Mock responses with different text contents
        text_found = mock.MagicMock(text="Page found in our database")
        text_not_found = mock.MagicMock(text="Sorry, page not found")

        # Validates response with a given text
        resp_handler = TextMatchProbingResponse("Page found")
        self.assertEqual(resp_handler.process(text_found), True)

        # Invalidates response where the text is not present
        self.assertEqual(resp_handler.process(text_not_found), False)

        # The search is case-sensitive
        resp_handler = TextMatchProbingResponse("page found")
        self.assertEqual(resp_handler.process(text_found), False)

        # Validates response where text is not present
        resp_handler = TextMatchProbingResponse("page not found", opposite=True)
        self.assertEqual(resp_handler.process(text_found), True)

        # Invalidates response where text is present
        self.assertEqual(resp_handler.process(text_not_found), False)



    def test_binary_format(self):
        """
        Tests the binary format detection response handler
        """

        # Mock text and binary responses
        text_header = {'Content-Type': 'text/json'}
        text_resp = mock.MagicMock(headers=text_header)
        binary_header = {'Content-Type': 'application/vnd.ms-excel'}
        binary_resp = mock.MagicMock(headers=binary_header)

        # Validates binary response
        resp_handler = BinaryFormatProbingResponse()
        self.assertEqual(resp_handler.process(binary_resp), True)

        # Invalidates text response
        self.assertEqual(resp_handler.process(text_resp), False)

        # Validates text response
        resp_handler = BinaryFormatProbingResponse(opposite=True)
        self.assertEqual(resp_handler.process(text_resp), True)

        # Invalidates binary response
        self.assertEqual(resp_handler.process(binary_resp), False)


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
