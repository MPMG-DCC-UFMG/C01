import asyncio
import time

def range_(stop):
    return [i for i in range(stop)]

def print_(word):
    return word

def selecione(driver, xpath_select, opcao):
    return None

async def clique(page, xpath):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    await asyncio.wait([
        elements[0].click(),
        page.waitForNavigation(),
    ])

def espere(segs):
	time.sleep(segs)