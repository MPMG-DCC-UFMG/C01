# Antiblock driver module
General antiblock module for libraries other than Scrapy. Supported features:

- User-agent rotation
- Delay between requests
    - Fixed delay
    - Auto-throttle
- IP Rotation
    - Tor
    - Proxy list
- Cookie management

Currently only supports the Requests library. Will support Pyppeteer in the
future.

**IP-rotation using Tor requires Tor to be installed, and switches system-wide
IP values in Tor. Be mindful of possible conflicts.**

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, run the following command in the
`antiblock_drivers` folder, replacing the file name accordingly:

```
pip install dist/<wheel file name>
```

## Components

### General Antiblock

The `antiblock_general` module implements the base skeleton for more specific
anti-blocking implementations. These implementations should inherit from the
`AntiblockDriver` class, and can use the `_send_request` method to wrap request
calls using specific libraries. If more flexibility is desired, the main class
methods can be used directly. The configurations for this class (and
subclasses) are passed in a dictionary sent to the constructor.

#### Configuration settings

Below are all the options received by the constructor:

- **rotate_user_agent_enabled** Enables the user-agent rotation
- **user_agents** List of user-agents to be rotated
- **min_user_agent_usage** Minimum number of times to use a single user-agent
value
- **max_user_agent_usage** Maximum number of times to use a single user-agent
value
- **download_delay** Seconds to wait between consecutive requests
- **download_delay_randomize** Enable randomization of delay values (if
enabled, a random value between 0.5 * **download_delay** and 1.5 *
**download_delay** is picked after every request)
- **autothrottle_enabled** Enable the AutoThrottle algorithm (described
[here](https://docs.scrapy.org/en/latest/topics/autothrottle.html#throttling-algorithm))
- **autothrottle_start_delay** Initial delay for AutoThrottle, if enabled
- **autothrottle_max_delay** Maximum delay allowed during AutoThrottle, if
enabled
- **iprotator_enabled** Enable IP-rotation
- **iprotator_type** IP-rotator type (Tor or proxy list)
- **tor_iprotator_change_after** Number of times a single IP value can be
re-used by Tor, if enabled
- **tor_iprotator_allow_reuse_ip_after** Number of different IPs to be used bY
Tor before repeating, if enabled
- **iprotator_proxy_list** List of proxies to be used, if enabled (supplied
proxies are used consecutively)
- **insert_cookies** Enable cookie insertion
- **cookies** List of dictionaries containing key-value pairs to be used as
cookies, if enabled

#### Main methods:

##### `_send_request`
Does the following procedures:

- Generates the next user-agent value, applying the rotation if necessary
- Generates the next IP value, applying the rotation if necessary
- Generates the correct headers, cookies and proxies to be sent to the request
- Applies the necessary delay
- Calls the the supplied request function, sending in the values calculated in
the previous step
- Calculates the next delay value

In general, to implement an anti-block driver for a new library, one should
call this method sending in the request function for this library. It should
accept the `headers`, `cookies` and `proxies` parameters. In case the specific
library function doesn't support these parameter names specifically, a wrapper
function can be used. If this method is not flexible enough for some use case,
the other methods can be invoked directly.

##### `_generate_next_delay`

Generates the value for the delay to be applied before doing the next request.
Can use a fixed delay, a randomized delay or the AutoThrottle algorithm.

##### `_get_current_user_agent`
Gets the current user agent to use, and applies the rotation if necessary.

##### `_apply_delay`
Waits for the configured amount of time, previously calculated by the
`_generate_next_delay` method.

##### `_generate_headers`
Generates the headers for the next request, with the correct user-agent value.

##### `_generate_proxies`
Generates the proxies for the next request, considering the given list or the
Tor configuration, if supplied.

##### `_generate_cookies`
Generates the cookies for the next request.

### Requests Antiblock
Wrapper for calls to the `requests` library, subclass of `AntiblockDriver`.
Takes in the configuration dictionary as the only parameter to the constructor,
and after being instantiated can be used as a proxy to the methods in the
`requests` module.

The available methods are:

- `request()`
- `get()`
- `post()`
- `put()`
- `delete()`
- `head()`
- `patch()`

#### Example usage
```
from antiblock_drivers import AntiblockRequests

req = AntiblockRequests({
    'rotate_user_agent_enabled': True,
    'user_agents': ['A', 'B', 'C'],
    'min_user_agent_usage': 1,
})

# The requests will have 'A', 'B', and 'C' as their respective user-agents
req.get('https://example.com/')
req.post('https://example.com/')
req.head('https://example.com/')
```

### Pyppeteer Antiblock
To be added.
