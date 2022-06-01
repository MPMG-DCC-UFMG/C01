import inspect
import sys
from pyext import RuntimeModule


def generate_protected_iteration(child, module):
    """
    Generates the iteration body for iterations, while encapsulating it in a
    try/except pair
    """

    # Save the page stack length before continuing, to be able to clean up
    # later if needed
    code = ((child['depth'] + 1) * '    ') + \
        f'initial_page_stack_len{child["depth"]} = len(page_stack)\n'
    code += ((child['depth'] + 1) * '    ') + 'try:\n'

    # Indent iteration body
    for line in generate_body(child, module, True).splitlines():
        code += '    ' + line + '\n'

    code += ((child['depth'] + 1) * '    ') + 'except Exception as e:\n'
    code += ((child['depth'] + 2) * '    ') + 'print("Erro em iteração: " + str(e))\n'
    code += ((child['depth'] + 2) * '    ') + 'print("Continuando para a próxima iteração.")\n'
    # Close tabs open in this iteration and clean the stack as needed
    code += ((child['depth'] + 2) * '    ') + f'while len(page_stack) > initial_page_stack_len{child["depth"]}:\n'
    code += generate_fechar_aba({'depth': child['depth'] + 3}, module)

    return code


def generate_para_cada(child, module, skip_iter_errors):
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

    if skip_iter_errors:
        code += generate_protected_iteration(child, module)
    else:
        code += generate_body(child, module, skip_iter_errors)

    return code


def generate_se(child, module, skip_iter_errors):
    code = ''
    code += child['depth'] * '    ' + 'if '

    # if child['negation']:
    #     code += 'not '

    if 'call' in child['condition']:
        call = child['condition']['call']
        function = getattr(module, call['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        code += generate_call(call['step'], call['arguments'], is_coroutine) + ':' + '\n'
    else:
        raise TypeError('This condition is in the wrong format')

    code += generate_body(child, module, skip_iter_errors)

    return code


def generate_enquanto(child, module, skip_iter_errors):
    code = ''
    code += child['depth'] * '    ' + 'while '

    # if child['negation']:
    #     code += 'not '

    if 'call' in child['condition']:
        call = child['condition']['call']
        function = getattr(module, call['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        code += generate_call(call['step'], call['arguments'], is_coroutine) + ':' + '\n'
    else:
        raise TypeError('This condition is in the wrong format')

    if skip_iter_errors:
        code += generate_protected_iteration(child, module)
    else:
        code += generate_body(child, module, skip_iter_errors)

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
    code += child['depth'] * '    ' + 'if iframe_stack:\n'
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = page\n'
    code += child['depth'] * '    ' + "    pages[gera_nome_arquivo()] = "
    code += "await salva_pagina(**missing_arguments)\n"
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = iframe_stack[-1]\n'
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
    code += "(path=f\"{scrshot_path}/{datetime.datetime.now()}.png\", "
    code += "full_page=True)\n"
    return code


def generate_executar_em_iframe(child, module):
    xpath = child['arguments']['xpath']
    code = "\n"
    code += child['depth'] * '    ' + "### Início: Passando o contexto de execução para iframe ###\n"
    code += child['depth'] * '    ' + f'el_locator_xpath = {xpath}\n'
    code += child['depth'] * '    ' + 'el_locator = missing_arguments["pagina"].locator(f"xpath={el_locator_xpath}")\n'
    code += child['depth'] * '    ' + 'await el_locator.wait_for()\n'
    code += child['depth'] * '    ' + 'el_handler = await el_locator.first.element_handle()\n'
    code += child['depth'] * '    ' + 'iframe_stack.append(await el_handler.content_frame())\n'
    code += child['depth'] * '    ' + 'missing_arguments["pagina"] = iframe_stack[-1]\n'
    code += child['depth'] * '    ' + "### Fim: Passando o contexto de execução para iframe ###\n"
    return code


def generate_sair_de_iframe(child, module):
    code = "\n"
    code += child['depth'] * '    ' + "### Início: Saindo do contexto de iframe ###\n"
    code += child['depth'] * '    ' + 'iframe_stack.pop()\n'
    code += child['depth'] * '    ' + 'if not iframe_stack:\n'
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = page\n'
    code += child['depth'] * '    ' + 'else:\n'
    code += child['depth'] * '    ' + '    missing_arguments["pagina"] = iframe_stack[-1]\n'
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
        + "    iframe_stack = []\n"\
        + "    scrshot_path = \"" + scrshot_path + "\"\n"
    return code


def generate_body(recipe, module, skip_iter_errors):
    """
    Generates the second part of the code, that is,
    the body of the function, the steps.
    """
    thismodule = sys.modules[__name__]
    code = ""
    for child in recipe['children']:
        if hasattr(thismodule, "generate_" + child["step"]):
            args = [child, module]

            # Iterative steps and steps which can call generate_body should be
            # sent the skip_iter_errors parameter
            if child["step"] in ["para_cada", "enquanto", "se"]:
                args.append(skip_iter_errors)

            code += getattr(thismodule, "generate_" + child["step"])(*args)
        else:
            code += generate_call_step(child, module)

    return code


def generate_code(recipe, module, scrshot_path, skip_iter_errors):
    """
    Generates the entire code.
    """
    code = generate_head(module, scrshot_path)
    code += generate_body(recipe, module, skip_iter_errors)
    code += "    return pages"
    print(code)
    print('--------------------------------------------------------------------------')
    return RuntimeModule.from_string("steps", code)
