**Scrapy and Puppeteer**

Scrapy middleware to handle javascript pages using [puppeteer](https://github.com/GoogleChrome/puppeteer).

The main issue when running Scrapy and Puppeteer together is that Scrapy is using [Twisted](https://twistedmatrix.com/trac/) and that [Pyppeteeer](https://miyakogi.github.io/pyppeteer/) (the python port of puppeteer we are using) is using [asyncio](https://docs.python.org/3/library/asyncio.html) for async stuff. 

Luckily, we can use the Twisted's [asyncio reactor](https://twistedmatrix.com/documents/18.4.0/api/twisted.internet.asyncioreactor.html) to make the two talking with each other.

That's why you **cannot** use the buit-in `scrapy` command line (installing the default reactor), you will have to use the `scrapyp` one, provided by this module.

If you are running your spiders from a script, you will have to make sure you install the asyncio reactor before importing scrapy or doing anything else:

```python
import asyncio
from twisted.internet import asyncioreactor

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    asyncioreactor.install(loop)
except Exception:
    pass
```


## Installation
```
$ python install src/scrapy_puppeteer
```

## Configuration
Add the `PuppeteerMiddleware` to the downloader middlewares:
```python
DOWNLOADER_MIDDLEWARES = {
    'scrapy_puppeteer.PuppeteerMiddleware': 800
}
```


## Usage
Use the `scrapy_puppeteer.PuppeteerRequest` instead of the Scrapy built-in `Request` like below:
```python
from scrapy_puppeteer import PuppeteerRequest

def your_parse_method(self, response):
    # Your code...
    yield PuppeteerRequest('http://httpbin.org', self.parse_result)
```
The request will be then handled by puppeteer.

The `selector` response attribute work as usual (but contains the html processed by puppeteer).

```python
def parse_result(self, response):
    print(response.selector.xpath('//title/@text'))
```

### Additional arguments
The `scrapy_puppeteer.PuppeteerRequest` accept 4 additional arguments:

#### `wait_until`

Will be passed to the [`waitUntil`](https://miyakogi.github.io/pyppeteer/_modules/pyppeteer/page.html#Page.goto) parameter of puppeteer.
Default to `domcontentloaded`.

#### `wait_for`
Will be passed to the [`waitFor`](https://miyakogi.github.io/pyppeteer/reference.html?highlight=image#pyppeteer.page.Page.waitFor) to puppeteer.

#### `screenshot`
When used, puppeteer will take a [screenshot](https://miyakogi.github.io/pyppeteer/reference.html?highlight=headers#pyppeteer.page.Page.screenshot) of the page and the binary data of the .png captured will be added to the response `meta`:
```python
yield PuppeteerRequest(
    url,
    self.parse_result,
    screenshot=True
)

def parse_result(self, response):
    with open('image.png', 'wb') as image_file:
        image_file.write(response.meta['screenshot'])
```

#### `steps`
Will be passed to the code generator. These are the steps the user configured in the interface.