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
        :yields:             strings following the format for each possible
                             combination of parameters
        """

        # if verif function is supplied, check if verif_index is too
        if verif and not verif_index:
            message = "Verification number index must be supplied when using "+\
                      "a verification function"
            raise ValueError(message)

        ranges_list = []

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
                ranges_list.append(range(lower_lim, upper_lim))
            elif isinstance(entry, list):
                ranges_list.append(entry)
            else:
                # invalid type for entry in param_limits
                message = "Elements in param_limits should be lists or tuples"
                raise ValueError(message)

        # itertools.product generates all combinations of entries from each list
        # in ranges_list
        for entry in itertools.product(*ranges_list):
            params_list = entry

            # calculate the verification code for this entry, if supplied
            if verif:
                verif_code = verif(*entry)
                # insert it in the code, at the correct position
                first_half = entry[:verif_index]
                second_half = entry[verif_index:]

                params_list = first_half + (verif_code, ) + second_half

            yield code_format.format(*params_list)

    @staticmethod
    def generate_num_sequence(first: int,
                              last: int,
                              step: int = 1,
                              pad: bool = True
                              ) -> Generator[str, None, None]:
        """
        Generates a sequence of strings in numerical sequence

        :param first: first number in the sequence
        :param last:  last number in the sequence
        :param step:  how much to "step" between one number and the next
        :param pad:   if true, the numbers will be padded with zeroes to have
                      the same number of digits
        :yields:      the sequence numbers as strings
        """

        upper_lim = None
        if first <= last:
            upper_lim = last + 1
        else:
            upper_lim = last - 1

        # account for possible negative numbers
        fill_size = 0
        if first != 0:
            fill_size = int(log10(abs(first)))
        if last != 0:
            fill_size = max(fill_size, int(log10(abs(last))))

        fill_size += 1

        for i in range(first, upper_lim, step):
            i_str = str(i)
            if pad:
                i_str = i_str.zfill(fill_size)
            yield i_str

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
        :yields:          the search terms as strings
        """

        if length <= 0:
            raise ValueError("Word length should be greater than zero.")
        if num_words <= 0:
            raise ValueError("Word count should be greater than zero.")

        alphabet = string.ascii_lowercase if no_upper else string.ascii_letters

        # itertools.product generates all combinations of entries from the
        # alphabet with the required size
        sequences = itertools.product(alphabet, repeat=length * num_words)

        for seq in sequences:
            curr = ""
            # split the sequence into words with correct size
            for i in range(num_words):
                if i > 0:
                    curr += " "

                curr += "".join(seq[i * length : (i + 1) * length])
                curr += "*"

            yield curr


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
        :yields:            the formatted dates in the given range
        """

        if len(date_format) == 0:
            raise ValueError("A valid date format must be supplied")
        if not start_date or not end_date:
            raise ValueError("The start and end dates must be supplied.")
        if not isinstance(start_date, datetime.date) or \
           not isinstance(end_date, datetime.date):
            raise ValueError("The start and end dates must be of type "+\
                             "datetime.date.")
        if frequency not in ['Y', 'M', 'D']:
            raise ValueError("The frequency must be one of the following " +\
                             "options: 'Y', 'M' or 'D'.")

        # add 1 to number of days to include the end of the period
        max_days = int((end_date - start_date).days) + 1
        delta_coef = 1
        if start_date > end_date:
            # do the inverse subtraction in case the start and end dates are
            # reversed
            max_days = int((start_date - end_date).days) + 1
            # go backwards if start_date comes after end_date
            delta_coef = -1

        prev_period = None
        get_period_val = None

        # choose the required periodicity
        if frequency == 'Y':
            get_period_val = lambda x: x.year
        elif frequency == 'M':
            get_period_val = lambda x: x.month
        elif frequency == 'D':
            get_period_val = lambda x: x.day

        for day in range(max_days):
            curr = start_date + delta_coef * datetime.timedelta(day)
            if get_period_val(curr) != prev_period:
                prev_period = get_period_val(curr)
                yield curr.strftime(date_format)
