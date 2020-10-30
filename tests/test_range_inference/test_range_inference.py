"""
This module tests the range inference module
"""
import unittest
from unittest import mock

from datetime import date, datetime
from typing import Any, Callable, Optional, Union

from entry_probing import EntryProbing
from range_inference import RangeInference


class RangeInferenceTest(unittest.TestCase):
    """
    Testing routines for the range inference. We use the mock module to create
    mocks of the EntryProbing class, used for validating an entry.
    """

    @staticmethod
    def dummy_entry_probe(begin: Union[int, date],
                          end: Union[int, date],
                          date_format: Optional[str] = None
                          ) -> EntryProbing:
        """
        Helper function which returns a mock of an entry probe. The begin and
        end parameters determine the interval where it considers an entry as
        valid.

        :param begin:       first value to be considered a "hit" for an entry
        :param end:         last value to be considered a "hit" for an entry
        :param date_format: date format if a date interval is being used

        :returns: a mock of EntryProbe for which calls to check_entry return
                  True when the given parameter is within the [begin, end]
                  interval, and False otherwise
        """

        # Make sure we don't use the date_format if we're not dealing with
        # dates
        if not isinstance(begin, date) or not isinstance(end, date):
            date_format = None

        def check(x):
            if isinstance(x[0], str) and date_format is not None:
                date_entry = datetime.strptime(x[0], date_format).date()
                return begin <= date_entry <= end
            else:
                return begin <= x[0] <= end

        probe = mock.Mock(spec=EntryProbing, check_entry=check)

        return probe


    @staticmethod
    def dummy_code_probe(separator, end_list):
        """
        Creates a dummy probe in the case of formatted codes

        :param separator: separator used in code
        :param end_list:  list of last values to be accepted for each
                          sub-parameter

        :returns: a mock of EntryProbe for which calls to check_entry
                  return True when all the sub-parameters are less than its
                  corresponding entry in end_list, and False otherwise
        """

        def check(x):
            values = x[0].split(separator)
            for i, v in enumerate(values):
                if int(v) > end_list[i]:
                    return False
            return True

        probe = mock.Mock(spec=EntryProbing, check_entry=check)
        return probe


    # TESTS

    # NUMERIC RANGE

    def test_numeric_range_inference(self):
        """
        Tests simple numeric ranges
        """

        # Last entry at position number 50
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 50)
        last_entry = RangeInference.filter_numeric_range(0, 200, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 50)

        # Interval beginning at 25 and ending at 48
        entry_probe = RangeInferenceTest.dummy_entry_probe(25, 48)
        last_entry = RangeInference.filter_numeric_range(0, 200, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 48)

        # Simple case similar to the first, but with extra parameters
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 50)
        last_entry = RangeInference.filter_numeric_range(0, 200, entry_probe,
                                                         [None, 2, 'test'],
                                                         cons_misses=10)
        self.assertEqual(last_entry, 50)

        # Case where our module is unable to work: there is a gap in the
        # sequence, and it is larger than the cons_misses parameter
        # Create two interval checks
        def check_25_48(x): return 25 <= x[0] <= 48
        def check_90_95(x): return 90 <= x[0] <= 95
        # Test against both intervals and returns True if it belongs to any of
        # them
        def check_all(x): return (check_25_48(x) or check_90_95(x))
        # Create a specific mock of EntryProbing for this
        entry_probe = mock.Mock(spec=EntryProbing, check_entry=check_all)
        last_entry = RangeInference.filter_numeric_range(0, 200, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 48)

        # Same case as above, but with a higher value for cons_misses, in which
        # case the module finds the correct answer
        last_entry = RangeInference.filter_numeric_range(0, 200, entry_probe,
                                                         cons_misses=50)
        self.assertEqual(last_entry, 95)


    def test_numeric_corner_cases(self):
        """
        Tests the behavior of the numerical range inference in some corner
        cases
        """

        # Empty range (no entries in the original search space)
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, -1)
        # Yearly
        last_entry = RangeInference.filter_numeric_range(0, 100, entry_probe,
                                                         cons_misses=10)
        self.assertIsNone(last_entry)

        # Entire search space is filled
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 123)
        last_entry = RangeInference.filter_numeric_range(0, 123, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 123)

        # Only one entry at the beginning
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 0)
        last_entry = RangeInference.filter_numeric_range(0, 123, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 0)

        # Only one entry near the beginning
        entry_probe = RangeInferenceTest.dummy_entry_probe(5, 5)
        last_entry = RangeInference.filter_numeric_range(0, 123, entry_probe,
                                                         cons_misses=10)
        self.assertEqual(last_entry, 5)


    def test_numeric_error_range_limits(self):
        """
        Tests the errors raised for invalid range limits
        """

        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 50)

        # End of interval is lower than the beginning
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 10,
                          0, entry_probe)
        # Beginning is None
        self.assertRaises(ValueError, RangeInference.filter_numeric_range,
                          None, 10, entry_probe)
        # End is None
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          None, entry_probe)


    def test_numeric_error_entry_probe(self):
        """
        Tests the errors when entry_probe is not supplied
        """

        # Supply None as entry_probe
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, None)


    def test_numeric_error_extra_params(self):
        """
        Tests the errors when the extra_params value is supplied incorrectly
        """

        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 50)

        # Supply list with no None entries
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, entry_probe, [1, 2, 3])

        # Supply list with more than one None entry
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, entry_probe, [None, 2, None])

        # Supply empty list
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, entry_probe, [])


    def test_numeric_error_cons_misses(self):
        """
        Tests the errors when the number of consecutive misses is invalid
        """
        entry_probe = RangeInferenceTest.dummy_entry_probe(0, 50)

        # Supply None as the cons_misses parameter
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, entry_probe, None, None)

        # Supply a negative value as cons_misses
        self.assertRaises(ValueError, RangeInference.filter_numeric_range, 0,
                          10, entry_probe, None, -1)


    # DATE RANGE

    def test_daterange_inference(self):
        """
        Tests simple date ranges
        """

        # Last entry at day 01/01/2012
        int_begin = date(2010, 1, 1)
        int_end = date(2012, 1, 1)
        end = date(2020, 1, 1)
        entry_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end)
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'Y',
                                                     cons_misses=10)
        # Since we're using yearly resolution, only the year value matters
        self.assertEqual(last_entry.year, int_end.year)

        # Same as above but with monthly resolution
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'M',
                                                     cons_misses=10)
        # Using monthly resolution, check year and month
        self.assertEqual(last_entry.year, int_end.year)
        self.assertEqual(last_entry.month, int_end.month)

        # Same as above but with daily resolution
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'D',
                                                     cons_misses=10)
        # Since now the resolution is daily, we can just compare the results
        self.assertEqual(last_entry, int_end)

        # Repeating the tests above, but now with int_end at 31/12/2011, to
        # catch off-by-one errors
        int_end = date(2011, 12, 31)
        entry_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end)
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'Y',
                                                     cons_misses=10)
        self.assertEqual(last_entry.year, int_end.year)
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'M',
                                                     cons_misses=10)
        self.assertEqual(last_entry.year, int_end.year)
        self.assertEqual(last_entry.month, int_end.month)
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     entry_probe, 'D',
                                                     cons_misses=10)
        self.assertEqual(last_entry, int_end)

        # Test usage of date format strings
        datestr_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end, "%Y")
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     datestr_probe, 'Y',
                                                     "%Y",
                                                     cons_misses=10)
        self.assertEqual(last_entry.year, int_end.year)
        datestr_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end, "%m-%Y")
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     datestr_probe, 'M',
                                                     "%m-%Y",
                                                     cons_misses=10)
        self.assertEqual(last_entry.year, int_end.year)
        self.assertEqual(last_entry.month, int_end.month)
        datestr_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end, "%d-%m-%Y")
        last_entry = RangeInference.filter_daterange(int_begin, end,
                                                     datestr_probe, 'D',
                                                     "%d-%m-%Y",
                                                     cons_misses=10)
        self.assertEqual(last_entry, int_end)



    def test_date_error_invalid_detail(self):
        """
        Tests the error case when the supplied detail level is invalid
        """

        # detail_level = None
        int_begin = date(1996, 1, 1)
        int_end = date(1996, 1, 10)
        end = date(1998, 1, 1)
        entry_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end)
        self.assertRaises(ValueError, RangeInference.filter_daterange,
                          int_begin, end, entry_probe, None)

        # detail_level = "YEAR"
        self.assertRaises(ValueError, RangeInference.filter_daterange,
                          int_begin, end, entry_probe, "YEAR")

        # detail_level = ""
        self.assertRaises(ValueError, RangeInference.filter_daterange,
                          int_begin, end, entry_probe, "")


    def test_date_corner_cases(self):
        """
        Tests the behavior of the date range inference in some corner cases
        """

        # Empty range (no entries in the original search space)
        int_begin = date(2010, 1, 1)
        int_end = date(2009, 1, 1)
        begin = date(2000, 1, 1)
        end = date(2020, 1, 1)
        entry_probe = RangeInferenceTest.dummy_entry_probe(int_begin, int_end)
        # Yearly
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'Y', cons_misses=10)
        self.assertIsNone(last_entry)
        # Monthly
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'M', cons_misses=10)
        self.assertIsNone(last_entry)
        # Daily
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'D', cons_misses=10)
        self.assertIsNone(last_entry)

        # Entire search space is filled
        entry_probe = RangeInferenceTest.dummy_entry_probe(begin, end)
        # Yearly
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'Y', cons_misses=10)
        self.assertEqual(last_entry.year, end.year)
        # Monthly
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'M', cons_misses=10)
        self.assertEqual(last_entry.year, end.year)
        self.assertEqual(last_entry.month, end.month)
        # Daily
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'D', cons_misses=10)
        self.assertEqual(last_entry, end)

        # Only one entry at the beginning
        entry_probe = RangeInferenceTest.dummy_entry_probe(begin, begin)
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'D', cons_misses=10)
        self.assertEqual(last_entry, begin)

        # Only one entry near the beginning
        entry_date = date(2000, 1, 5)
        entry_probe = RangeInferenceTest.dummy_entry_probe(entry_date,
                                                           entry_date)
        last_entry = RangeInference.filter_daterange(begin, end, entry_probe,
                                                     'D', cons_misses=10)
        self.assertEqual(last_entry, entry_date)


    def test_date_error_range_limits(self):
        """
        Tests the errors raised for invalid range limits
        """

        # End of interval is lower than the beginning
        begin = date(2020, 1, 1)
        end = date(2000, 1, 1)
        entry_probe = RangeInferenceTest.dummy_entry_probe(begin, end)

        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          end, entry_probe)
        # Beginning is None
        self.assertRaises(ValueError, RangeInference.filter_daterange, None,
                          end, entry_probe)
        # End is None
        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          None, entry_probe)


    def test_date_error_date_format(self):
        """
        Tests the errors when the specified date_format is invalid
        """
        begin = date(2020, 1, 1)
        end = date(2020, 1, 5)
        entry_probe = RangeInferenceTest.dummy_entry_probe(begin, end)

        # Pass a list instead of a string
        self.assertRaises(TypeError, RangeInference.filter_daterange, begin,
                          end, entry_probe, date_format=[])


    def test_date_error_entry_probe(self):
        """
        Tests the errors when entry_probe is not supplied
        """

        # Supply None as entry_probe
        begin = date(2000, 1, 1)
        end = date(2020, 1, 1)

        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          end, None)


    def test_date_error_cons_misses(self):
        """
        Tests the errors when the number of consecutive misses is invalid
        """

        begin = date(2000, 1, 1)
        end = date(2020, 1, 1)

        # Supply None as the cons_misses parameter
        self.assertRaises(ValueError, RangeInference.filter_daterange,
                          begin, end, None, 'Y', cons_misses=None)

        # Supply a negative value as cons_misses
        self.assertRaises(ValueError, RangeInference.filter_daterange,
                          begin, end, None, 'Y', cons_misses=-1)


    def test_date_error_extra_params(self):
        """
        Tests the errors when the extra_params value is supplied incorrectly
        """

        begin = date(2000, 1, 1)
        end = date(2020, 1, 1)
        entry_probe = RangeInferenceTest.dummy_entry_probe(begin, end)

        # Supply list with no None entries
        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          end, entry_probe, 'Y', extra_params=[1, 2, 3])

        # Supply list with more than one None entry
        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          end, entry_probe, 'Y', extra_params=[None, 2, None])

        # Supply empty list
        self.assertRaises(ValueError, RangeInference.filter_daterange, begin,
                          end, entry_probe, 'Y', extra_params=[])


    # FORMATTED CODE

    def test_formatted_code_inference(self):
        """
        Tests simple formatted codes
        """

        # 01-01 to 10-10
        first_begin = 1
        first_end = 100
        first_last_entry = 10
        second_begin = 1
        second_last_entry = 10
        second_end = 100
        entry_probe = RangeInferenceTest.dummy_code_probe("-",
                        [first_last_entry, second_last_entry])
        result = RangeInference.filter_formatted_code("{:02}-{:02}",
                              [(first_begin, first_end),
                               (second_begin, second_end)], [True, True],
                              entry_probe)
        final_values = list(map(lambda x: x[-1], result))
        self.assertEqual(final_values, [first_last_entry, second_last_entry])

        # Same as above, but only filter the first parameter
        result = RangeInference.filter_formatted_code("{:02}-{:02}",
                              [(first_begin, first_end),
                               (second_begin, second_end)], [True, False],
                              entry_probe)
        final_values = list(map(lambda x: x[-1], result))
        self.assertEqual(final_values, [first_last_entry, second_end])

        # Now only filter the second parameter
        result = RangeInference.filter_formatted_code("{:02}-{:02}",
                              [(first_begin, first_end),
                               (second_begin, second_end)], [False, True],
                              entry_probe)
        final_values = list(map(lambda x: x[-1], result))
        self.assertEqual(final_values, [first_end, second_last_entry])


    def test_formatted_code_corner_cases(self):
        """
        Tests the behavior of the formatted code inference in some corner cases
        """

        # Entire search space is filled
        first_begin = 1
        first_end = 100
        second_begin = 1
        second_end = 100
        entry_probe = RangeInferenceTest.dummy_code_probe("-",
                        [first_end, second_end])
        result = RangeInference.filter_formatted_code("{:02}-{:02}",
                              [(first_begin, first_end),
                               (second_begin, second_end)], [True, True],
                              entry_probe)
        final_values = list(map(lambda x: x[-1], result))
        self.assertEqual(final_values, [first_end, second_end])

        # Only one entry at the beginning
        entry_probe = RangeInferenceTest.dummy_code_probe("-", [1, 1])
        result = RangeInference.filter_formatted_code("{:02}-{:02}",
                              [(first_begin, first_end),
                               (second_begin, second_end)], [True, True],
                              entry_probe)
        final_values = list(map(lambda x: x[-1], result))
        self.assertEqual(final_values, [1, 1])


    def test_formatted_code_error_range_limits(self):
        """
        Tests the errors raised for invalid range limits
        """

        # End of interval is lower than the beginning
        begin = 100
        end = 1
        entry_probe = RangeInferenceTest.dummy_code_probe("-", [end])
        self.assertRaises(ValueError, RangeInference.filter_formatted_code,
            "{:02}", [(begin, end)], [True], entry_probe)

        # Beginning is None
        self.assertRaises(ValueError, RangeInference.filter_formatted_code,
            "{:02}", [(None, end)], [True], entry_probe)
        # End is None
        self.assertRaises(ValueError, RangeInference.filter_formatted_code,
            "{:02}", [(begin, None)], [True], entry_probe)


    def test_formatted_code_error_code_format(self):
        """
        Tests the errors when the specified code format is invalid
        """

        begin = 1
        end = 100
        entry_probe = RangeInferenceTest.dummy_code_probe("-", [end])
        # Pass a list instead of a string
        self.assertRaises(TypeError, RangeInference.filter_formatted_code, [],
            [(begin, end)], [True], entry_probe)


    def test_formatted_code_error_entry_probe(self):
        """
        Tests the errors when entry_probe is not supplied
        """

        # Supply None as entry_probe
        self.assertRaises(ValueError, RangeInference.filter_formatted_code,
            "{}", [(0, 1)], [True], None)


    # PROCESS CODE

    def test_process_code_inference(self):
        """
        Tests inference of process codes
        """

        first_year = 2010
        last_year = 2020
        segment_ids = [4]
        court_ids = [2]
        origin_ids = [0, 9999]

        LAST_VAL = 20

        def check(x): return int(x[0].split("-")[0]) <= LAST_VAL

        entry_probe = mock.Mock(spec=EntryProbing, check_entry=check)

        result = RangeInference.filter_process_code(first_year, last_year,
                              segment_ids, court_ids, origin_ids, entry_probe)
        self.assertEqual(result, LAST_VAL)


if __name__ == '__main__':
    unittest.main()
