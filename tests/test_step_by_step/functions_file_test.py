"""
This module tests the functions_file code inside the step-by-step module
"""
from step_crawler import functions_file

from playwright.async_api._generated import Page

import asyncio
import unittest

class FunctionsFileTest(unittest.TestCase):
    """
    Testing routines for the step definitions. We use the mock module to create
    mocks of the Playwright pages.
    """

    def setUp(self):
        """
        Sets up the testing environment, creating an event loop to run the
        async code
        """

        # monkey patch MagicMock (https://stackoverflow.com/a/51399767/2825167)
        async def async_magic():
            pass

        unittest.mock.MagicMock.__await__ = lambda x: async_magic().__await__()

        self.loop = asyncio.new_event_loop()

    def tearDown(self):
        """
        Closes the event loop created during setup
        """
        self.loop.close()

    def test_execute_javascript(self):
        page = unittest.mock.create_autospec(Page)
        js_code = 'alert("test")'

        self.loop.run_until_complete(
            functions_file.run_javascript(page, js_code)
        )

        page.evaluate.assert_called_once_with(js_code)
