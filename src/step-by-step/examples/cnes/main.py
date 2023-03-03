from pyext import RuntimeModule
from step_crawler import atomizer as atom
from step_crawler.functions_file import *
from step_crawler import functions_file
from step_crawler import code_generator as code_g
from playwright.async_api import async_playwright

import asyncio
import json

import sys
sys.path.append("../../../")


async def main():
    async with async_playwright() as apw:
        browser = await apw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp')
        await page.wait_for_load_state("networkidle")

        steps = code_g.generate_code(recipe, functions_file)
        pages = await steps.execute_steps(page=page)

        await browser.close()
        return

with open('recipe.json') as file:
    recipe = json.load(file)


asyncio.get_event_loop().run_until_complete(main())
