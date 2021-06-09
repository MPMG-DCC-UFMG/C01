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


    ## problema com a profundidade provavelmente é no python, a informação depth já existe
    ## colocar child['depth'] * '    '  na hora de fazer passo filho 
    code += child['depth'] * '    ' + 'for ' + child['iterator']
    code += ' in ' + iterable_statement + ':' + '\n'
    code += generate_body(child, module)
    return code


def generate_if(child, module):
    code = ''
    code += child['depth'] * '    ' + 'if '
    if child['negation']:
        code += 'not '
    if 'call' in child['condition']:
        call = child['condition']['call']
        function = getattr(module, call['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        code += generate_call(call['step'], call['arguments'], is_coroutine)
        code += ':\n'
    elif 'comparison' in child['condition']:
        code += child['condition']['comparison'] + ':\n'
    else:
        raise TypeError('This condition is in the wrong format')

    code += generate_body(child, module)

    return code


def generate_while(child, module):
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


def generate_attribution(child, module):
    code = ""
    code += child['depth'] * '    ' + child['target']
    code += ' = ' + str(child['source']) + '\n'
    return code


def generate_para_cada_pagina_em(child, module):
    code = ""
    code += child['depth'] * '    ' + 'clickable = True' + '\n'\
        + child['depth'] * '    ' + 'while clickable:' + '\n'\
        + generate_body(child, module)\
        + (1 + child['depth']) * '    ' + "buttons = await page.xpath("\
        + child["xpath_dos_botoes"] + ")\n"\
        + (1 + child['depth']) * '    ' + "if len(buttons) !=0: \n"\
        + (1 + child['depth']) * '    ' + "    next_button = buttons["\
        + str(child["indice_do_botao_proximo"]) + "] \n"\
        + (1 + child['depth']) * '    '\
        + "    before_click = await page.content()\n"\
        + (1 + child['depth']) * '    '\
        + "    await next_button.click() \n"\
        + (1 + child['depth']) * '    '\
        + "    after_click = await page.content() \n"\
        + (1 + child['depth']) * '    '\
        + "    if before_click == after_click: \n"\
        + (1 + child['depth']) * '    '\
        + "        clickable = False \n"\
        + (1 + child['depth']) * '    ' + "else: \n"\
        + (1 + child['depth']) * '    ' + "    clickable = False \n"
    return code


def generate_salva_pagina(child, module):
    code = ""
    code += child['depth'] * '    ' + "pages[gera_nome_arquivo()] = "
    code += "await salva_pagina(**missing_arguments)\n"
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
        # considerar se a chama é de string ou se é de variável, na vdd as aspas é para o parametro
    return call


def generate_head(module):
    """
    Generates the first part of the code, that is,
    imports and function signature.
    TODO: refactor
    """
    code = "import step_crawler\n"
    code += "from " + module.__name__ + " import *\n\n"
    code += "async def execute_steps(**missing_arguments):\n"\
        + "    pages = {}\n"\
        + "    page = missing_arguments['page']\n"
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


def generate_code(recipe, module):
    """
    Generates the entire code.
    """
    code = generate_head(module)
    code += generate_body(recipe, module)
    code += "    return pages"
    print(code)
    return RuntimeModule.from_string("steps", code)
