import inspect


def generate_head(module):
    """
    Generates the first part of the code, that is,
    imports and function signature.
    """
    code = "import sys \n" + "sys.path.append(\"code\")\n"
    code = code + "from " + module.__name__ + " import *\n\n"
    code = code + "async def execute_steps(**missing_argument):\n"
    return code


def generate_body(recipe, module):
    """
    Generates the second part of the code, that is,
    the body of the function, the steps.
    """
    code = ""
    for child in recipe['children']:
        if child['step'] == 'for':
            iterable_parameter = "**" + str(child['iterable']['arguments'])
            step_call = child['iterable']['step']
            if inspect.iscoroutinefunction(getattr(module, child['iterable']['step'])):         
                iterable_parameter += ", **missing_argument"
                step_call = "await " + step_call

            code = code + (child['depth']) * '    ' \
                + 'for ' + child['iterator'] \
                + ' in ' + step_call \
                + '(' + iterable_parameter \
                + '):' + '\n'
            code = code + generate_body(child, module)




        elif child['step'] == 'while':
            
            iterable_parameter = "**" + str(child['condition']['arguments'])
            step_call = child['condition']['step']
            if inspect.iscoroutinefunction(getattr(module, child['condition']['step'])):         
                iterable_parameter += ", **missing_argument"
                step_call = "await " + step_call

            code = code + (child['depth']) * '    ' \
                + 'while ' \
                + step_call \
                + '(' + iterable_parameter + '):'\
                + '\n'
            code = code + generate_body(child, module)            

        elif child['step'] == 'if':
            pass

        elif child['step'] == 'attribution':
            code = code + (child['depth']) * '    ' + \
                child['to'] + ' = ' + str(child['from']) + '\n'

        elif inspect.iscoroutinefunction(getattr(module, child['step'])):
            code = code + (child['depth']) * '    ' \
                + 'await ' + \
                child['step'] + '(**' + str(child['arguments']) + \
                ', **missing_argument)' + '\n'
        else:
            code = code + (child['depth']) * '    ' \
                + child['step'] \
                + '(**' + str(child['arguments']) \
                + ')\n'
    return code


def generate_code(recipe, module):
    """
        Generates the entire code.
    """
    code = generate_head(module)
    code = code + generate_body(recipe, module)
    return code
