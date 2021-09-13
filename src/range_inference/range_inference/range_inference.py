"""
This module filters the search space for a specified parameter
"""

import datetime
import functools
import itertools

from typing import Any, Callable, Generator, List, Optional, Tuple, Union
from dateutil.relativedelta import relativedelta
from entry_probing import EntryProbing
from param_injector import ParamInjector


class RangeInference():
    """
    The RangeInference class contains the static methods to filter the search
    space. The __filter_range method is the core of the binary search. The
    filter_numeric_range and filter_daterange methods do computation on the
    inputs to call __filter_range accordingly.
    """


    @staticmethod
    def __range_validate_input(limits: Tuple[Union[int, datetime.date],
                                             Union[int, datetime.date]],
                               entry_probe: EntryProbing,
                               step_size: Union[int, relativedelta],
                               mid_calc: Callable[[Any, Any], int],
                               range_gen: Generator,
                               extra_params: Optional[List[Any]] = None,
                               preprocess: Callable[[Any, Any], Any] = None,
                               ) -> None:
        """
        Takes in the parameters for __filter_range and validates them, raising
        an error if needed

        :param limits:       tuple with lower and upper limits for the range to
                             be checked
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param step_size:    value to be added to a given index to go to the
                             next one
        :param mid_calc:     function which takes the beginning and end of the
                             current range being considered and calculates the
                             midpoint
        :param range_gen:    generator which takes the current mid point and
                             the beginning and end of the current range being
                             considered and yields all the points near the
                             middle that we need to check
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one "None" entry, which represents
                             the position for the filtered parameter)
        :param preprocess:   function to be applied to each generated entry to
                             search
        """
        begin, end = limits

        if begin is None or end is None:
            raise ValueError("The range limits should be supplied for the " +
                             "inference.")
        if begin > end:
            raise ValueError("The beginning of the range should be lower" +
                             " than the end.")
        if not isinstance(entry_probe, EntryProbing):
            raise ValueError("A valid EntryProbing instance must be supplied" +
                             " entry_probe.")
        if step_size is None:
            raise ValueError("A range step size must be supplied.")
        if mid_calc is None:
            raise ValueError("A valid middle-calculating function must be " +
                             "supplied.")
        if range_gen is None:
            raise ValueError("A valid range generator must be supplied.")

        if extra_params is not None and (not isinstance(extra_params, list) or
           extra_params.count(None) != 1):
            raise ValueError("extra_params must either be None or a list with" +
                             " exactly one of the entries being None")

        if preprocess is not None and not callable(preprocess):
            raise ValueError("A valid preprocessing function must be " +
                             "supplied.")


    @staticmethod
    def __filter_range(limits: Tuple[Union[int, datetime.date],
                                     Union[int, datetime.date]],
                       entry_probe: EntryProbing,
                       step_size: Union[int, relativedelta],
                       mid_calc: Callable[[Any, Any], int],
                       range_gen: Generator,
                       extra_params: Optional[List[Any]] = None,
                       preprocess: Callable[[Any, Any], Any] = lambda x: x
                       ) -> Union[int, datetime.date]:
        """
        Does a binary search in the given range to discover which part of it
        actually contains results, but checks cons_misses entries at a time
        before doing the division step. This method works for both dates and
        integers, and contains the barebones algorithm only.

        :param limits:       tuple with lower and upper limits for the range to
                             be checked
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param step_size:    value to be added to a given index to go to the
                             next one
        :param mid_calc:     function which takes the beginning and end of the
                             current range being considered and calculates the
                             midpoint
        :param range_gen:    generator which takes the current mid point and
                             the beginning and end of the current range being
                             considered and yields all the points near the
                             middle that we need to check
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one "None" entry, which represents
                             the position for the filtered parameter)
        :param preprocess:   function to be applied to each generated entry to
                             search (identity function by default)

        :returns: position where the last hit entry was found, None if no
                  entries were found
        """
        # Validate inputs
        RangeInference.__range_validate_input(limits, entry_probe, step_size,
                                              mid_calc, range_gen,
                                              extra_params, preprocess)

        begin, end = limits

        last_hit = None
        delta = step_size

        curr_begin = begin
        curr_end = end

        # If extra_params is None, we insert this parameter as the only element
        # in a list (we signal this by setting the only entry to None)
        if extra_params is None:
            extra_params = [None]

        param_index = extra_params.index(None)

        params_instance = extra_params.copy()
        while curr_begin <= curr_end:
            mid = mid_calc(curr_begin, curr_end)
            # check the required number of entries before declaring a miss
            all_miss = True
            for i in range_gen(mid, curr_begin, curr_end):
                params_instance[param_index] = preprocess(i)

                if entry_probe.check_entry(params_instance):
                    all_miss = False
                    last_hit = i

            if all_miss:
                curr_end = mid - delta
            else:
                curr_begin = last_hit + delta

        return last_hit


    @staticmethod
    def filter_numeric_range(begin: int,
                             end: int,
                             entry_probe: EntryProbing,
                             extra_params: Optional[List[Any]] = None,
                             cons_misses: int = 100
                             ) -> int:
        """
        Does the binary search over a numeric range.

        :param begin:        lower limit for the range to be checked
        :param end:          upper limit for the range to be checked
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one "None" entry, which represents
                             the position for the filtered parameter)
        :param cons_misses:  number of consecutive misses needed to discard all
                             following entries

        :returns: position where the last hit entry was found, None if no
                  entries were found
        """
        # Parameter validation
        if not isinstance(cons_misses, int) or cons_misses < 0:
            raise ValueError("The number of consecutive misses must be a " +
                             "positive integer.")

        def calc_mid(curr_begin, curr_end):
            return (curr_begin + curr_end) // 2

        def range_gen(mid, _, curr_end):
            return range(mid, min(mid + cons_misses, curr_end + 1, end + 1))


        return RangeInference.__filter_range((begin, end), entry_probe, 1,
                calc_mid, range_gen, extra_params)


    @staticmethod
    def __daterange_calc_stepsize(detail_level: str = 'Y') -> relativedelta:
        """
        Calculates the step size for the date based on the required granularity

        :param detail_level: granularity of date check (Y = yearly,
                             M = monthly, D = daily)

        :returns: a relativedelta describing the distance between two
                  consecutive dates in the supplied frequency
        """

        if detail_level == 'Y':
            return relativedelta(years=1)
        if detail_level == 'M':
            return relativedelta(months=1)
        if detail_level == 'D':
            return relativedelta(days=1)

        raise ValueError("The detail level must be one of the following " +
                         "options: 'Y', 'M' or 'D'.")

    @staticmethod
    def filter_daterange(begin: datetime.date,
                         end: datetime.date,
                         entry_probe: EntryProbing,
                         detail_level: str = 'Y',
                         date_format: Optional[str] = None,
                         extra_params: Optional[List[Any]] = None,
                         cons_misses: int = 100
                         ) -> Union[str, datetime.date]:
        """
        Does the binary search over a date range.

        :param begin:        lower limit for the range to be checked
        :param end:          upper limit for the range to be checked
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param detail_level: granularity of date check (Y = yearly,
                             M = monthly, D = daily)
        :param date_format:  format to be applied to the generated dates, will
                             return datetime.date values if set to None
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one None entry, which represents the
                             position for the filtered parameter)
        :param cons_misses:  number of consecutive misses needed to discard all
                             following entries

        :returns: position where the last hit entry was found, None if no
                  entries were found
        """

        # Parameter validation
        if not isinstance(cons_misses, int) or cons_misses < 0:
            raise ValueError("The number of consecutive misses must be a " +
                             "positive integer.")

        if date_format is not None and not isinstance(date_format, str):
            raise TypeError("The date format parameter must be a string or " +
                            "None.")

        time_delta = RangeInference.__daterange_calc_stepsize(detail_level)

        # Calculates the date in the middle of the given range, following the
        # defined detail level
        def calc_mid(curr_begin, curr_end):
            mid = relativedelta(curr_end, curr_begin)
            if detail_level == 'Y':
                mid = relativedelta(years=mid.years // 2)
                mid += curr_begin
            elif detail_level == 'M':
                mid = relativedelta(months=mid.months // 2)
                mid += curr_begin
            elif detail_level == 'D':
                mid = relativedelta(days=mid.days // 2)
                mid += curr_begin
            return mid

        # Generates the range of dates to be checked
        def range_gen(mid, _, curr_end):
            i = mid
            while i <= mid + cons_misses * time_delta and \
                    i <= curr_end and \
                    i <= end:
                yield i
                i += time_delta

        def preprocess(entry):
            if date_format is not None:
                return entry.strftime(date_format)
            return entry

        return RangeInference.__filter_range((begin, end), entry_probe,
                time_delta, calc_mid, range_gen, extra_params, preprocess)

    @staticmethod
    def filter_formatted_code(code_format: str,
                              param_limits: List[Union[Tuple[int, int],
                                                       List[int]]],
                              filter_which: List[bool],
                              entry_probe: EntryProbing,
                              verif: Optional[Callable[
                                              [List[int]], int]] = None,
                              verif_index: Optional[int] = None,
                              extra_params: Optional[List[Any]] = None,
                              cons_misses: int = 100
                              ) -> List[Union[Tuple[int, int],
                                              List[int]]]:
        """
        Does the binary search over the specified sub-fields of a formatted
        code.

        :param code_format:  a Python format string describing the desired code
        :param param_limits: a list where each element is either a list of
                             possible values for a placeholder, or a tuple
                             containing the upper and lower limits for it
        :param filter_which: array of boolean values, where a True entry means
                             the parameter in the corresponding position should
                             be filtered
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param verif:        a function which receives the generated parameters
                             and returns an integer, to be used as a
                             verification code calculator for each entry
        :param verif_index:  if the verification function is supplied, this
                             parameter determines where the generated
                             verification code should be inserted in the format
                             string
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one None entry, which represents the
                             position for the filtered parameter)
        :param cons_misses:  number of consecutive misses needed to discard all
                             following entries

        :returns: a copy of param_limits, but with updated end values for
                  filtered ranges
        """

        # Parameter validation
        if not isinstance(cons_misses, int) or cons_misses < 0:
            raise ValueError("The number of consecutive misses must be a " +
                             "positive integer.")

        if not isinstance(code_format, str):
            raise TypeError("The code format parameter must be a string.")

        initial_values = list(map(lambda x: x[0], param_limits))

        def calc_mid(curr_begin, curr_end):
            return (curr_begin + curr_end) // 2

        new_param_limits = param_limits.copy()

        for index, subparam in enumerate(new_param_limits):
            if filter_which[index] and isinstance(subparam, tuple):
                # filter range parameters specified by the user
                begin = subparam[0]
                end = subparam[1]

                def range_gen(mid, _, curr_end):
                    return range(mid, min(mid + cons_misses, curr_end + 1,
                                          end + 1))

                def preprocess(entry):
                    entries_list = initial_values.copy()
                    entries_list[index] = entry
                    return ParamInjector.format_params(code_format,
                            tuple(entries_list), verif, verif_index)

                new_end = RangeInference.__filter_range((begin, end),
                            entry_probe, 1, calc_mid, range_gen, extra_params,
                            preprocess)
                new_param_limits[index] = (begin, new_end)

        return new_param_limits


    @staticmethod
    def filter_process_code(first_year: int,
                            last_year: int,
                            segment_ids: List[int],
                            court_ids: List[int],
                            origin_ids: List[int],
                            entry_probe: EntryProbing,
                            extra_params: Optional[List[Any]] = None,
                            cons_misses: int = 100
                            ) -> int:
        """
        Does the binary search over the sequential number section of a process
        code, returning the maximum value found among all possible combinations
        for other parameters

        :param first_year:   the first year to be checked
        :param last_year:    the last year to be checked
        :param segment_ids:  a list of segment ids to check
        :param court_ids:    a list of court ids to check
        :param origin_ids:   a list of origin ids to check
        :param entry_probe:  instance of EntryProbing describing the request
                             method and response validation
        :param extra_params: list of extra parameters to be sent during probing
                             (must include one None entry, which represents the
                             position for the filtered parameter)
        :param cons_misses:  number of consecutive misses needed to discard all
                             following entries

        :returns: the highest sequential digit found for all possible
                  combination of other parameters
        """

        # Parameter validation
        if not isinstance(first_year, int):
            raise TypeError("The first year of the process code must be an"
                            " integer.")
        if not isinstance(last_year, int):
            raise TypeError("The last year of the process code must be an"
                            " integer.")
        if not isinstance(segment_ids, list) and \
           not all([isinstance(seg, int) for seg in segment_ids]):
            raise TypeError("The segment ids must be a list of integers.")
        if not isinstance(court_ids, list) and \
           not all([isinstance(seg, int) for seg in court_ids]):
            raise TypeError("The court ids must be a list of integers.")
        if not isinstance(origin_ids, list) and \
           not all([isinstance(seg, int) for seg in origin_ids]):
            raise TypeError("The origin ids must be a list of integers.")


        PROCESS_FORMAT = '{}-{}.{:04d}.{}.{:02d}.{:04d}'
        SEQ_LIMIT = 9999999
        verif_index = 1
        year_range = range(first_year, last_year + 1)
        max_seq = 0
        # Generate all possible combinations for other parameters
        for combination in itertools.product(year_range, segment_ids,
                                             court_ids, origin_ids):
            year, segment, court, origin = combination
            updated_format = PROCESS_FORMAT.format('{:07d}', '{:02d}', year,
                               segment, court, origin)

            def verif(seq):
                return ParamInjector.process_code_verification(seq, year,
                         segment, court, origin)

            curr_seq = RangeInference.filter_formatted_code(updated_format,
                         [(0, SEQ_LIMIT)], [True], entry_probe, verif,
                verif_index, extra_params, cons_misses)[0][1]
            if curr_seq is not None and curr_seq > max_seq:
                max_seq = curr_seq

        return max_seq
