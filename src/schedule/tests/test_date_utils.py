import unittest
from schedule.date_utils import *

class DateUtilsTest(unittest.TestCase):
    def test_date_date_with_invalid_date(self):
        # If a day of month is invalid, get_date should return the last day of the month
        # For example, 31/02/2021 is invalid, so get_date should return 28/02/2021

        year, month, day = 2021, 2, 31
        date = get_date(year, month, day)
        self.assertEqual(date.day, 28) 
    
    def test_get_last_day_of_month(self):
        # get_last_day_of_month should return the last day of the month
        # For example, 31/12/2021 is the last day of the month

        year, month = 2021, 12
        last_day = get_last_day_of_month(month, year)
        self.assertEqual(last_day, 31)

    def test_get_first_weekday_date_of_month(self):
        # get_first_weekday_date_of_month should return the first weekday of the month
        # For example, the first saturday of march of 2023 is 04/03/2023.

        year, month, weekday = 2023, 3, 6
        date = get_first_weekday_date_of_month(weekday, year, month)
        self.assertEqual(date.day, 4)

    def test_get_last_weekday_date_of_month(self):
        # get_last_weekday_date_of_month should return the last weekday of the month
        # For example, the last sunday of april of 2023 is 30/04/2023.

        year, month, weekday = 2023, 4, 0
        date = get_last_weekday_date_of_month(weekday, year, month)
        self.assertEqual(date.day, 30)
    
    def test_weeks_next_execution_date(self):
        # weeks_next_execution_date should return the next execution date given a base date, a list of days of week and a interval between executions
        # For example, the next execution date of 2023-02-01, given a list of days of week [3] (wednesday), interval equal to 1 is 08/02/2023.

        base_date = datetime.datetime(2023, 2, 1)
        days_of_week = [3]
        interval = 1
        date = weeks_next_execution_date(base_date, days_of_week, interval)
        self.assertEqual(date.day, 8)

        # Another example, the next execution date of 2023-02-01, given a list of days of week [0, 2] (sunday and tuesday), interval equal to 3 weeks is 19/02/2023.

        days_of_week = [0, 2]
        interval = 3
        date = weeks_next_execution_date(base_date, days_of_week, interval)
        self.assertEqual(date.day, 19)

        # Another example, the next execution date of 2023-02-01, given a list of days of week [2, 6] (sunday and tuesday), interval equal to 2 weeks is 04/02/2023.

        days_of_week = [2, 6]
        interval = 2
        date = weeks_next_execution_date(base_date, days_of_week, interval)
        self.assertEqual(date.day, 4)

        # But if the list of days is only [2], the next execution date should be 14/02/2023.

        days_of_week = [2]
        interval = 2
        date = weeks_next_execution_date(base_date, days_of_week, interval)
        self.assertEqual(date.day, 14)
    
    def test_month_next_execution_date(self):
        # months_next_execution_date should return the next execution date given a base date, the type of execution (day of month or weekday of month) and a interval between executions
        # For example, the next execution date of 2023-02-01, given a type of execution equal to 'day-x', interval equal to 1 is 01/03/2023.

        base_date = datetime.datetime(2023, 2, 1)
        type_of_execution = 'day-x'
        interval = 1

        date = month_next_execution_date(base_date, type_of_execution, interval)

        self.assertEqual(date.day, 1)
        self.assertEqual(date.month, 3)

        # If the the next month has not the same number of days of the base date, the next execution date should be the last day of the next month.
        # For example, the next execution date of 2023-01-01, given a type of execution equal to 'day-x', day_x = 31 and interval equal to 1 is 28/02/2023.
        # Because the next month (february) has only 28 days.

        base_date = datetime.datetime(2023, 1, 1)
        type_of_execution = 'day-x'
        day_x = 31
        interval = 1

        date = month_next_execution_date(base_date, type_of_execution, day_x, interval=interval)

        self.assertEqual(date.day, 28)
        self.assertEqual(date.month, 2)

        # Another example, the next execution date of 2023-02-01, given a type of execution equal to 'fist-weekday', first_weekday_to_run = 3 (runs every first wednesday of <interval> month), interval equal to 2 is 05/04/2023.
        # Because the next execution date is the first wednesday of march.

        base_date = datetime.datetime(2023, 2, 1)
        type_of_execution = 'first-weekday'
        first_weekday_to_run = 3
        interval = 2

        date = month_next_execution_date(base_date, type_of_execution, first_weekday_to_run=first_weekday_to_run, interval=interval)

        self.assertEqual(date.day, 5)
        self.assertEqual(date.month, 4)

        # Another example, the next execution date of 2023-02-01, given a type of execution equal to 'last-weekday', last_weekday_to_run = 1 (runs every last monday of <interval> month), interval equal to 7 is 25/09/2023.
        # Because the next execution date is the last monday of september.

        base_date = datetime.datetime(2023, 2, 1)
        type_of_execution = 'last-weekday'
        last_weekday_to_run = 1
        interval = 7

        date = month_next_execution_date(base_date, type_of_execution, last_weekday_to_run=last_weekday_to_run, interval=interval)

        self.assertEqual(date.day, 25)
        self.assertEqual(date.month, 9)

    def test_year_next_execution_date(self):
        # year_next_execution_date should return the next execution date given a base date and a interval between executions
        # For example, the next execution date of 2023-02-01, interval equal to 1 is 01/02/2024.

        base_date = datetime.datetime(2023, 2, 1)
        date = year_next_execution_date(base_date, interval=1)

        self.assertEqual(date.day, 1)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.year, 2024)
        
        # However, if the next year has not the same number of days of the base date, the next execution date should be the last day of the next year.
        # For example, the next execution date of 2020-02-29, interval equal to 3 is 28/02/2021.
        # Because the next year (2021) has only 28 days.

        base_date = datetime.datetime(2020, 2, 29)
        date = year_next_execution_date(base_date, interval=3)

        self.assertEqual(date.day, 28)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.year, 2023)

        # Another example, the next execution date of 2020-02-29, interval equal to 4 is 29/02/2024.
        # Because the next year (2024) has 29 days.

        base_date = datetime.datetime(2020, 2, 29)
        date = year_next_execution_date(base_date, interval=4)
        
        self.assertEqual(date.day, 29)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.year, 2024)


    def test_decode_datetimestr(self):
        # decode_datetimestr should return a datetime object given a string with the format %Y-%m-%d %H:%M:%S
        # For example, the datetime object of 2023-02-01 12:00:00 is 2023-02-01 12:00:00.

        date = decode_datetimestr('2023-02-01 12:00:00')

        self.assertEqual(date.day, 1)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.hour, 12)
        self.assertEqual(date.minute, 0)
        self.assertEqual(date.second, 0)

        # Another example, the datetime object of 2023-02-01 12:00:00 is 2023-02-01 12:00:00.

        date = decode_datetimestr('2023-02-01 12:00:00')

        self.assertEqual(date.day, 1)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.hour, 12)
        self.assertEqual(date.minute, 0)
        self.assertEqual(date.second, 0)
