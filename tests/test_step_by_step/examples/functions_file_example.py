from step_crawler.functions_file import *


@step("Mandatory and optional params")
def mandatory_and_optional_params(some, parameters, to=1, test=None):
    if test is None:
        test = {}
    return some, parameters, to, test


@step("Only mandatory params")
def only_mandatory_params(some, parameters, to, test):
    return some, parameters, to, test


@step("Only optional params")
def only_optional_params(some="some", parameters="parameters", to="to",
                         test="test"):
    return some, parameters, to, test


@step("No params")
def no_params():
    return [1, 2]
