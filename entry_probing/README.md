# Entry probing module
Entry probing module to check for an entry's existence in the website to be
crawled. There are three main components: the Probing Request, Probing Response,
and the Entry Probing which encapsulates both parts.

## Building

This module is packaged as a Python Wheel file. To install it, run the following
command in the `entry_probing` folder:

```
pip install dist/entry_probing-0.1-py3-none-any.whl
```

To build the .whl file from the source code you need to have the `setuptools`
and `wheel` packages installed. After both packages are installed, run:

```
python setup.py bdist_wheel
```

## Components

### Probing request
The request classes define how the request to the desired URL should be made.
They all inherit from the abstract `ProbingRequest` class, and should implement
the `process` method, which returns a `requests.models.Response` object obtained
from the URL with the specified parameters. The parameters are provided to the
class through its constructor.

#### ProbingRequest
Abstract class, defines the interface for a probing request through the
`process` abstract method.

#### GETProbingRequest
Implements a GET request handler. Receives an URL to request with possible
placeholders, and an optional entry identifier to be inserted in the URL. The
`process` method generates the target URL and uses the `requests.get` method to
get a response.

```
req = GETProbingRequest("http://test.com/{}", 10)
# creates a request handler which will send a GET request to http://test.com/10
# when the process method is called
```

#### POSTProbingRequest
Implements a POST request handler. Receives an URL to request, as well as the
name of the parameter to be inserted in the request body and the value to
insert. It optionally receives extra data to be included. The `process` method
uses the `requests.post` method to send the data and get a response.

```
req = POSTProbingRequest("http://test.com/", "test_prop", 100)
# creates a request handler which will send a POST request to http://test.com/
# and a dictionary with the key-value pair {"test_prop": 100} in the request
# body when the process method is called
```

### Probing response
The response classes define which responses obtained should be considered valid.
They all inherit from the abstract `ProbingResponse` class, and should implement
the `_validate_resp` method, which gets a `requests.models.Response` object and
returns a boolean indicating if it is valid or not. The parameters are provided
to the class through its constructor. The `process` method is defined in the
main `ProbingResponse` class, and returns the validation result using the
`_validate_resp` method and the `opposite` attribute.

#### ProbingResponse
Abstract class, defines the interface for a probing response handler through the
`_validate_resp` abstract method. It also defines the `process` method, which
calls `_validate_resp` and inverts the output depending on the value of the
`opposite` attribute.

#### HTTPStatusProbingResponse
Implements a response handler which validates responses with a given HTTP status
code.

```
resp_handler = HTTPStatusProbingResponse(200)
# Validates a response with HTTP status 200
resp_handler = HTTPStatusProbingResponse(404, opposite=True)
# Validates a response with any HTTP status besides 404
```

#### TextMatchProbingResponse
Implements a response handler which validates responses with a given text within
their body. (case sensitive)

```
resp_handler = TextMatchProbingResponse("Page found")
# Validates a response which has the text "Page found" within its body
```

#### BinaryFormatProbingResponse
Implements a response handler which validates responses with a non-textual
MIME-type.

```
resp_handler = BinaryFormatProbingResponse()
# Validates a binary response
# (e.g. with a MIME-type of application/vnd.ms-excel)
resp_handler = BinaryFormatProbingResponse(opposite=True)
# Validates a text response
# (e.g. with a MIME-type of text/json)
```

### Entry Probing
This component contains a single class, `EntryProbing`, which encapsulates the
request and response mechanisms described above into a single unit to check for
an entry's existence. The `ProbingRequest` instance is obtained through the
constructor, and the `ProbingResponse` instances are added through the
`add_response_handler` method. After the request and response handlers are
properly set, the `check_entry` method can be used to execute the whole process
and determine if an entry has been hit or not.

#### EntryProbing
Encapsulates the entire probing process and validates an entry.

```
probe = EntryProbing(GETProbingRequest("http://test.com/"))
probe.add_response_handler(HTTPStatusProbingResponse(200))\
     .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
     .add_response_handler(TextMatchProbingResponse("entry found"))

probe.check_entry()
# Sends a GET request to "http://test.com/", and returns true if the response
# has an HTTP status of 200, is textual and contains the text "entry found"
```
