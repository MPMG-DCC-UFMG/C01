# Tools to convert injection data into the actual injectors

from entry_probing import BinaryFormatProbingResponse, HTTPProbingRequest,\
    HTTPStatusProbingResponse, TextMatchProbingResponse,\
    EntryProbing
from param_injector import ParamInjector
from range_inference import RangeInference

import datetime
import itertools


def create_probing_object(base_url, req_type, resp_handlers=[]):
    """
    Loads the request data and response handlers supplied, and generates
    the respective EntryProbing instance
    """

    # Probing request
    probe = EntryProbing(HTTPProbingRequest(base_url, method=req_type))

    # Probing response
    for handler_data in resp_handlers:
        resp_handler = None

        handler_type = handler_data['handler_type']
        if handler_type == 'text':
            resp_handler = TextMatchProbingResponse(
                text_match=handler_data['text_match_value'],
                opposite=handler_data['opposite']
            )
        elif handler_type == 'http_status':
            resp_handler = HTTPStatusProbingResponse(
                status_code=handler_data['http_status'],
                opposite=handler_data['opposite']
            )
        elif handler_type == 'binary':
            resp_handler = BinaryFormatProbingResponse(
                opposite=handler_data['opposite']
            )
        else:
            raise AssertionError

        probe.add_response_handler(resp_handler)

    return probe


def create_parameter_generators(probe, parameter_handlers, filter_limits=True):
    """
    Loads the parameter information and creates a list of the respective
    generators from the ParamInjector module, while filtering the ranges as
    necessary
    """

    url_injectors = []
    initial_values = []

    for i in [1, 2]:
        # We run this code twice: the first pass will get the initial
        # values for each parameter, which is used in the second pass to
        # filter the ends of the limits as required
        # I couldn't find a nicer way to do this

        if not filter_limits and i == 2:
            # Don't filter limits unless required
            break

        for param_index, param in enumerate(parameter_handlers):
            param_type = param['parameter_type']
            param_gen = None

            if i == 2 and not param['filter_range']:
                # We are running the "filtering" pass but this parameter
                # should not be filtered
                continue

            entries_list = []
            cons_misses = None
            if i == 2:
                # Configure the list of extra parameters for the range
                # inference
                entries_list = initial_values.copy()
                entries_list[param_index] = None
                cons_misses = int(param['cons_misses'])

            if param_type == "process_code":
                PROCESS_FORMAT = '{:07d}-{:02d}.{:04d}.{}.{:02d}.{:04d}'

                first_year = int(param['first_year_proc_param'])
                last_year = int(param['last_year_proc_param'])
                segment_ids = param['segment_ids_proc_param'].split(",")
                court_ids = param['court_ids_proc_param'].split(",")
                origin_ids = param['origin_ids_proc_param'].split(",")

                # turn string lists into integers
                segment_ids = list(map(int, segment_ids))
                court_ids = list(map(int, court_ids))
                origin_ids = list(map(int, origin_ids))

                max_seq = 9999999
                if i == 2:
                    # Filter the process_code range
                    max_seq = RangeInference.filter_process_code(
                        first_year, last_year, segment_ids, court_ids,
                        origin_ids, probe, entries_list,
                        cons_misses=cons_misses
                    )

                subparam_list = [
                    # sequential identifier
                    (0, max_seq),
                    # year
                    (first_year, last_year),
                    # segment identifiers
                    segment_ids,
                    # court identifiers
                    court_ids,
                    # origin identifiers
                    origin_ids
                ]

                param_gen = ParamInjector.generate_format(
                    code_format=PROCESS_FORMAT,
                    param_limits=subparam_list,
                    verif=ParamInjector.process_code_verification,
                    verif_index=1
                )

            elif param_type == "number_seq":
                begin = int(param['first_num_param'])
                end = int(param['last_num_param'])

                if i == 2:
                    # Filter the number range
                    end = RangeInference.filter_numeric_range(begin, end,
                              probe, entries_list, cons_misses=cons_misses)

                param_gen = ParamInjector.generate_num_sequence(
                    first=begin,
                    last=end,
                    step=int(param['step_num_param']),
                    leading=param['leading_num_param'],
                )
            elif param_type == 'date_seq':
                begin = datetime.date.fromisoformat(
                    param['start_date_date_param']
                )
                end = datetime.date.fromisoformat(
                    param['end_date_date_param']
                )
                frequency = param['frequency_date_param']
                date_format = param['date_format_date_param']

                if i == 2:
                    # Filter the date range
                    end = RangeInference.filter_daterange(begin, end,
                              probe, frequency, date_format, entries_list,
                              cons_misses=cons_misses)

                param_gen = ParamInjector.generate_daterange(
                    date_format=date_format,
                    start_date=begin,
                    end_date=end,
                    frequency=frequency,
                )
            elif param_type == 'alpha_seq':
                # We don't do anything diferent here if it's the second
                # pass, since alphabetic sequences can't be filtered

                length = int(param['length_alpha_param'])
                num_words = int(param['num_words_alpha_param'])
                no_upper = param['no_upper_alpha_param']

                param_gen = ParamInjector.generate_alpha(length=length,
                   num_words=num_words,
                   no_upper=no_upper
                )
            elif param_type == 'value_list':
                # No filtering applied to this parameter
                list_values = param['value_list_param']

                param_gen = ParamInjector.generate_list(
                    elements=list_values
                )
            elif param_type == 'const_value':
                # No filtering applied to this parameter
                const_value = param['value_const_param']

                param_gen = ParamInjector.generate_constant(
                    value=const_value
                )
            else:
                raise ValueError(f"Invalid parameter type: {param_type}")

            if i == 2 and param_gen is not None:
                # We have filtered the range for this parameter, and should
                # update the generator in the list
                url_injectors[param_index] = param_gen
            else:
                # Create a copy of the generator, to extract the first
                # value. After that, add to the list of parameter
                # generators
                param_gen, param_gen_first = itertools.tee(param_gen)
                initial_values.append(next(param_gen_first))
                url_injectors.append(param_gen)

    return url_injectors
