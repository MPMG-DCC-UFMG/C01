# Entry probing module
Entry probing module to check for an entry's existence in the website to be
crawled. There are three main components: the Probing Request, Probing Response,
and the Entry Probing which encapsulates both parts.

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, run the following command in the
`entry_probing` folder, replacing the file name accordingly:

```
pip install dist/<wheel file name>
```

## Components

### Probing request
The request classes define how the request to the desired URL should be made.
They all inherit from the abstract `ProbingRequest` class, and should implement
the `process` method, which returns a `ResponseData` object obtained from the
URL with the specified parameters. The parameters are provided to the class
through its constructor, and the entry identifier is provided as an argument
to the `process` method.

#### ProbingRequest
Abstract class, defines the interface for a probing request through the
`process` abstract method.

#### GETProbingRequest
Implements a GET request handler. Receives an URL to request with possible
placeholders. The `process` method receives an optional entry identifier to be
inserted in the URL, generates the target URL and uses the `requests.get`
method to get a response, which is returned as a `ResponseData` entry.

```
req = GETProbingRequest("http://test.com/{}")
req.process(10)
# creates a request handler which sends a GET request to http://test.com/10
# when the process method is called
```

#### POSTProbingRequest
Implements a POST request handler. Receives an URL to request, as well as the
name of the parameter to be inserted in the request body. It optionally
receives extra data to be included. The `process` method receives the entry
identifier to insert in the request body and uses the `requests.post` method to
send the data and get a response, which is returned as a `ResponseData` entry.

```
req = POSTProbingRequest("http://test.com/", "test_prop")
req.process(100)
# creates a request handler which will send a POST request to http://test.com/
# and a dictionary with the key-value pair {"test_prop": 100} in the request
# body when the process method is called
```

#### PyppeteerProbingRequest
Implements a Pyppeteer request handler. Receives an instance of
`pyppeteer.page.Page`, which is the page where the desired URL will be loaded.
In its constructor, it adds a `response` event to the supplied page so that we
can capture the response when we access the URL. The request must be done
manually outside of this class, and before the call to `process` is made. The
`process` method gets the response and returns it as a `ResponseData` instance,
overwriting the `text` property with the text of the currently open page. **The
HTTP headers and status code are captured from the first response received by
the Pyppeteer page after the constructor is called, but the text is collected
from the page contents when the process() method is called. This may cause
synchronization issues if multiple pages are requested in sequence between
these calls (e.g.: it will analyse the response to the first page request, and
the text contents of the last page).** All methods are implemented as
coroutines, since Pyppeteer works asynchronously.

```
browser = await launch()
page = await browser.newPage()
req = PyppeteerProbingRequest()
await page.goto("http://test.com")
req.process()
# creates a request handler which will capture the response received when the
# request to http://test.com is sent
```

### Probing response
The response classes define which responses obtained should be considered valid.
They all inherit from the abstract `ProbingResponse` class, and should implement
the `_validate_resp` method, which gets a `ResponseData` object and returns a
boolean indicating if it is valid or not. The parameters are provided to the
class through its constructor. The `process` method is defined in the main
`ProbingResponse` class, and returns the validation result using the
`_validate_resp` method and the `opposite` attribute.

#### ResponseData
A general wrapper for responses from any source. Contains the headers, HTTP
status code and text content of a response. Has class methods to create an
instance out of a `requests.models.Response` instance as well as a
`pyppeteer.network_manager.Response` instance. If a response is detected to
have a binary type, the text content is set to an empty string.

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
and determine if an entry has been hit or not. The `check_entry` method takes
in the entry identifier to be sent to the request handler. The
`async_check_entry` coroutine does the same as `check_entry`, except that it
works asynchronously by awaiting the result of calling the `process` method in
the `ProbingRequest` instance. This is used for working with Pyppeteer.


#### EntryProbing
Encapsulates the entire probing process and validates an entry. After checking,
the response is stored in the probe's `response` property

```
probe = EntryProbing(GETProbingRequest("http://test.com/{}"))
probe.add_response_handler(HTTPStatusProbingResponse(200))\
     .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
     .add_response_handler(TextMatchProbingResponse("entry found"))

probe.check_entry(100)
# Sends a GET request to "http://test.com/100", and returns true if the
# response has an HTTP status of 200, is textual and contains the text
# "entry found"

probe.response # Returns the obtained response
```

Another example, using Pyppeteer

```
browser = await launch()
page = await browser.newPage()

probe = EntryProbing(PyppeteerProbingRequest(page))
probe.add_response_handler(HTTPStatusProbingResponse(200))\
     .add_response_handler(BinaryFormatProbingResponse(opposite=True))\
     .add_response_handler(TextMatchProbingResponse('entry found'))

await page.goto("http://test.com/")

is_valid = await probe.async_check_entry()

await browser.close()
```
