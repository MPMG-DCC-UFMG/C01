"""This module contains the ``PuppeteerMiddleware`` scrapy middleware"""
import asyncio
from hashlib import new
from crawling_utils import crawling_utils
from twisted.internet import asyncioreactor

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    asyncioreactor.install(loop)
except Exception:
    pass
import logging
import requests

import base64
import sys
import os
import time
from glob import glob
import shutil

from step_crawler import code_generator as code_g
from step_crawler import functions_file
from step_crawler.functions_file import *
from step_crawler import atomizer as atom
from pyppeteer import launch
from scrapy import signals
from scrapy.http import HtmlResponse
from twisted.internet.defer import AlreadyCalledError, Deferred
from promise import Promise
from scrapy.exceptions import CloseSpider, IgnoreRequest
from pyppeteer import __chromium_revision__

from .http import PuppeteerRequest
from .chromium_downloader import chromium_executable

import crawling_utils

# For the system to wait up to TIMEOUT_TO_DOWNLOAD_START
# seconds for a download to start. The value below is arbitrary
TIMEOUT_TO_DOWNLOAD_START = 7

def as_deferred(f):
    """Transform a Twisted Deffered to an Asyncio Future"""

    return Deferred.fromFuture(asyncio.ensure_future(f))


class PuppeteerMiddleware:
    """Downloader middleware handling the requests with Puppeteer

    More info about middlewares structure:
    https://docs.scrapy.org/en/latest/topics/spider-middleware.html#writing-your-own-spider-middleware
    """

    @classmethod
    async def _from_crawler(cls, crawler):
        """Start the browser

        :crawler(Crawler object): crawler that uses this middleware
        """

        middleware = cls()
        middleware.browser = None#await launch({"headless": True, 'args': ['--no-sandbox'], 'dumpio':True, 'logLevel': crawler.settings.get('LOG_LEVEL')})
        middleware.download_path = None
        # page = await middleware.browser.newPage()

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware

        :crawler(Crawler object): crawler that uses this middleware
        """

        loop = asyncio.get_event_loop()
        middleware = loop.run_until_complete(
            asyncio.ensure_future(cls._from_crawler(crawler))
        )

        return middleware

    async def block_until_complete_downloads(self):
        """Blocks the flow of execution until all files are downloaded.
        """

        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path) 

        def exists_pendent_downloads():
            # Pending downloads in chrome have the .crdownload extension. 
            # So, if any of these files exist, we know that a download is running.
            pendend_downloads = glob(f'{self.download_path}*.crdownload')
            return len(pendend_downloads) > 0  

        for _ in range(TIMEOUT_TO_DOWNLOAD_START):
            await asyncio.sleep(1)
            if exists_pendent_downloads():
                break

        while exists_pendent_downloads():
            await asyncio.sleep(1)

    async def _process_request(self, request, spider):
        """Handle the request using Puppeteer

        :request: The PuppeteerRequest object sent by the spider
        :spider: The spider using this middleware
        """

        try:
            page = await self.browser.newPage()

        except:
            crawler_id = request.meta['config']['crawler_id']

            # Folder where the files downloaded from this crawl will be temporarily
            # dp : dynamic processing
            self.download_path = os.path.join(os.getcwd(), f'temp_dp/{crawler_id}/') 

            self.browser = await launch(executablePath=chromium_executable())
            await self.browser.newPage()

            page = await self.browser.newPage()

            cdp = await page._target.createCDPSession()
            await cdp.send('Browser.setDownloadBehavior', { 'behavior': 'allow', 'downloadPath': self.download_path })

        downloads_processing = set(glob(f'{self.download_path}*'))

        # Cookies
        if isinstance(request.cookies, dict):
            await page.setCookie(*[
                {'name': k, 'value': v}
                for k, v in request.cookies.items()
            ])
        else:
            await page.setCookie(request.cookies)

        # The request method and data must be set using request interception
        # For some reason the regular method with setRequestInterception and
        # page.on('request', callback) doesn't work, I had to use this instead.
        # This directly manipulates the lower level modules in the pyppeteer
        # page to achieve the results. Details on this workaround here (I have
        # changed the code so it no longer uses the deprecated 'Network'
        # domain, using 'Fetch' instead):
        # https://github.com/pyppeteer/pyppeteer/issues/198#issuecomment-750221057
        async def setup_request_interceptor(page) -> None:
            client = page._networkManager._client

            async def intercept(event) -> None:
                request_id = event["requestId"]

                try:
                    int_req = event["request"]
                    url = int_req["url"]

                    options = {"requestId": request_id}
                    options['method'] = request.method

                    if request.body:
                        # The post data must be base64 encoded
                        b64_encoded = base64.b64encode(request.body)
                        options['postData'] = b64_encoded.decode('utf-8')

                    await client.send("Fetch.continueRequest", options)
                except:
                    # If everything fails we need to be sure to continue the
                    # request anyway, else the browser hangs
                    options = {
                        "requestId": request_id,
                        "errorReason": "BlockedByClient"
                    }
                    await client.send("Fetch.failRequest", options)


            # Setup request interception for all requests.
            client.on("Fetch.requestPaused",
                lambda event: client._loop.create_task(intercept(event)),
            )

            # Set this up so that only the initial request is intercepted
            # (else it would capture requests for external resources such as
            # scripts, stylesheets, images, etc)
            patterns = [{"urlPattern": request.url}]
            await client.send("Fetch.enable", {"patterns": patterns})

        async def stop_request_interceptor(page) -> None:
            await page._networkManager._client.send("Fetch.disable")

        await setup_request_interceptor(page)

        try:
            response = await page.goto(
                request.url,
                {
                    'waitUntil': request.wait_until,
                },
            )

        except:
            await page.close()
            raise IgnoreRequest()

        # Stop intercepting following requests
        await stop_request_interceptor(page)

        if request.screenshot:
            request.meta['screenshot'] = await page.screenshot()

        if request.wait_for:
            await page.waitFor(request.wait_for)

        if request.steps:
            steps = code_g.generate_code(request.steps, functions_file)
            request.meta["pages"] = await steps.execute_steps(page=page)

        content = await page.content()
        body = str.encode(content)

        await self.block_until_complete_downloads()
        await page.close()

        url_hash = crawling_utils.hash(request.url.encode())
        new_downloads = set(glob(f'{self.download_path}*')) - downloads_processing

        for download_path in new_downloads:
            s_download_path = download_path.split('/')

            filename = s_download_path[-1]
            filename_renamed =  '/'.join(s_download_path[:-1]) + f'/{url_hash}_{filename}'

            os.rename(download_path, filename_renamed)

        # Necessary to bypass the compression middleware (?)
        response.headers.pop('content-encoding', None)
        response.headers.pop('Content-Encoding', None)

        return HtmlResponse(
            page.url,
            status=response.status,
            headers=response.headers,
            body=body,
            encoding='utf-8',
            request=request,
        )

    def process_request(self, request, spider):
        """Check if the Request should be handled by Puppeteer

        :request: The request object sent by the spider
        :spider: The spider using this middleware
        """

        if not isinstance(request, PuppeteerRequest):
            return None

        return as_deferred(self._process_request(request, spider))

    async def _spider_closed(self):
        await self.browser.close()

    def spider_closed(self):
        """Shutdown the browser when spider is closed"""
        
        # delete the temporarily folder 
        shutil.rmtree(self.download_path, ignore_errors=True)

        return as_deferred(self._spider_closed())
