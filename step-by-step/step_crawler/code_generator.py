import inspect
import step_crawler.step_generators as step_generators
from pyext import RuntimeModule



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
        if hasattr(step_generators, "generate_" + child["step"]):
            code += getattr(step_generators, "generate_" + child["step"])(child, module)
        else:
            code += step_generators.generate_call_step(child, module)

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
