import functions_file
import itertools as it
from copy import deepcopy


def track_parallelizable_fors(recipe, list_of_iterables=None, code=0):
    """ Recursive function that tracks the parallelizable "fors" in the
    recipe passed by parameter and returns a list with information
    about their iterations. In addition, this function marks each
    of these "for" to be paralleled with a "code" key. This code key
    is the index where the "for" information is found in the list
    to be returned.

    Parameters:
            recipe -- the dictionary containing the steps to be paralelized
            list_of_iterables -- this parameter is for recursion.
            code -- this parameter is for recursion.

    Return:
            A list with the information of the parallelizable "fors",
            where the indice of this list, is the same valor of the
            code of the correspondent for.

    """
    if list_of_iterables is None:
        list_of_iterables = []
    for child, i in zip(recipe["children"], range(len(recipe["children"]))):
        if child['step'] == "for":
            if len(recipe["children"]) - 1 == i:
                if child['breakable']:
                    list_of_iterables.append({
                        'iterator': child['iterator'],
                        'iterable': child['iterable']
                    })
                    recipe["children"][i]['code'] = code
                    code += 1
                track_parallelizable_fors(child, list_of_iterables, code)

    return list_of_iterables


def get_iterable_objects(list_of_iterables, module=functions_file):
    """ The list_of_iterables is a list where each element is a dict with
    the name of a function that is in module passed by parameter and a 
    key with its arguments. Thus, each element of this list represents a
    function call. What get_iterable_objects does is, execute all this
    calls and return a list with the objects that this calls returned.

    Parameters:
            recipe -- the dictionary contening the steps to be paralelized
            list_of_iterables -- this parameter is for recursion.
            code -- this parameter is for recursion.

    Return:
            A list with the information of the parallelizable "fors",
            where the indice of this list, is the same valor of the
            code of the correspondent for.
    """
    for i in range(len(list_of_iterables)):
        func = getattr(module, list_of_iterables[i]['iterable']['step'])
        list_of_iterables[i]['iterable'] = func(
            **(list_of_iterables[i]['iterable']['arguments']))
    return list_of_iterables


def decrase_depth(recipe):
    """
    This function assists the for_to_attribution function decrasing the
    value maintained by the "depth" key, when all the steps inside the
    for step come out. Read for_to_attribution description to understand
    better.

    Parameters:
            recipe -- a recipe suposed to have a for with the first step
    Return:
            The recipe passed by parameter but with all the steps inside
            the first step with your depth decrased.

    """
    if "depth" in recipe.keys():
        recipe["depth"] -= 1
    else:
        raise TypeError("""The recipe passed by parameter hasn't the "depth" key in some step""")
    for i in range(len(recipe["children"])):
        if "children" in recipe['children'][i].keys():
            decrase_depth(recipe['children'][i])
        else:
            recipe['children'][i]["depth"] -= 1
    return recipe


def for_to_attribution(recipe, target, source):
    """
    Receives a recipe that is suposed to have a for as the first step.
    Get all inside steps of the for and put them in front of this for.
    After that, replace this for with an attribution step where target
    receives source.

    Parameters:
        recipe -- a recipe suposed to have a for with the first step
        target -- the left side of the attribution that will replace the for
        source -- the right side of the attribution that will replace the for
    Return:
        A recipe with the for step replaced by an attribution

    """
    if 'step' not in recipe or 'depth' not in recipe or 'children' not in recipe:
        raise TypeError("This recipe is in the wrong format")

    if recipe['step']!= 'for':
        raise TypeError("This step is not a for")

    new_recipe = []
    attribution_step = {"step": "attribution",
                        "source": source,
                        "target": target,
                        "depth": recipe["depth"]}
    new_recipe.append(attribution_step)
    decrase_depth(recipe)
    new_recipe = new_recipe + recipe["children"]
    return new_recipe


def replace_fors_to_attributions(recipe, combination, list_of_iterables,
                                 steps_to_consider=['root', 'for']):
    """This function goes through all the recipe, replacing all the for
    steps marked by a "code" key, by an attribution that corresponds with
    one loop of this for step. The value that the "code" key holds is the
    index of the "combination" list that maintains the number of the loop
    that corresponds at this attribution.

    Parameters:
        recipe --  The json with the steps, made by the interface user
        combination -- A list where each indice is relative to a for step
        in recipe. And the value that this indice holds is the values that
        will be in the right side of the attribution.

    Return:
        A recipe with the for steps that is marked by the "code" key
        replaced by an attribution step, and with all the other changes
        needed done.

    """
    if recipe['step'] in steps_to_consider:
        for i in range(len(recipe['children'])):
            replace_fors_to_attributions(
                recipe['children'][i], combination, list_of_iterables)
            if 'code' in recipe['children'][i].keys():
                recipe['children'][i:i+1] = for_to_attribution(
                    recipe['children'][i],
                    list_of_iterables[recipe['children']
                                      [i]['code']]['iterator'],
                    combination[recipe['children'][i]['code']])
        return recipe


def extend(recipe):
    """
    Create a recipe for each iterable combination of breakable fors.
    Each of these recipes represents an iteration of the innermost parallelizable for step.
    Parameters:
            recipe -- The recipe to be broke
    Return:
            A list with all the pieces of this broken recipe.
    """
    list_of_iterables = get_iterable_objects(track_parallelizable_fors(recipe))
    combinations = [i for i in it.product(
        *[item['iterable'] for item in list_of_iterables])]
    extended_list = list()

    for i in range(len(combinations)):
        extended_list.append(deepcopy(recipe))

    for i in range(len(extended_list)):
        extended_list[i] = replace_fors_to_attributions(
            extended_list[i], combinations[i], list_of_iterables)

    return extended_list
