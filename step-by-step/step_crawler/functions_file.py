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


async def salva_pagina(page):
    content = await page.content()
    body = str.encode(content)
    return body


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



async def digite(page ,xpath, texto):
    await page.type(cssify(xpath), texto)



async def nesse_elemento_esta_escrito(page, xpath, texto):
    elements = await page.xpath(xpath)
    if len(elements):
        element = elements[0]
    else:
        return 0

    element_text_content = await element.getProperty('textContent')
    element_text = await (element_text_content).jsonValue()
    if texto in element_text:
        return True
    else:
        return False

