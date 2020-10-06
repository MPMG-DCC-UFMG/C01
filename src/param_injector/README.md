# Parameter injection module
Collection of helper methods to generate most common cases for search ranges during web crawling.

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, run the following command in the
`param_injector` folder, replacing the file name accordingly:

```
pip install dist/<wheel file name>
```

## Main methods and usage
As these methods are not state-dependent, they are implemented as static methods, and therefore don't require a class instance. Each method returns a Python generator, over which we can iterate to get all possible values. Below we give a high level overview of each main method, with examples:

### Format generator
Generates strings according to a specified format and parameter ranges. It is capable of generating validation codes as needed.

```
gen = ParamInjector.generate_format('{}-{}', [(1996, 2000)], lambda x: x % 10, 1)
list(gen) # ['1996-6', '1997-7', '1998-8', '1999-9', '2000-0']
```

### Number sequence generator
Generates a sequence of numbers between two values with a given step size. By default adds leading zeros to the values so that they have the same number of digits.

```
gen = ParamInjector.generate_num_sequence(0, 10)
list(gen) # ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
gen = ParamInjector.generate_num_sequence(10, 0, -1)
list(gen) # ['10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
gen = ParamInjector.generate_num_sequence(10, 0, -1, False)
list(gen) # ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
```

### Alphabetic search query generator
In some websites we can search for entries by using search parameters with wildcards (e.g.: "a\* a\*" returns all entries where the first and second names begin with an 'a'). This generates such parameters. The word length and number of words can be specified. It has options to use just lowercase letters or both upper and lowercase letters.

```
gen = ParamInjector.generate_alpha(2, 2)
list(gen) # ['aa* aa*', 'aa* ab*', 'aa* ac*', ..., 'zz* zx*', 'zz* zy*', 'zz* zz*']
gen = ParamInjector.generate_alpha(2, 2, True)
list(gen) # ['aa* aa*', 'aa* ab*', 'aa* ac*', ..., 'ZZ* ZX*', 'ZZ* ZY*', 'ZZ* ZZ*']
```

### Date range generator
Generates strings representing a range of dates between two limits. The output format and date granularity (day, month or year) can be specified.

```
gen = ParamInjector.generate_daterange('%Y', datetime.date(2000,1,1), datetime.date(2003,1,1))
list(gen) # ['2000', '2001', '2002', '2003']

gen = ParamInjector.generate_daterange('%Y-%m-%d', datetime.date(2000,1,1), datetime.date(2000,1,5), "D")
list(gen) # ['2000-01-01', '2000-01-02', '2000-01-03', '2000-01-04', '2000-01-05']
```