import json
import sys

sys.path.append('../../../code')
import code_generator as code_g
import atomizer as atom
from functions_file import *
import functions_file

import time
from pyppeteer import launch




async def main():
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp')

    steps = __import__('steps')
    await steps.execute_steps(page = page)

    await browser.close()
    return


with open('recipe.json') as file:
    recipe = json.load(file)

with open('steps.py', 'w+') as file:
    print(code_g.generate_code(recipe, functions_file), '\n\n\n\n')
    file.write(code_g.generate_code(recipe, functions_file))

asyncio.get_event_loop().run_until_complete(main())








