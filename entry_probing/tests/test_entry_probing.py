"""
This module tests the entry probing process as a whole
"""
import unittest

from unittest import mock

from entry_probing import EntryProbing, GETProbingRequest,\
    HTTPStatusProbingResponse, TextMatchProbingResponse,\
    BinaryFormatProbingResponse


class EntryProbingTest(unittest.TestCase):
    """
    Testing routines for the entry probing process. We only use GET requests,
    since the tests for different request methods is done in a separate test
    file
    """

    def response_200(*_):
        """
        Function used to return a mock of an HTTP response with status 200 and
        "entry found" in the text body
        """

        return mock.Mock(headers={'Content-Type': 'text/html'},
                         text="entry found",
                         status_code=200)


    def response_404(*_):
        """
        Function used to return a mock of an HTTP response with status 404 and
        "entry not found" in the text body
        """

        return mock.Mock(headers={'Content-Type': 'text/html'},
                         text="entry not found",
                         status_code=404)


    @mock.patch('entry_probing.requests.get', response_200)
    def test_probing_found(self):
        """
        Tests the general working cases for probing a found entry
        """

        # Checks the URL for a 200 code, the string "entry found" and a text
        # type
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), True)

        # The same as above but checks for a binary file
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(BinaryFormatProbingResponse())\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # Checks the URL for a non-404 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), True)

        # Checks the URL for a 404 code, a 200 code, and the string
        # "entry found" (should always fail)
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # Just requests without any checks (should default to True)
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertEqual(probe.check_entry(), True)


    @mock.patch('entry_probing.requests.get', response_404)
    def test_probing_not_found(self):
        """
        Tests the general working cases for probing a not found entry
        """

        # Checks the URL for a 200 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(200))\
             .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # Checks the URL for a non-404 code and the string "entry found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404,
                                                             opposite=True))\
            .add_response_handler(TextMatchProbingResponse("entry found"))
        self.assertEqual(probe.check_entry(), False)

        # Checks the URL for a 404 code and the string "entry not found"
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(404))\
             .add_response_handler(TextMatchProbingResponse("entry not found"))
        self.assertEqual(probe.check_entry(), True)

        # Checks the URL for a non-503 code
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        probe.add_response_handler(HTTPStatusProbingResponse(503,
                                                             opposite=True))
        self.assertEqual(probe.check_entry(), True)


    def test_probing_param_errors(self):
        """
        Tests the passing of invalid parameters to the probing methods
        """

        # Invalid request handler
        self.assertRaises(TypeError, EntryProbing, [1])

        # Invalid response handler
        probe = EntryProbing(GETProbingRequest("http://test.com/"))
        self.assertRaises(TypeError, probe.add_response_handler, [1])


if __name__ == '__main__':
    unittest.main()
