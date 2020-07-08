import asyncio
import time
import uuid


def range_(stop):
    return [i for i in range(stop)]


def print_(word):
    return word


def espere(segs):
    time.sleep(segs)

def gera_nome_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)

async def wait_page(page):
    jsWait = "document.readyState === 'complete' || \
              document.readyState === 'iteractive'"
    while not (await page.evaluate(jsWait)):
        await page.waitFor(1)

async def clique(page, xpath):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    await asyncio.wait([
        elements[0].click(),
        #page.waitForNavigation(),
    ])

async def opcoes(page, xpath, exceto = []):
    option_values = []
    await page.waitForXPath(xpath)
    options = await page.xpath(xpath + "/option")
    for option in options:
        value = await option.getProperty("text")
        option_values.append(value.toString().split(":")[-1])
    return [value for value in option_values if value not in exceto]

async def selecione(page, xpath, opcao):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    select = elements[0]
    await select.type(opcao)


async def salva_pagina(page, path):
    content = await page.content()
    body = str.encode(content)
    with open(path, "w") as page_file:
        page_file.write(body)

async def elementos_nesse_xpath(page, xpath):
    await page.waitForXPath(xpath)
    elements = await page.xpath(xpath)
    return [await element.getProperties() for element in elements]

def espere(segs):
	time.sleep(segs)


async def for_clicavel(page, xpath):
    try:
        await clique(page,xpath)
        return 1
    except:
        print('error')
        return 0


