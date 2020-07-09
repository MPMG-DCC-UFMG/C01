import inspect


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
    code = ""
    for child in recipe['children']:
        if child['step'] == 'for':

            if 'call' in child['iterable']:
                is_coroutine = inspect.iscoroutinefunction(
                    getattr(module, child['iterable']['call']['step']))
                iterable = generate_call(child['iterable']['call']['step'],
                                         child['iterable']['call']
                                         ['arguments'],
                                         is_coroutine)
            elif 'object' in child['iterable']:
                iterable = '[' + ', '.join(child['iterable']['object']) + ']'
            else:
                raise TypeError('This iterable is in the wrong format')

            code += child['depth'] * '    ' \
                + 'for ' + child['iterator'] \
                + ' in '\
                + iterable\
                + ':' + '\n'
            code += generate_body(child, module)

        elif child['step'] == 'while':
            is_coroutine = inspect.iscoroutinefunction(
                getattr(module, child['condition']['step']))
            call = generate_call(child['condition']['step'],
                                 child['condition']['arguments'], is_coroutine)

            code += child['depth'] * '    ' \
                + 'while ' + call + ':' + '\n'
            code += generate_body(child, module)

        elif child['step'] == 'if':
            pass

        elif child['step'] == 'attribution':
            code += child['depth'] * '    ' + \
                child['target'] + ' = ' + str(child['source']) + '\n'
        elif child['step'] == 'para_cada_pagina_em':
            code += child['depth'] * '    '\
                + 'clickable = True' + '\n'\
                + child['depth'] * '    '\
                + 'while clickable:' + '\n'\
                + generate_body(child, module)\
                + (1 + child['depth']) * '    '\
                + "buttons = await page.xpath("+child["xpath_dos_botoes"]+")\n" \
                + (1 + child['depth']) * '    '\
                + "if len(buttons) !=0: \n" \
                + (1 + child['depth']) * '    '\
                + "    next_button = buttons["+ str(child["indice_do_botao_proximo"]) +"] \n" \
                + (1 + child['depth']) * '    '\
                + "    before_click = await page.content() \n" \
                + (1 + child['depth']) * '    '\
                + "    await next_button.click() \n" \
                + (1 + child['depth']) * '    '\
                + "    after_click = await page.content() \n" \
                + (1 + child['depth']) * '    '\
                + "    if before_click == after_click: \n" \
                + (1 + child['depth']) * '    '\
                + "        clickable = False \n" \
                + (1 + child['depth']) * '    '\
                + "else: \n" \
                + (1 + child['depth']) * '    '\
                + "    clickable = False \n" \

        elif child['step'] == 'salva_pagina':
            code += child['depth'] * '    ' + "pages[gera_nome_arquivo()] = " + \
                    "await salva_pagina(**missing_arguments)\n"

        else:
            is_coroutine = inspect.iscoroutinefunction(getattr(module,
                                                               child['step']))
            code += child['depth'] * '    ' \
                + generate_call(child['step'], child['arguments'],
                                is_coroutine) + '\n'
    return code


def generate_code(recipe, module):
    """
    Generates the entire code.
    """
    code = generate_head(module)
    code += generate_body(recipe, module)
    code += "    return pages"
    return code


