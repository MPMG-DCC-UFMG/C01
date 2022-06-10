import inspect
import sys
import os


def extract_info(func, ignore_params=None):
    """ Extracts the function information, that is, name,
    mandatory parameters, optional parameters and their arguments.
    Parameters:
            func -- some function object
            ignore_params -- parameters to ignore on return

    Returns:
            The function name and parameters.
    """
    if ignore_params is None:
        ignore_params = ['pagina']

    name = func.__code__.co_name
    name_display = name.capitalize().replace('_', '') if not func.display else func.display
    executable_contexts = func.executable_contexts

    optional_params = dict()
    mandatory_params = list()
    field_options = func.field_options
    signature = inspect.signature(func)
    for k, v in signature.parameters.items():
        if v.default is not inspect.Parameter.empty:
            optional_params[k] = v.default
        else:
            if k not in ignore_params:
                mandatory_params.append(k)


    func_info = {
        'name': name,
        'name_display': name_display,
        'executable_contexts': executable_contexts,
        'mandatory_params': mandatory_params,
        'optional_params': optional_params,
        'field_options': field_options,
    }
    return func_info


def import_by_path(module_path):
    """
        Imports a module by its path and returns it.
    """
    module_folder_path = os.path.dirname(module_path)
    module_name = os.path.basename(module_path)
    sys.path.append(module_folder_path)
    module = __import__(module_name[:-3])
    return module


def get_module_functions(module):
    """ Extracts the module functions.
    Parameters:
            module -- the module to extract the functions
    Returns:
            Module functions.
    """
    result = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if type(attr).__name__ == "function" and hasattr(attr, "is_step"):
            result.append(attr)
    return result


def get_module_functions_info(module, ignore_params=None):
    """
    Returns a set with information of all the module functions
    """
    return [extract_info(i, ignore_params) for i in get_module_functions(module)]
