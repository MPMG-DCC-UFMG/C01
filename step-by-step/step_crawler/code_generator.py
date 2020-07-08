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
    code = code + "from " + module.__name__ + " import *\n\n"
    code = code + "async def execute_steps(**missing_arguments):\n"
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

            code = code + (child['depth']) * '    ' \
                + 'for ' + child['iterator'] \
                + ' in '\
                + iterable\
                + ':' + '\n'
            code = code + generate_body(child, module)

        elif child['step'] == 'while':
            is_coroutine = inspect.iscoroutinefunction(
                getattr(module, child['condition']['step']))
            call = generate_call(child['condition']['step'],
                                 child['condition']['arguments'], is_coroutine)
            
            code = code + (child['depth']) * '    ' \
                + 'while ' + call + ':' + '\n'
            code = code + generate_body(child, module)            

        elif child['step'] == 'if':
            pass

        elif child['step'] == 'attribution':
            code = code + (child['depth']) * '    ' + \
                child['target'] + ' = ' + str(child['source']) + '\n'
        else:
            is_coroutine = inspect.iscoroutinefunction(getattr(module,
                                                               child['step']))
            code = code + (child['depth']) * '    ' \
                + generate_call(child['step'], child['arguments'],
                                is_coroutine) + '\n'
    return code


def generate_code(recipe, module):
    """
    Generates the entire code.
    """
    code = generate_head(module)
    code = code + generate_body(recipe, module)
    return code
