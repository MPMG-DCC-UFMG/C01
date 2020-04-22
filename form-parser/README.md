Form parser module for web crawling. 
 
### Features
- Extracts parameters from URLs using urllib.parse

#### URLParser
```
from form_parser import URLParser
Parser = URLParser("myurl.com/param=value1&param2=value2")
Parser.query() # param1=value1&param2=value2
Parser.parameters() # {'param1': 'value1', 'param2': 'value2'}
```

- Extracts parameters from HTML forms using lxml.etree and XPaths
#### HTMLParser
```
from form_parser import HTMLExtractor, HTMLForm
HTML = HTMLExtractor("myurl.com/param=value1&param2=value2")
form_list = HTML.get_forms()
for form in form_list:
    ParsedForm = HTMLForm(form)
```
- List possible input types

```ParsedForm.list_field_types() # -> list(str), ['text', 'radio', 'select']```
- Count number of fields available

```ParsedForm.get_number_fields() # -> int```

- Retrieve full list of inputs

```ParsedForm.input_types() # -> list(str), ['text', 'text', 'radio', 'select', 'select', ...]```
- Retrieve field types and <Element input>

```ParsedForm.fields() # -> dict, {'field_type': [<Element input 1>, <Element input 2>], ...}```

- List required fields
```ParsedForm.required_fields() # -> list(<Element input>)``` 

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
    ParsedForm.get_parent_field(option_field) # -> ```<Element select>``` 
``` 

Note: also works for other types of ```<Element>``` objects

### TODO
- [ ] Parse custom format types
- [ ] Extract and parse non-HTML forms
- [ ] Find void select options
- [ ] Increase test coverage 
