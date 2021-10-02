import asyncio

import time
from pyppeteer import launch

from .chromium_downloader import chromium_executable

CONTENT_EMPTY = '<head></head><body></body>'

async def async_iframe_loader(url: str, xpath: str, max_attempts: int = 5) -> str:
    wait_time = 1.5

    browser = await launch({'handleSIGINT': False,
                            'handleSIGTERM': False,
                            'handleSIGHUP': False,
                            'headless': True})

    page = await browser.newPage()

    await page.goto(url)
    await page.waitForXPath(xpath)
    
    el_handlers = await page.xpath(xpath)
    iframe = await el_handlers[0].contentFrame()

    attempt = 1
    error = None
    while attempt <= max_attempts:
        try:

            time.sleep(wait_time * attempt)

            # Extract the content inside the iframe
            content = await iframe.evaluate('''
                () => {
                    const el = document.querySelector("*");
                    return el.innerHTML;
                }
            ''')

            if content == CONTENT_EMPTY:
                attempt += 1

            else:
                break

        except Exception as e:
            attempt += 1 
            error = e

    await browser.close()

    if attempt == max_attempts:
        raise error

    return content

def iframe_loader(url: str, xpath: str):
    try:
        loop = asyncio.get_event_loop()
        
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop = asyncio.get_event_loop()
    coroutine = async_iframe_loader(url, xpath)
    content = loop.run_until_complete(coroutine)
    return content