# Range inference module
Collection of helper methods to narrow a range of search space parameters when crawling.

## Main methods and usage
As these methods are not state-dependent, they are implemented as static methods, and therefore don't require a class instance. Each method returns the last parameter value for which we found an entry. Below we give a high level overview of each main method, with examples:

### Core range filter
The `__filter_range` method is a general case of both filters described below, by using a binary search approach for both numerical and date type parameters. It takes in the general information on how to traverse the search space and tries to find out where the entries stop happening.

#### Caveats
We found some websites where we can have an empty interval between two populated ranges for a parameter, for example, if we are generating a numerical parameter between 0 and 1000, we can maybe have entries in values from 0 to 230, then no entries until 260, and then have more entries up to 500. If we ran a simple binary search to find the maximum parameter value, we would stop at 230, missing all entries after that. To avoid this problem, our algorithm looks not only at the middle of a range, but at a certain number of entries after this midpoint, and considers a miss only if no entries were found.

### Number range filter
Checks a range of numerical parameters and finds the maximum value for which we can find an entry.

```
# Dummy check function, as an example (max param value is 100)
hit_check = lambda x: 50 <= x <= 100

RangeInference.filter_numeric_range(0, 1000, hit_check) # 100
```

### Date range filter
Checks a range of date parameters and finds the maximum value for which we can find an entry. Works for daily, monthly or yearly ranges.

```
# Dummy check function, as an example (max param value is date(2010, 1, 1))
hit_check = lambda x: date(2000, 1, 1) <= x <= date(2010, 1, 1)

RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), hit_check)
# datetime.date(2010, 1, 1)
RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), hit_check, 'M')
# datetime.date(2010, 1, 1)
RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), hit_check, 'D')
# datetime.date(2010, 1, 1)
```
