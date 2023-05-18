from pyext import RuntimeModule
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
        browser = await apw.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto('http://www.in.gov.br/web/guest/inicio')
        await page.wait_for_load_state("networkidle")

        steps = __import__('steps')
        await steps.execute_steps(page=page)
        await browser.close()
        return


with open('recipe.json') as file:
    recipe = json.load(file)

with open('steps.py', 'w+') as file:
    file.write(code_g.generate_code(recipe, functions_file))

code = code_g.generate_code(recipe, functions_file)
steps = RuntimeModule.from_string("steps", code)
print(code)

asyncio.get_event_loop().run_until_complete(main())
