import asyncio
import pyppeteer
import scrapy
import unittest

from typing import Any
from unittest import mock

import scrapy_puppeteer


class BrowserMock(pyppeteer.browser.Browser):
    """
    Pyppeteer browser mock to avoid passing in the required constructor
    parameters
    """

    def __init__(self):
        pass


def gen_async(result: Any = None):
    """
    Helper function to generate an async function returning the supplied
    argument

    :param result: The value to be returned by the async function

    :returns: An async function which takes any number of arguments and returns
              the supplied result
    """
    async def fn(*_, **__):
        return result
    return fn


class ScrapyPuppeteerTestCase(unittest.TestCase):
    """Test case for the ``scrapy-puppeteer`` package"""

    def setUp(self):
        """
        Sets up the testing environment, creating mocks for the required
        classes and an event loop to run the async code
        """

        self.loop = asyncio.new_event_loop()

        # Set up mock instances for Pyppeteer classes and methods

        # Response mock
        mockResponse = mock.create_autospec(pyppeteer.network_manager.Response)
        mockResponse.headers = {
            'content-type': 'text/html; charset=iso-8859-1'
        }

        self.mockResponse = mockResponse

        # CDP mock
        mockCDP = mock.create_autospec(pyppeteer.connection.CDPSession)
        mockCDP.send = mock.MagicMock(side_effect=gen_async())
        self.mockCDP = mockCDP

        # Target mock
        mockTarget = mock.create_autospec(pyppeteer.browser.Target)
        mockTarget.createCDPSession = mock.MagicMock(
            side_effect=gen_async(mockCDP))
        self.mockTarget = mockTarget

        # Page mock
        mockPage = mock.create_autospec(pyppeteer.page.Page)
        mockPage.goto = mock.MagicMock(side_effect=gen_async(mockResponse))
        mockPage.setCookie = mock.MagicMock(side_effect=gen_async(None))
        mockPage.content = mock.MagicMock(side_effect=gen_async(""))
        mockPage.close = mock.MagicMock(side_effect=gen_async(None))
        mockPage.screenshot = mock.MagicMock(side_effect=gen_async(None))
        mockPage.waitFor = mock.MagicMock(side_effect=gen_async(None))
        mockPage.url = "http://example.com"
        mockPage._target = mockTarget
        self.mockPage = mockPage

        # Create the network manager client, which is used internally
        networkClient = mock.create_autospec(pyppeteer.connection.CDPSession)
        networkClient.send = mock.MagicMock(side_effect=gen_async(None))
        self.mockPage._networkManager = mock.MagicMock(_client=networkClient)

        # Browser mock
        mockBrowser = mock.create_autospec(BrowserMock)
        mockBrowser.newPage = mock.MagicMock(side_effect=gen_async(mockPage))
        mockBrowser.close = mock.MagicMock(side_effect=gen_async(None))
        self.mockBrowser = mockBrowser

        # Request mock
        self.mockRequest = mock.create_autospec(
            scrapy_puppeteer.PuppeteerRequest,
            cookies={},
            url="http://example.com",
            wait_until="load",
            wait_for=False,
            screenshot=False,
            steps=False
        )

        # Spider mock
        self.mockSpider = mock.create_autospec(scrapy.Spider)


    def tearDown(self):
        """
        Closes the event loop created during setup
        """
        self.loop.close()


    def assert_default_calls(self, mockLaunch: mock.MagicMock):
        """
        Asserts that the minimum required calls have been called

        :param mockLaunch: mock of the launch function from Pyppeteer
        """

        # launch should be called once
        mockLaunch.assert_called_once()
        # browser.newPage should be called
        self.mockBrowser.newPage.assert_called()
        # page.setCookie should be called once
        self.mockPage.setCookie.assert_called_once()
        # Page content should be loaded
        self.mockPage.content.assert_called_once()
        # Page should be closed once
        self.mockPage.close.assert_called_once()
        # Request interception routine should be set up
        self.mockPage._networkManager._client.on.assert_called()
        self.mockPage._networkManager._client.send.assert_called()


    def test_process_request_run_with_no_extra_options(self):
        """
        Tests if the process_request interface works as intended when no extra
        operations are required
        """

        with mock.patch('scrapy_puppeteer.middlewares.launch',
                side_effect=gen_async(self.mockBrowser)) as mockLaunch:

            middleware = scrapy_puppeteer.PuppeteerMiddleware()
            f = middleware._process_request(self.mockRequest, self.mockSpider)
            d = self.loop.run_until_complete(f)

            self.assert_default_calls(mockLaunch)

            # page.screenshot shouldn't be called
            self.mockPage.screenshot.assert_not_called()
            # page.waitFor shouldn't be called
            self.mockPage.waitFor.assert_not_called()


    def test_process_request_run_and_screenshot(self):
        """
        Tests if the process_request interface works as intended when a
        screenshot is requested
        """

        with mock.patch('scrapy_puppeteer.middlewares.launch',
                side_effect=gen_async(self.mockBrowser)) as mockLaunch:

            # Enable the screenshot feature
            self.mockRequest.screenshot = True

            middleware = scrapy_puppeteer.PuppeteerMiddleware()
            f = middleware._process_request(self.mockRequest, self.mockSpider)
            d = self.loop.run_until_complete(f)

            self.assert_default_calls(mockLaunch)

            # page.screenshot should be called once
            self.mockPage.screenshot.assert_called_once()
            # page.waitFor shouldn't be called
            self.mockPage.waitFor.assert_not_called()


    def test_process_request_run_and_wait_for(self):
        """
        Tests if the process_request interface works as intended when the
        wait_for option is supplied
        """

        with mock.patch('scrapy_puppeteer.middlewares.launch',
                side_effect=gen_async(self.mockBrowser)) as mockLaunch:

            # Enable the wait_for feature
            self.mockRequest.wait_for = True

            middleware = scrapy_puppeteer.PuppeteerMiddleware()
            f = middleware._process_request(self.mockRequest, self.mockSpider)
            d = self.loop.run_until_complete(f)

            self.assert_default_calls(mockLaunch)

            # page.screenshot shouldn't be called
            self.mockPage.screenshot.assert_not_called()
            # page.waitFor should be called once
            self.mockPage.waitFor.assert_called_once()


    @mock.patch('scrapy_puppeteer.middlewares.code_g')
    def test_process_request_run_with_steps(self, mockCode_g):
        """
        Tests if the process_request interface works as intended when dynamic
        steps are supplied

        :param mockCode_g: mock of the code_generator module inside
                           scrapy_puppeteer
        """

        # Create mock steps object
        mockSteps = mock.MagicMock()
        mockSteps.execute_steps = mock.MagicMock(side_effect=gen_async(None))
        # Mock the generate_code function to return our mocked steps object
        mockCode_g.generate_code = mock.MagicMock(return_value=mockSteps)

        with mock.patch('scrapy_puppeteer.middlewares.launch',
                side_effect=gen_async(self.mockBrowser)) as mockLaunch:

            # Enable the steps feature (dummy entry just to check function
            # calls)
            self.mockRequest.steps = {"test": True}

            middleware = scrapy_puppeteer.PuppeteerMiddleware()
            f = middleware._process_request(self.mockRequest, self.mockSpider)
            d = self.loop.run_until_complete(f)

            self.assert_default_calls(mockLaunch)

            # page.screenshot shouldn't be called
            self.mockPage.screenshot.assert_not_called()
            # page.waitFor shouldn't be called
            self.mockPage.waitFor.assert_not_called()
            # The methods for step generation and execution should be called
            mockCode_g.generate_code.assert_called_once()
            mockSteps.execute_steps.assert_called_once_with(pagina=self.mockPage)


    def test_middleware_closes_browser(self):
        """
        Tests if the middleware properly closes the browser when requested
        """

        middleware = scrapy_puppeteer.PuppeteerMiddleware()
        middleware.browser = self.mockBrowser
        f = middleware._spider_closed()
        d = self.loop.run_until_complete(f)

        # browser.close should be called
        self.mockBrowser.close.assert_called_once()


    def test_middleware_generated_from_crawler(self):
        """
        Tests if the from_crawler method loads the browser correctly
        """

        with mock.patch('scrapy_puppeteer.middlewares.launch',
                side_effect=gen_async(self.mockBrowser)) as mockLaunch:

            self.mockSpider.settings = {
                "CRAWLER_ID": 1,
                "INSTANCE_ID": 1,
                "DATA_PATH": 'test',
                "OUTPUT_FOLDER": '/data'
            }
            self.mockSpider.signals = mock.MagicMock()
            f = scrapy_puppeteer.PuppeteerMiddleware._from_crawler(
                self.mockSpider
            )
            result = self.loop.run_until_complete(f)

            # The result should be an instance of the middleware
            self.assertIsInstance(result, scrapy_puppeteer.PuppeteerMiddleware)
            # The download path should be set properly
            self.assertEqual(result.download_path, '/data/test/1/data/files')
            # launch should be called once
            mockLaunch.assert_called_once()
            # browser.newPage should be called once
            self.mockBrowser.newPage.assert_called_once()
            # crawler.signals.connect should be called once with the expected
            # arguments
            self.mockSpider.signals.connect.assert_called_once_with(
                result.spider_closed,
                scrapy.signals.spider_closed
            )
