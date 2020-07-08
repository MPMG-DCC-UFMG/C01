"""
This module tests the classes which abstract the entry probing requests
"""
import unittest
from unittest import mock

import requests.exceptions

from entry_probing import GETProbingRequest, POSTProbingRequest


class ProbingRequestTest(unittest.TestCase):
    """
    Testing routines for the entry probing request
    """

    @mock.patch('entry_probing.requests.post')
    @mock.patch('entry_probing.requests.get')
    def test_succesful_req(self,
                           get_mock: unittest.mock.MagicMock,
                           post_mock: unittest.mock.MagicMock):
        """
        Tests if the correct requests are sent to the specified URLs with the
        expected parameters

        :param get_mock:  Mock function, called when requests.get is used inside
                          the entry probing module
        :param post_mock: Mock function, called when requests.post is used
                          inside the entry probing module
        """

        # GET request with a parameter
        probe = GETProbingRequest("http://test.com/{}", 10)
        probe.process()
        expected = [("http://test.com/10",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # GET request with a formatted parameter
        probe = GETProbingRequest("http://test.com/{:03d}", 10)
        probe.process()
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

        # If entry is present but URL doesn't have any placeholders it just uses
        # the given url
        probe = GETProbingRequest("http://test.com/", 1)
        probe.process()
        expected = [("http://test.com/",), {}]
        self.assertEqual(list(get_mock.call_args), expected)

        # POST request with a parameter in the request body
        probe = POSTProbingRequest("http://test.com/", "test_prop", 100)
        probe.process()
        expected = [('http://test.com/',), {'data': {'test_prop': 100}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with multiple parameters in the request body
        probe = POSTProbingRequest("http://test.com/", "test_prop", 100,
                                   {'extra1': 0, 'extra2': 1})
        probe.process()
        expected = [('http://test.com/',), {'data': {'test_prop': 100,
                                                     'extra1': 0, 'extra2': 1}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request with no parameters in the request body
        probe = POSTProbingRequest("http://test.com/")
        probe.process()
        expected = [('http://test.com/',), {'data': {}}]
        self.assertEqual(list(post_mock.call_args), expected)

        # POST request using only the pre-made request body
        probe = POSTProbingRequest("http://test.com/", None, None,
                                   {'extra1': 0})
        probe.process()
        expected = [('http://test.com/',), {'data': {'extra1': 0}}]
        self.assertEqual(list(post_mock.call_args), expected)


    def test_invalid_req(self):
        """
        Tests invalid requests with GET and POST
        """

        # Non-existent URL
        probe = GETProbingRequest("http://nonexistenturl1234")
        self.assertRaises(requests.exceptions.ConnectionError, probe.process)

        # URL misses schema (http://)
        probe = GETProbingRequest("nonexistenturl/")
        self.assertRaises(requests.exceptions.MissingSchema, probe.process)

        # Non-existent URL
        probe = POSTProbingRequest("http://nonexistenturl1234", "test", 1)
        self.assertRaises(requests.exceptions.ConnectionError, probe.process)

        # URL misses schema (http://)
        probe = POSTProbingRequest("nonexistenturl/", "test", 1)
        self.assertRaises(requests.exceptions.MissingSchema, probe.process)

        # Invalid POST property name
        self.assertRaises(TypeError, POSTProbingRequest,
                          "http://nonexistenturl/", [], 1)

        # Invalid POST request body
        self.assertRaises(TypeError, POSTProbingRequest,
                          "http://nonexistenturl/", "test", 1, [])


if __name__ == '__main__':
    unittest.main()
