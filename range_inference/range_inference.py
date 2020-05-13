"""
This module filters the search space for a specified parameter
"""

import datetime

from typing import Any, Callable, Generator, Tuple, Union
from dateutil.relativedelta import relativedelta

class RangeInference():
    """
    The RangeInference class contains the static methods to filter the search
    space. The __filter_range method is the core of the binary search. The
    filter_numeric_range and filter_date_range methods do computation on the
    inputs to call __filter_range accordingly.
    """

    @staticmethod
    def __filter_range(limits: Tuple[Union[int, datetime.date],
                                     Union[int, datetime.date]],
                       hit_check: Callable[[Any], bool],
                       step_size: Union[int, relativedelta],
                       mid_calc: Callable[[Any, Any], int],
                       range_gen: Generator
                       ) -> Union[int, datetime.date]:
        """
        Does a binary search in the given range to discover which part of it
        actually contains results, but checks cons_misses entries at a time
        before doing the division step. This method works for both dates and
        integers, and contains the barebones algorithm only.

        :param limits:    tuple with lower and upper limits for the range to be
                          checked
        :param hit_check: function which does the request and returns True if it
                          hits an entry or False if it doesn't
        :param step_size: value to be added to a given index to go to the next
                          one
        :param mid_calc:  function which takes the beginning and end of the
                          current range being considered and calculates the
                          midpoint
        :param range_gen: generator which takes the current mid point and the
                          beginning and end of the current range being
                          considered and yields all the points near the middle
                          that we need to check

        :returns:     position where the last hit entry was found, None if no
                      entries were found
        """
        begin, end = limits

        last_hit = None
        delta = step_size

        curr_begin = begin
        curr_end = end

        while curr_begin < curr_end:
            mid = mid_calc(curr_begin, curr_end)
            # check the required number of entries before declaring a miss
            all_miss = True
            for i in range_gen(mid, curr_begin, curr_end):
                if hit_check(i):
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
                             hit_check: Callable[[str], bool],
                             cons_misses: int = 100
                            ) -> int:
        """
        Does the binary search over a numeric range.

        :param begin:       lower limit for the range to be checked
        :param end:         upper limit for the range to be checked
        :param hit_check:   function which does the request and returns True if
                            it hits an entry or False if it doesn't
        :param cons_misses: number of consecutive misses needed to discard all
                            following entries

        :returns: position where the last hit entry was found, None if no
                  entries were found
        """
        # Parameter validation
        if not isinstance(begin, int) or not isinstance(end, int):
            raise ValueError("The range limits should be supplied for the "+\
                             "inference.")
        if begin > end:
            raise ValueError("The beginning of the range should be lower than"+\
                             " the end.")
        if hit_check is None:
            raise ValueError("A valid entry probing function must be supplied.")
        if not isinstance(cons_misses, int) or cons_misses < 0:
            raise ValueError("The number of consecutive misses must be a "+\
                             "positive integer.")

        def calc_mid(curr_begin, curr_end):
            return (curr_begin + curr_end) // 2

        def range_gen(mid, _, curr_end):
            return range(mid, min(mid + cons_misses, curr_end + 1, end + 1))


        return RangeInference.__filter_range((begin, end), hit_check, 1,
                                             calc_mid, range_gen)


    @staticmethod
    def filter_date_range(begin: datetime.date,
                          end: datetime.date,
                          hit_check: Callable[[datetime.date], bool],
                          detail_level: str = 'Y',
                          cons_misses: int = 100,
                          ) -> datetime.date:
        """
        Does the binary search over a date range.

        :param begin:        lower limit for the range to be checked
        :param end:          upper limit for the range to be checked
        :param hit_check:    function which does the request and returns True if
                             it hits an entry or False if it doesn't
        :param detail_level: granularity of date check (Y = yearly, M = monthly,
                             D = daily)
        :param cons_misses:  number of consecutive misses needed to discard all
                             following entries

        :returns: position where the last hit entry was found, None if no
                  entries were found
        """
        # Parameter validation
        if not isinstance(begin, datetime.date) or \
           not isinstance(end, datetime.date):
            raise ValueError("The range limits should be supplied for the "+\
                             "inference.")
        if begin > end:
            raise ValueError("The beginning of the range should be lower than"+\
                             " the end.")
        if hit_check is None:
            raise ValueError("A valid entry probing function must be supplied.")
        if not isinstance(cons_misses, int) or cons_misses < 0:
            raise ValueError("The number of consecutive misses must be a "+\
                             "positive integer.")

        # Calculates the step size based on the required granularity
        time_delta = None
        if detail_level == 'Y':
            time_delta = relativedelta(years=1)
        elif detail_level == 'M':
            time_delta = relativedelta(months=1)
        elif detail_level == 'D':
            time_delta = relativedelta(days=1)
        else:
            raise ValueError("The detail level must be one of the following " +\
                             "options: 'Y', 'M' or 'D'.")

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

        return RangeInference.__filter_range((begin, end), hit_check,
                                             time_delta, calc_mid, range_gen)
