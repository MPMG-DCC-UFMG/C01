"""
This module contains the methods to generate the most common cases of
parameters to be injected
"""

import datetime
import itertools
import string

from math import log10
from typing import Callable, Generator, List, Optional, Tuple, Union


class ParamInjector():
    """
    The ParamInjector contains static methods to generate a sequence of
    parameters to be injected in a page
    """

    @staticmethod
    def process_code_verification(sequential: int, year: int, seg_id: int,
                                  court_id: int, origin_id: int):
        """
        Generates the verification digits for a process code.

        :param sequential: the sequential identifier for the process
        :param year:       the year of the process
        :param seg_id:     the segment id of the process
        :param court_id:   the court id of the process
        :param origin_id:  the origin id of the process

        :returns: the verification digits obtained
        """

        value_str = str(sequential) + str(year) + str(seg_id) + \
            str(court_id) + str(origin_id)
        verif_val = 98 - ((int(value_str) * 100) % 97)

        return verif_val


    @staticmethod
    def __format_unpack_ranges(param_limits: List[Union[Tuple[int, int],
                                                        List[int]]]
                               ) -> List[Union[range, list]]:
        """
        Converts the supplied parameter range limits into a list of iterables

        :param param_limits: a list where each element is either a list of
                             possible values for a placeholder, or a tuple
                             containing the upper and lower limits for it

        :returns: a list of iterables for each parameter
        """

        result = []
        for entry in param_limits:
            if isinstance(entry, tuple):
                if len(entry) != 2 or \
                   not isinstance(entry[0], int) or \
                   not isinstance(entry[1], int):
                    raise ValueError("Tuple entries in param_limits should " +
                                     "contain two integers")

                lower_lim = entry[0]
                upper_lim = entry[1] + 1

                # this shouldn't be too computationally expensive, since ranges
                # are lazily computed
                result.append(range(lower_lim, upper_lim))
            elif isinstance(entry, list):
                result.append(entry)
            else:
                # invalid type for entry in param_limits
                message = "Elements in param_limits should be lists or tuples"
                raise ValueError(message)

        return result


    @staticmethod
    def format_params(code_format: str,
                      entry: Tuple[int, ...],
                      verif: Optional[Callable[[List[int]], int]],
                      verif_index: Optional[int]
                      ) -> str:
        """
        Generates the formatted code as a string for a single combination of
        parameters

        :param code_format:  a Python format string describing the desired code
        :param entry:        a tuple of parameters to be included in the result
        :param verif:        a function which receives the generated parameters
                             and returns an integer, to be used as a
                             verification code calculator for each entry
        :param verif_index:  if the verification function is supplied, this
                             parameter determines where the generated
                             verification code should be inserted in the format
                             string

        :returns: the formatted string with the supplied parameters and the
                  verification code, if applicable
        """

        if verif:
            # calculates the verification code for this entry
            verif_code = verif(*entry)
            # insert it in the code, at the correct position
            first_half = entry[:verif_index]
            second_half = entry[verif_index:]

            entry = first_half + (verif_code, ) + second_half

        return code_format.format(*entry)


    @staticmethod
    def generate_format(code_format: str,
                        param_limits: List[Union[Tuple[int, int], List[int]]],
                        verif: Optional[Callable[[List[int]], int]] = None,
                        verif_index: Optional[int] = None
                        ) -> Generator[str, None, None]:
        """
        Generates a sequence of strings following a given format string and
        allowed ranges

        :param code_format:  a Python format string describing the desired code
        :param param_limits: a list where each element is either a list of
                             possible values for a placeholder, or a tuple
                             containing the upper and lower limits for it
        :param verif:        a function which receives the generated parameters
                             and returns an integer, to be used as a
                             verification code calculator for each entry
        :param verif_index:  if the verification function is supplied, this
                             parameter determines where the generated
                             verification code should be inserted in the format
                             string

        :yields: strings following the format for each possible combination of
                 parameters
        """

        # if verif function is supplied, check if verif_index is too
        if verif and not isinstance(verif_index, int):
            message = "Verification number index must be supplied when using " +\
                      "a verification function"
            raise ValueError(message)

        ranges_list = ParamInjector.__format_unpack_ranges(param_limits)

        # itertools.product generates all combinations of entries from each list
        # in ranges_list
        for entry in itertools.product(*ranges_list):
            yield ParamInjector.format_params(code_format, entry, verif,
                                              verif_index)


    @staticmethod
    def __num_calculate_fill_size(first: int, last: int) -> int:
        """
        Calculates the required number of digits given the first and last
        numbers to generate

        :param first: first number in the sequence
        :param last:  last number in the sequence

        :returns: number of digits required to represent all numbers in the
                  range with the same length
        """

        # we use the abs function to account for negative values
        fill_size = 0
        if first != 0:
            fill_size = int(log10(abs(first)))
        if last != 0:
            fill_size = max(fill_size, int(log10(abs(last))))
        return fill_size + 1


    @staticmethod
    def generate_num_sequence(first: int,
                              last: int,
                              step: int = 1,
                              leading: bool = True
                              ) -> Generator[str, None, None]:
        """
        Generates a sequence of strings in numerical sequence

        :param first:   first number in the sequence
        :param last:    last number in the sequence
        :param step:    how much to "step" between one number and the next
        :param leading: if true, leading zeros will be added to the numbers so
                        that they all have the same number of digits

        :yields: the sequence numbers as strings
        """

        upper_lim = (last + 1) if first <= last else (last - 1)

        fill_size = ParamInjector.__num_calculate_fill_size(first, last)

        for i in range(first, upper_lim, step):
            i_str = str(i)
            if leading:
                i_str = i_str.zfill(fill_size)
            yield i_str


    @staticmethod
    def __alpha_validate_input(length: int,
                               num_words: int
                               ) -> None:
        """
        Takes in a word length and the number of words for an alphabetic
        gerenator and validates them, raising an error if needed

        :param length:    number of alphabetic characters in each word
        :param num_words: number of words to generate
        """

        if length <= 0:
            raise ValueError("Word length should be greater than zero.")
        if num_words <= 0:
            raise ValueError("Word count should be greater than zero.")


    @staticmethod
    def __alpha_split_sequence(sequence: Tuple[str, ...],
                               length: int,
                               num_words: int
                               ) -> str:
        """
        Turns a tuple of characters into a string of words with the required
        length and formatted as search strings

        :param sequence:  tuple with characters to stringify
        :param length:    number of alphabetic characters in each word
        :param num_words: number of words to generate

        :returns: the search term for this tuple
        """

        result = ""
        # split the sequence into words with correct size
        for i in range(num_words):
            if i > 0:
                result += " "
            result += "".join(sequence[i * length: (i + 1) * length])
            result += "*"

        return result


    @staticmethod
    def generate_alpha(length: int,
                       num_words: int,
                       no_upper: bool = True
                       ) -> Generator[str, None, None]:
        """
        Generates a sequence of alphabetic search parameters, each composed of
        the required number of letters and an asterisk in the end

        :param length:    number of alphabetic characters in each word
        :param num_words: number of words to generate
        :param no_upper:  if True, uses only lowercase letters

        :yields: the search terms as strings
        """

        ParamInjector.__alpha_validate_input(length, num_words)

        alphabet = string.ascii_lowercase if no_upper else string.ascii_letters

        # itertools.product generates all combinations of entries from the
        # alphabet with the required size
        sequences = itertools.product(alphabet, repeat=length * num_words)

        for seq in sequences:
            yield ParamInjector.__alpha_split_sequence(seq, length, num_words)


    @staticmethod
    def __daterange_validate_input(date_format: str,
                                   start_date: datetime.date,
                                   end_date: datetime.date
                                   ) -> None:
        """
        Takes in a date format, start date and end date, and validates them,
        raising an error if needed

        :param date_format: the output format for the dates
        :param start_date:  first date to generate
        :param end_date:    last date to generate
        """

        if len(date_format) == 0:
            raise ValueError("A valid date format must be supplied")
        if not start_date or not end_date:
            raise ValueError("The start and end dates must be supplied.")
        if not isinstance(start_date, datetime.date) or \
           not isinstance(end_date, datetime.date):
            raise ValueError("The start and end dates must be of type " +
                             "datetime.date.")


    @staticmethod
    def __daterange_freq_to_filter(frequency: str
                                   ) -> Callable[[datetime.date], int]:
        """
        Validates a given frequency string and returns the function which takes
        in a date and returns the value corresponding to the implied granularity

        :param frequency: frequency of dates to be generated (Y = yearly,
                          M = monthly, D = daily)

        :returns: the function which converts a date to its desired property
                  (day, month or year)
        """

        if frequency not in ['Y', 'M', 'D']:
            raise ValueError("The frequency must be one of the following" +
                             " options: 'Y', 'M' or 'D'.")

        # choose the required periodicity
        if frequency == 'Y':
            return lambda x: x.year
        if frequency == 'M':
            return lambda x: x.month

        return lambda x: x.day


    @staticmethod
    def __daterange_iter_params(start_date: datetime.date,
                                end_date: datetime.date
                                ) -> Tuple[int, int]:
        """
        Calculates the iteration parameters (max number of days in the range and
        the iteration direction) based on the range limits

        :param start_date:  first date to generate
        :param end_date:    last date to generate

        :returns: a tuple containing, respectively, the max number of days and
                  the iteration direction as an integer, where 1 means ascending
                  and -1 means descending
        """

        # add 1 to number of days to include the end of the period
        max_days = int((end_date - start_date).days) + 1
        delta_coef = 1
        if start_date > end_date:
            # do the inverse subtraction in case the start and end dates are
            # reversed
            max_days = int((start_date - end_date).days) + 1
            # go backwards if start_date comes after end_date
            delta_coef = -1

        return max_days, delta_coef


    @staticmethod
    def generate_daterange(date_format: str,
                           start_date: datetime.date,
                           end_date: datetime.date,
                           frequency: str = 'Y'
                           ) -> Generator[str, None, None]:
        """
        Generates a sequence of dates in the given range as strings, in the
        requested periodicity

        :param date_format: the output format for the dates
        :param start_date:  first date to generate
        :param end_date:    last date to generate
        :param frequency:   frequency of dates to be generated (Y = yearly,
                            M = monthly, D = daily)

        :yields: the formatted dates in the given range
        """

        ParamInjector.__daterange_validate_input(date_format, start_date,
                                                 end_date)

        max_days, delta_coef = ParamInjector.__daterange_iter_params(start_date,
                                                                     end_date)

        prev_period = None
        period_val = ParamInjector.__daterange_freq_to_filter(frequency)

        for day in range(max_days):
            curr = start_date + delta_coef * datetime.timedelta(day)
            if period_val(curr) != prev_period:
                prev_period = period_val(curr)
                yield curr.strftime(date_format)


    @staticmethod
    def generate_list(elements: str) -> Generator[str, None, None]:
        """
        Generates a user-specified list of values. Used when there is not a
        large amount of values to generate and they are not uniform enough to
        use one of the other generators

        :param elements: comma-separated list of elements to generate, as a
                         string

        :yields: the values described in the supplied string
        """

        # Remove leading and trailing spaces in the list elements
        values = [i.strip() for i in elements.split(',')]

        for v in values:
            yield v


    @staticmethod
    def generate_constant(value: str) -> Generator[str, None, None]:
        """
        Generates a single value once. Used for specific cases where you just
        want to fill a placeholder.

        :param value: value to be generated

        :yields: the supplied value
        """

        yield value
