import asyncio
import time
import uuid
from cssify import cssify


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
    await page.click(cssify(xpath))
    await wait_page(page)


async def selecione(page, xpath, opcao):
    await page.waitForXPath(xpath)
    await page.type(cssify(xpath), opcao)
    await wait_page(page)


async def salva_pagina(page, path):
    content = await page.content()
    body = str.encode(content)
    with open(path, "w") as page_file:
        page_file.write(body)

async def opcoes(page, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []
    await page.waitForXPath(xpath)
    for option in (await page.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


async def for_clicavel(page, xpath):
    try:
        await clique(page, xpath)
        return True
    except:
        return False



