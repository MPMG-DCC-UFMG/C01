# Step crawler module
Back-end to create interactive crawlers through web interfaces, similar
 to the idea in `https://scratch.mit.edu/`.

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the source code you need to have `setuptools` and `wheel` installed. After both packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary depending on the version. To install it, run the following command in the `step-by-step` folder, replacing the file name accordingly:

```
pip install dist/<wheel file name>
```


## Features

### Functions file

File containing some implemented functions. These functions later turn into steps, such as:
```
click
send_keys
save_page
...
```

### Parameter extraction mechanism

Mechanism that reads a file with functions and creates a json with a list where each element contains the name of a function, its required parameters and its optional parameters.


### Steps json

The json with steps created by the interface should have a structure similar to the one already created, with the difference that now, in order to be transformed into code, each element of that json would be a line of code.

Example:
```
{
    "name": "for",
    "iterator_name": "i",
    "iterable": [“1”,”2”,”3”],
    "depth": 0,
    "children": [
        {
            "name": "send_keys",
            "parameters": {"xpath": "/body/div[‘+i+’]", "keys": "exemplo"}
            "depth": 1,
        }
    ]
}
```

All steps, which are not structural as loops, ifs and assignments, would have at least three keys: function name, parameters, and depth. The depth informs how much indentation to give when turning this step into a line of code.

### Atomizer

In a case where there is a “for” step that iterates using “i” in [1,2,3], for example, the mechanism would create another 3 jsons replacing each 'for' call by a step to assign an element of that list to variable “i” and subtract 1 from the depth of all steps that were within that iteration. To better illustrate, what happens in terms of code is:

```
for i in [“1”,”2”]:
    send_keys(xpath= "/body/div["+i+"]", keys= "exemplo")
```

After being atomized, the new json step files would be:

1st json:
```
i = “1”
send_keys(xpath= "/body/div["+i+"]", keys= "exemplo")
```
2nd json:
```
i = “2”
send_keys(xpath= "/body/div["+i+"]", keys= "exemplo")
```

### Code generator

In the json created by the interface, there must be two types of steps, the structural ones (if, for, assignment) and those that simply represent a function call.

For those that represent function calls, basically what needs to be done is getting the name of this function in the json, with its parameters and its depth. In this way, the depth tells us the indentation and we only need to assemble the function by its name and passing the parameters.

For structural steps, a more specific json configuration will be required. Something as described in the examples above where the "for" was used.

Example:
```
{
    "name": "attribution",
    "source": "1",
    "target": “i”,
    "depth": 0,
},
{
    "name": "send_keys",
    "parameters": {"xpath": "/body/div[‘+i+’]", "keys": "exemplo"}
    "depth": 0,
}
```

Generates the code:
```
i = 1
send_keys(xpath= "/body/div["+i+"]", keys= "exemplo")
```

## TODO
[ ] Function to process `except` conditions
[ ] Function to extract all links from a page
[ ] Function to generate through url-encoded pagination  
