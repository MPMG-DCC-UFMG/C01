import inspect
import step_crawler.code_generator as cg


def generate_para_cada(child, module):
    code = ""
    if 'call' in child['iterable']:
        function_info = child['iterable']['call']
        function = getattr(module, function_info['step'])
        is_coroutine = inspect.iscoroutinefunction(function)
        iterable_statement = cg.generate_call(function_info['step'],
                                          function_info['arguments'],
                                          is_coroutine)
    elif 'object' in child['iterable']:
        iterable_statement = '[' + ', '.join([str(item) for item in child['iterable']['object']]) + ']'
    else:
        raise TypeError('This iterable is in the wrong format')

    code += child['depth'] * '    ' + 'for ' + child['iterator']
    code += ' in ' + iterable_statement + ':' + '\n'
    code += cg.generate_body(child, module)
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
        code += cg.generate_call(call['step'], call['arguments'], is_coroutine)
        code += ':\n'
    elif 'comparison' in child['condition']:
        code += child['condition']['comparison'] + ':\n'
    else:
        raise TypeError('This iterable is in the wrong format')

    code += cg.generate_body(child, module)

    return code


def generate_while(child, module):
    condition_call_name = getattr(module, child['condition']['step'])
    is_coroutine = inspect.iscoroutinefunction(condition_call_name)
    call = cg.generate_call(child['condition']['step'],
                         child['condition']['arguments'],
                         is_coroutine)

    code += child['depth'] * '    '
    code += 'while ' + call + ':' + '\n'
    code += cg.generate_body(child, module)
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
        + cg.generate_body(child, module)\
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
        + cg.generate_call(child['step'], child['arguments'],
                        is_coroutine) + '\n'
    return code
