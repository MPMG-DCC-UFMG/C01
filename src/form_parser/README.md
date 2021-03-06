Form parser module for web crawling. 

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, run the following command in the
`form_parser` folder, replacing the file name accordingly:

```
pip install dist/<wheel file name>
```
 
### Features
- Extracts parameters from URLs using urllib.parse

#### URLParser
```
from formparser import URLParser
Parser = URLParser("myurl.com/param=value1&param2=value2")
Parser.query() # param1=value1&param2=value2
Parser.parameters() # {'param1': 'value1', 'param2': 'value2'}
```

- Extracts parameters from HTML forms using lxml.etree and XPaths
#### HTMLParser
```
from formparser import HTMLExtractor, HTMLParser
HTML = HTMLExtractor("myurl.com/param=value1&param2=value2")
form_list = HTML.get_forms()
for form in form_list:
    ParsedForm = HTMLForm(form)
```
- List possible input types

```ParsedForm.unique_field_types() # -> list(str), ['text', 'radio', 'select']```
- Count number of fields available

```ParsedForm.number_of_fields() # -> int```

- Retrieve full list of inputs

```ParsedForm.list_input_types() # -> list(str), ['text', 'text', 'radio', 'select', 'select', ...]```
- Retrieve list of inputs' labels

```ParsedForm.list_input_labels() # -> list(str), ['Name', 'Phone', 'Year', 'City', 'State', ...]```
- Retrieve field types and <Element input>

```ParsedForm.fields() # -> dict, {'field_type': [<Element input 1>, <Element input 2>], ...}```

- List required fields
```ParsedForm.required_fields(probing_element) # -> list(element_xpath)``` 
where `probing_element` identifies what to look for when the form submission
 is successful. `probing_element` can also be a a constructed object of the
  class EntryProbing, from the `entry_probing` lib.

- Retrieve dynamic fields
```ParsedForm.dynamic_fields() # -> dict, {'field1_xpath': ['field2_xpath', 'field3_xpath'], ...}```

- List select fields
```ParsedForm.select_fields() # -> list(<Element select>)```

- List option fields
```ParsedForm.option_fields() # -> list(<Element option>)```

- For each ```<Element>```, retrieve its attributes by using ```ParsedForm.list_field_attributes(field)```. Example:

```
text_fields = ParsedForm.fields()['text']  
for text_field in text_fields:
    ParsedForm.list_field_attributes(text_field) # -> dict, {'type': 'text', 'maxlength': 6, 'name': 'usrname', 'required': ''}
``` 

- For each ```<Element option>```, retrieve its parent select field by using ```ParsedForm.get_parent_field(field)```. Example:

```
option_fields = ParsedForm.option_fields()  
for option_field in option_fields:
    ParsedForm.get_parent_field(option_field) # -> <Element select> 
``` 
Note: also works for other types of `<Element>` objects

- Retrieve a select field with its respective options:
```ParsedForm.select_with_option_fields() # -> dict, {<Element select1>: [<Element option1>, <Element option2>, ...], ...}```


### TODO
- [ ] Parse custom format types
- [ ] Extract and parse non-HTML forms
- [ ] Find select options to be ignored (e.g. "Selecione")
- [ ] Increase test coverage