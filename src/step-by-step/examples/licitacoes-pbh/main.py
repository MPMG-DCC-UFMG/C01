import json

from step_crawler import code_generator as code_g
from step_crawler import functions_file
from step_crawler.functions_file import *
from pyppeteer import launch


async def main():
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('https://prefeitura.pbh.gov.br/licitacoes')

    steps = code_g.generate_code(recipe, functions_file)
    _ = await steps.execute_steps(page=page)

    await browser.close()
    return


with open('recipe.json') as file:
    recipe = json.load(file)

asyncio.get_event_loop().run_until_complete(main())
