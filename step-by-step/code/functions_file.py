import asyncio
import time

def range_(stop):
    return [i for i in range(stop)]

def print_(word):
    return word

async def clique(page, xpath):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    await asyncio.wait([
        elements[0].click(),
        page.waitForNavigation(),
    ])

async def opcoes(page, xpath):
    option_values = []
    await page.waitForXPath(xpath)
    options = await page.xpath(xpath + "/option")
    for option in options:
        value = await option.getProperty("text")
        option_values.append(value.toString().split(":")[-1])
    return option_values

async def selecione(page, xpath, opcao):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    select = elements[0]
    await select.type(opcao)


async def elementos_nesse_xpath(page, xpath):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    return [await element.getProperties() for element in elements]

def wait(segs):
	time.sleep(segs)
