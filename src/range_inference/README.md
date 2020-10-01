# Range inference module
Collection of helper methods to narrow a range of search space parameters when crawling.

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, you must have the `entry_probing`
module installed. Run the following command in the `range_inference` folder,
replacing the file name accordingly:

```
pip install dist/<wheel file name>
```

## Probing mechanism
The `entry_probing` module is used to check for an entry's existence. It
abstracts the whole process of requesting and validating the response, so that
the range inference can focus on the filtering itself. More details can be found
in the README file for `entry_probing`. We provide an example of how the probing
module and this range inference should be used in conjunction:

```
# Creates a probe which visits a website and checks for a 200 HTTP status, a
# text response, and the text "entry found" in the response's content
probe = EntryProbing(HTTPProbingRequest("http://test.com/{}", "GET"))
probe.add_response_handler(HTTPStatusProbingResponse(200))\
     .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
     .add_response_handler(TextMatchProbingResponse("entry found"))

# Uses the given probe to run the filtering method and check which entries are
# valid
RangeInference.filter_numeric_range(0, 1000, probe)
```

## Main methods and usage
As these methods are not state-dependent, they are implemented as static methods, and therefore don't require a class instance. Each method returns the last parameter value for which we found an entry. Below we give a high level overview of each main method, with examples:

### Core range filter
The `__filter_range` method is a general case of both filters described below, by using a binary search approach for both numerical and date type parameters. It takes in the general information on how to traverse the search space and tries to find out where the entries stop happening.

#### Caveats
We found some websites where we can have an empty interval between two populated ranges for a parameter, for example, if we are generating a numerical parameter between 0 and 1000, we can maybe have entries in values from 0 to 230, then no entries until 260, and then have more entries up to 500. If we ran a simple binary search to find the maximum parameter value, we would stop at 230, missing all entries after that. To avoid this problem, our algorithm looks not only at the middle of a range, but at a certain number of entries after this midpoint, and considers a miss only if no entries were found.

### Number range filter
Checks a range of numerical parameters and finds the maximum value for which we can find an entry.

```
from unittest import mock

def check(x): lambda x: 50 <= x <= 100
# Mock of an EntryProbing instance, used as an example (max param value is 100)
entry_probe = mock.MagicMock(spec=EntryProbing, check_entry=check)

RangeInference.filter_numeric_range(0, 1000, entry_probe) # 100
```

### Date range filter
Checks a range of date parameters and finds the maximum value for which we can find an entry. Works for daily, monthly or yearly ranges.

```
from unittest import mock

def check(x): lambda x: date(2000, 1, 1) <= x <= date(2010, 1, 1)
# Mock of an EntryProbing instance, used as an example (max param value is date(2010, 1, 1))
entry_probe = mock.MagicMock(spec=EntryProbing, check_entry=check)

RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), entry_probe)
# datetime.date(2010, 1, 1)
RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), entry_probe, 'M')
# datetime.date(2010, 1, 1)
RangeInference.filter_daterange(date(2000, 1, 1), date(2020, 1, 1), entry_probe, 'D')
# datetime.date(2010, 1, 1)
```
