"""This module contains the ``PuppeteerMiddleware`` scrapy middleware"""

import asyncio
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
    """Downloader middleware handling the requests with Puppeteer"""

    @classmethod
    async def _from_crawler(cls, crawler):
        """Start the browser"""

        middleware = cls()
        middleware.browser = await launch({"headless": True, 'args': ['--no-sandbox'], 'dumpio':True, 'logLevel': crawler.settings.get('LOG_LEVEL')})
        page = await middleware.browser.newPage()
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware"""

        loop = asyncio.get_event_loop()
        middleware = loop.run_until_complete(
            asyncio.ensure_future(cls._from_crawler(crawler))
        )

        return middleware

    async def _process_request(self, request, spider):
        """Handle the request using Puppeteer"""

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

        # The headers must be set using request interception
        await page.setRequestInterception(True)

        @page.on('request')
        async def _handle_headers(pu_request):
            overrides = {
                'headers': {
                    k.decode(): ','.join(map(lambda v: v.decode(), v))
                    for k, v in request.headers.items()
                }
            }
            await pu_request.continue_(overrides=overrides)

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
        """Check if the Request should be handled by Puppeteer"""

        if not isinstance(request, PuppeteerRequest):
            return None

        return as_deferred(self._process_request(request, spider))

    async def _spider_closed(self):
        await self.browser.close()

    def spider_closed(self):
        """Shutdown the browser when spider is closed"""

        return as_deferred(self._spider_closed())
