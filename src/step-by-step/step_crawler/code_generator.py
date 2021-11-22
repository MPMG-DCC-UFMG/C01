import inspect
import sys
from pyext import RuntimeModule


def generate_para_cada(child, module):
    code = ""
    if 'call' in child['iterable']:
        function_info = child['iterable']['call']
        function = getattr(module, function_info['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        iterable_statement = generate_call(function_info['step'],
                                          function_info['arguments'],
                                          is_coroutine)
    elif 'object' in child['iterable']:
        iterable_statement = '[' + ', '.join([str(item) for item in child['iterable']['object']]) + ']'
    else:
        raise TypeError('This iterable is in the wrong format')

    code += child['depth'] * '    ' + 'for ' + child['iterator']
    code += ' in ' + iterable_statement + ':' + '\n'
    code += generate_body(child, module)
    return code


def generate_elemento_existe_na_pagina(child, module):
    code = ''
    code += child['depth'] * '    ' + 'if '
    if child['arguments'] != '':
        call = child
        function = getattr(module, call['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        code += generate_call(call['step'], call['arguments'], is_coroutine)
        code += ':\n'
    else:
        raise TypeError('This condition is in the wrong format')

    code += generate_body(child, module)

    return code


def generate_enquanto(child, module):
    code = ''
    if 'limit' in child['condition']:
        code += child['depth'] * '    ' + 'limit = 0\n'
    code += child['depth'] * '    ' + 'while '

    if child['negation']:
        code += 'not '

    if 'call' in child['condition']:
        call = child['condition']['call']
        function = getattr(module, call['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        code += generate_call(call['step'], call['arguments'], is_coroutine)
    elif 'comparison' in child['condition']:
        code += child['condition']['comparison']
    else:
        raise TypeError('This condition is in the wrong format')

    if 'limit' in child['condition']:
        code += ' and limit < ' + str(child['condition']['limit'])
        code += ':\n'
        code += (child['depth'] + 1) * '    ' + 'limit += 1\n'
    else:
        code += ':\n'

    code += generate_body(child, module)
    return code


def generate_atribuicao(child, module):
    code = ""
    code += child['depth'] * '    ' + child['target']
    if type(child['source']) == dict and 'call' in child['source']:
        function_info = child['source']['call']
        function = getattr(module, function_info['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        source_statement = generate_call(function_info['step'],
                                         function_info['arguments'],
                                         is_coroutine)
        code += ' = ' + source_statement + '\n'
    else:
        code += ' = ' + str(child['source']) + '\n'
    return code


def generate_salva_pagina(child, module):
    code = ""
    code += child['depth'] * '    ' + 'if iframe is not None:\n'
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = page\n'
    code += child['depth'] * '    ' + "    pages[gera_nome_arquivo()] = "
    code += "await salva_pagina(**missing_arguments)\n"
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = iframe\n'
    code += child['depth'] * '    ' + 'else:\n'
    code += child['depth'] * '    ' + "    pages[gera_nome_arquivo()] = "
    code += "await salva_pagina(**missing_arguments)\n"
    return code


def generate_abrir_em_nova_aba(child, module):
    code = ""
    code += child['depth'] * '    ' + 'page_stack.append(page)\n'
    code += child['depth'] * '    ' + \
        'missing_arguments["pagina"] = await open_in_new_tab(**missing_arguments, ' + \
        'link_xpath = ' + child['link_xpath'] + ')\n'
    code += child['depth'] * '    ' + 'page = missing_arguments["pagina"]\n'
    return code


def generate_fechar_aba(child, module):
    code = ""
    code += child['depth'] * '    ' + 'await page.close()\n'
    code += child['depth'] * '    ' + 'missing_arguments["pagina"] = page_stack.pop()\n'
    code += child['depth'] * '    ' + 'page = missing_arguments["pagina"]\n'
    return code


def generate_screenshot(child, module):
    code = ""
    code += child['depth'] * '    ' + "await page.screenshot"
    code += "({'path': f\"{scrshot_path}/{datetime.datetime.now()}.png\", "
    code += "'fullPage': True })\n"
    return code


def generate_executar_em_iframe(child, module):
    xpath = child['arguments']['xpath']

    code = "\n"
    code += child['depth'] * '    ' + "### Início: Passando o contexto de execução para iframe ###\n"
    code += child['depth'] * '    ' + 'page_stack.append(page)\n'
    code += child['depth'] * '    ' + f'await page.waitForXPath({xpath})\n'
    code += child['depth'] * '    ' + f'el_handlers = await page.xpath({xpath})\n'
    code += child['depth'] * '    ' + f'iframe = await el_handlers[0].contentFrame()\n'
    code += child['depth'] * '    ' + 'missing_arguments["pagina"] = iframe\n'
    code += child['depth'] * '    ' + "### Fim: Passando o contexto de execução para iframe ###\n"
    return code


def generate_horizontal_scroll(child,module):
    code = "\n"
    code += child['depth'] * '    ' + "keep_running = True\n"
    code += child['depth'] * '    ' + "while keep_running:\n"
    code += (child['depth'] + 1) * '    ' + "keep_running = await page.evaluate('''() => { let table = $('.tableExContainer .bodyCells')[0]; let tableVisibleWidth = table.offsetWidth; let lastLeftOffset = table.scrollLeft;table.scrollLeft += tableVisibleWidth; return lastLeftOffset != table.scrollLeft}''')\n\n"

    return code

def generate_vertical_scroll(child,module):
    code = "\n"
    code += child['depth'] * '    ' + "table = ''\n"
    code += child['depth'] * '    ' + "while True:\n"
    code += (child['depth'] + 1) * '    ' + "keep_running, content = await page.evaluate('''() => { let table = $('.tableExContainer .bodyCells')[0]; let tableVisibleHeight = table.offsetHeight; let lastTopOffset = table.scrollTop; table.scrollTop += tableVisibleHeight; return [lastTopOffset != table.scrollTop, table.innerHTML]; } ''')\n\n"
    code += (child['depth'] + 1) * '    ' + "if keep_running:\n"
    code += (child['depth'] + 2) * '    ' + "table += '' + content\n"
    code += (child['depth'] + 1) * '    ' + "else:\n"
    code += (child['depth'] + 2) * '    ' + "break\n"
    code += (child['depth'] + 1) * '    ' + "time.sleep(1)\n\n"
    code += child['depth'] * '    ' + "with open('table_iframe.html', 'a') as f:\n"
    code += (child['depth'] + 1) * '    ' + "f.write(table)\n\n"    
    return code

def generate_sair_de_iframe(child, module):
    code = "\n"
    code += child['depth'] * '    ' + "### Início: Saindo do contexto de iframe ###\n"
    code += child['depth'] * '    ' + 'missing_arguments["pagina"] = page\n'
    code += child['depth'] * '    ' + 'iframe = None\n'
    code += child['depth'] * '    ' + "### Fim: Saindo do contexto de iframe ###\n\n"
    return code


def generate_call_step(child, module):
    code = ""
    is_coroutine = inspect.iscoroutinefunction(getattr(module,
                                                       child['step']))
    code += child['depth'] * '    ' \
        + generate_call(child['step'], child['arguments'],
                        is_coroutine) + '\n'
    return code


def dict_to_arguments(dict_of_arguments):
    """
    Generates a string that represents a parameter pass
    """
    return ', '.join([key + ' = ' + str(dict_of_arguments[key]) for key
                      in dict_of_arguments])


def generate_call(function_name, dict_of_arguments, is_coroutine=False):
    """
    Generates a string that represents a call function
    """
    call = function_name
    if is_coroutine:
        call = 'await ' + call + '(**missing_arguments, ' + \
               dict_to_arguments(dict_of_arguments) + ')'
    else:
        call = call + '(' + dict_to_arguments(dict_of_arguments) + ')'
    return call


def generate_head(module, scrshot_path):
    """
    Generates the first part of the code, that is,
    imports and function signature.
    TODO: refactor
    """
    code = "import step_crawler\n"
    code += "from " + module.__name__ + " import *\n\n"
    code += "async def execute_steps(**missing_arguments):\n"\
        + "    pages = {}\n"\
        + "    page = missing_arguments['pagina']\n"\
        + "    page_stack = []\n"\
        + "    iframe = None\n"\
        + "    scrshot_path = \"" + scrshot_path + "\"\n"
    return code

def generate_body(recipe, module):
    """
    Generates the second part of the code, that is,
    the body of the function, the steps.
    """
    thismodule = sys.modules[__name__]
    code = ""
    for child in recipe['children']:
        if hasattr(thismodule, "generate_" + child["step"]):
            code += getattr(thismodule, "generate_" + child["step"])(child, module)
        else:
            code += generate_call_step(child, module)

    return code


def generate_code(recipe, module, scrshot_path):
    """
    Generates the entire code.
    """
    code = generate_head(module, scrshot_path)
    code += generate_body(recipe, module)
    code += "    return pages"
    print(code)
    print('--------------------------------------------------------------------------')
    return RuntimeModule.from_string("steps", code)
