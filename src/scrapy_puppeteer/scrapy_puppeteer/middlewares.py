"""This module contains the ``PuppeteerMiddleware`` scrapy middleware"""
import asyncio
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
import sys, os, time

from step_crawler import code_generator as code_g
from step_crawler import functions_file
from step_crawler.functions_file import *
from step_crawler import atomizer as atom
from pyppeteer import launch
from scrapy import signals
from scrapy.http import HtmlResponse
from twisted.internet.defer import Deferred
from promise import Promise
from scrapy.exceptions import CloseSpider, IgnoreRequest

from .http import PuppeteerRequest


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
        middleware.browser = await launch({"headless": True, 'args': ['--no-sandbox'], 'dumpio':True, 'logLevel': crawler.settings.get('LOG_LEVEL')})
        page = await middleware.browser.newPage()
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

    async def _process_request(self, request, spider):
        """Handle the request using Puppeteer

        :request: The PuppeteerRequest object sent by the spider
        :spider: The spider using this middleware
        """

        try:
            page = await self.browser.newPage()
        except:
            self.browser = await launch({"headless": True, 'args': ['--no-sandbox'], 'dumpio':True})
            await self.browser.newPage()
            page = await self.browser.newPage()

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
        # page to achieve the results. Details on this workaround here:
        # https://github.com/pyppeteer/pyppeteer/issues/198#issuecomment-750221057
        async def setup_request_interceptor(page) -> None:
            client = page._networkManager._client

            async def intercept(event) -> None:
                interception_id = event["interceptionId"]

                try:
                    int_req = event["request"]
                    url = int_req["url"]

                    options = {"interceptionId": interception_id}
                    options['method'] = request.method

                    if request.body:
                        options['postData'] = request.body.decode('utf-8')

                    await client.send("Network.continueInterceptedRequest",\
                        options)
                except:
                    # If everything fails we need to be sure to continue the
                    # request anyway, else the browser hangs
                    options = {
                        "interceptionId": interception_id,
                        "errorReason": "BlockedByClient"
                    }
                    await client.send("Network.continueInterceptedRequest",\
                        options)


            # Setup request interception for all requests.
            client.on(
                "Network.requestIntercepted",
                lambda event: client._loop.create_task(intercept(event)),
            )

            # Set this up so that only the initial request is intercepted
            # (else it would capture requests for external resources such as
            # scripts, stylesheets, images, etc)
            patterns = [{"urlPattern": request.url}]
            await client.send("Network.setRequestInterception", \
                {"patterns": patterns})

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

        if request.screenshot:
            request.meta['screenshot'] = await page.screenshot()

        if request.wait_for:
            await page.waitFor(request.wait_for)

        if request.steps:
            steps = code_g.generate_code(request.steps, functions_file)
            request.meta["pages"] = await steps.execute_steps(page=page)

        content = await page.content()
        body = str.encode(content)

        await page.close()

        # Necessary to bypass the compression middleware (?)
        response.headers.pop('content-encoding', None)
        response.headers.pop('Content-Encoding', None)

        return HtmlResponse(
            page.url,
            status=response.status,
            headers=response.headers,
            body=body,
            encoding='utf-8',
            request=request
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

        return as_deferred(self._spider_closed())
