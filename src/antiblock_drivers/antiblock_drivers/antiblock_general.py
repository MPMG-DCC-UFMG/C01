"""
Implementation of the general anti-blocking measures, to be used more
concretely by sub-classes.
"""
from itertools import cycle
from typing import Any, Callable, Dict, Optional

import logging
import random
import time

from toripchanger import TorIpChanger


class AntiblockDriver():
    """
    General implementation for anti-blocking procedures. The _send_request
    method should be used by subclasses to send a request with anti-blocking
    mechanisms in place. The other methods can be used for cases that require
    more flexibility.
    """

    def __validate_user_agent_config(self):
        """
        Validate the user-agent configurations, raising an error if necessary
        """

        # Validate the list of user-agents
        if not isinstance(self.user_agent_list, list) or \
           len(self.user_agent_list) == 0:
            raise ValueError(('If user-agent rotation in enabled, a '
                'non-empty list of user-agents must be supplied.'))

        # Validate the minimum UA usage
        if not isinstance(self.ua_rotate_min_usage, int) or \
           self.ua_rotate_min_usage <= 0:
            raise TypeError(('The minimum user-agent usage should be a '
                'positive integer'))

        # Validate the maximum UA usage
        if not isinstance(self.ua_rotate_max_usage, int) or \
           self.ua_rotate_max_usage <= 0:
            raise TypeError(('The maximum user-agent usage should be a '
                'positive integer'))

        # Validate the overall range of possible UA usage values
        if self.ua_rotate_min_usage > self.ua_rotate_max_usage:
            raise ValueError('The maximum user-agent usage should be '
                'greater than the minimum usage.')

    def __validate_delay_config(self):
        """
        Validate the delay configurations, raising an error if necessary
        """

        if not isinstance(self.download_delay, (int, float)) or \
           self.download_delay < 0:
            raise ValueError('The download delay should be a positive number.')

    def __validate_autothrottle_config(self):
        """
        Validate the autothrottle configurations, raising an error if
        necessary
        """

        if not isinstance(self.at_start_delay, (int, float)) or \
                self.at_start_delay < 0:
            raise ValueError('The autothrottle start delay should be a '
                             'positive number.')
        if not isinstance(self.at_max_delay, (int, float)) or \
                self.at_max_delay < 0:
            raise ValueError('The autothrottle maximum delay should be a '
                             'positive number.')

    def __validate_ip_tor_config(self):
        """
        Validate the ip rotation configurations when using tor, raising an
        error if necessary
        """

        if not isinstance(self.ip_change_after, int) or \
                self.ip_change_after < 0:
            raise ValueError('The number of times an IP can be used in '
                             'succession should be a positive integer.')
        if not isinstance(self.ip_reuse_after, int) or self.ip_reuse_after < 0:
            raise ValueError('The number of different IPs to be used before '
                             'repeating should be a positive number.')

    def __validate_ip_proxy_config(self):
        """
        Validate the ip rotation configurations when using proxies, raising an
        error if necessary
        """

        if not isinstance(self.proxy_list, list):
            raise ValueError('A valid list of proxies must be supplied.')

    def __validate_cookie_config(self):
        """
        Validate the cookie injection configurations, raising an error if
        necessary
        """

        if not isinstance(self.cookies, list):
            raise ValueError('A valid list of cookies must be supplied.')

    def __setup_ip_rotation(self, antiblock_config: Dict[str, Any] = {}):
        """
        Setup the configurations for the ip rotation
        """

        rot_type = antiblock_config["iprotator_type"]
        self.ip_rotation_type = rot_type
        if rot_type == 'tor':
            self.ip_change_after = antiblock_config\
                .get('tor_iprotator_change_after', 1)
            self.ip_reuse_after = antiblock_config\
                .get('tor_iprotator_allow_reuse_ip_after', 10)
            self.__validate_ip_tor_config()

            self.tor_controller = TorIpChanger(
                reuse_threshold=self.ip_reuse_after
            )
            self.tor_controller.get_new_ip()
        elif rot_type == 'proxy':
            self.proxy_list = antiblock_config.get('iprotator_proxy_list', [])
            self.__validate_ip_proxy_config()
        else:
            raise ValueError('Invalid ip rotation type: ' + rot_type)

    def __init__(self, antiblock_config: Dict[str, Any] = {}):
        """
        Constructor for the generic antiblock driver.

        :param antiblock_config: Dictionary of configuration parameters for the
                                 antiblock measures
        """
        self.ua_items_scraped = 0
        self.ip_items_scraped = 0

        self.ua_rotate = antiblock_config\
            .get('rotate_user_agent_enabled', False)

        if self.ua_rotate:
            self.user_agent_list = antiblock_config.get('user_agents', [])

            self.ua_rotate_min_usage = antiblock_config\
                .get('min_user_agent_usage', 1)
            self.ua_rotate_max_usage = antiblock_config\
                .get('max_user_agent_usage', self.ua_rotate_min_usage)

            self.ua_rotate_limit_usage = random\
                .randint(self.ua_rotate_min_usage, self.ua_rotate_max_usage)

            self.__validate_user_agent_config()

            self.user_agents = cycle(self.user_agent_list)
            self.user_agent = next(self.user_agents)

        self.time_last_request = None
        self.current_delay = None
        self.download_delay = antiblock_config.get('download_delay', 0.25)
        self.randomize_delay = antiblock_config\
            .get('download_delay_randomize', True)
        self.__validate_delay_config()

        self.at_enabled = antiblock_config.get('autothrottle_enabled', False)
        if self.at_enabled:
            self.at_start_delay = antiblock_config\
                .get('autothrottle_start_delay', 5)
            self.at_max_delay = antiblock_config\
                .get('autothrottle_max_delay', 60)
            self.__validate_autothrottle_config()

        self.current_delay = 0

        self.ip_rotate = antiblock_config.get('iprotator_enabled', False)
        if self.ip_rotate:
            self.__setup_ip_rotation(antiblock_config)

        self.insert_cookies = antiblock_config.get('insert_cookies', False)
        if self.insert_cookies:
            self.cookies = antiblock_config.get('cookies', [])
            self.__validate_cookie_config()

    def _generate_next_delay(self,
                             response_latency: float = 0,
                             last_status: int = 0):
        """
        Generates the value for the delay to be applied before doing the next
        request.

        :param response_latency: time taken by the last request in seconds
        :param last_status:      HTTP status received from the last request
        """
        if self.at_enabled:
            # Autothrottle
            if self.current_delay is None or self.time_last_request is None:
                self.current_delay = self.at_start_delay
            else:
                next_delay = (response_latency + self.current_delay) / 2

                # Non-200 responses can't decrease the delay
                if last_status == 200 or next_delay > self.current_delay:
                    # Clamp delay between values supplied by the user
                    min_delay = self.download_delay
                    max_delay = self.at_max_delay
                    clamped = max(min_delay, min(max_delay, next_delay))

                    self.current_delay = clamped
        else:
            # Normal delay
            if self.randomize_delay:
                self.current_delay = self.download_delay * \
                    random.uniform(0.5, 1.5)
            else:
                self.current_delay = self.download_delay

    def _get_current_user_agent(self) -> Optional[str]:
        """
        Get the current user agent to use, and apply the rotation if necessary

        :returns: A string representing the user-agent to use for the next
                  request, or None if user-agent rotation is disabled
        """
        if self.ua_rotate:
            if self.ua_items_scraped >= self.ua_rotate_limit_usage:
                self.ua_items_scraped = 0
                self.ua_rotate_limit_usage = random.randint(
                    self.ua_rotate_min_usage,
                    self.ua_rotate_max_usage
                )

                self.user_agent = next(self.user_agents)

            self.ua_items_scraped += 1
            return self.user_agent
        else:
            return None

    def _apply_delay(self):
        """
        Wait for the configured amount of time, previously calculated by the
        _generate_next_delay method.
        """

        last_req = self.time_last_request
        elapsed = None
        if last_req is None:
            elapsed = self.current_delay
        else:
            elapsed = time.perf_counter() - self.time_last_request

        if self.time_last_request is None or elapsed < self.current_delay:
            # Wait for the remaining time
            remaining = self.current_delay - elapsed
            time.sleep(remaining)

    def _generate_headers(self, headers: Dict[str, Any] = {}):
        """
        Generate the headers for the next request, with the correct user-agent
        value.

        :param headers: Dictionary of extra values to be included in the header

        :returns: The headers for the next request
        """

        user_agent = self._get_current_user_agent()

        if self.ua_rotate and user_agent is not None:
            headers['User-Agent'] = user_agent

        if not bool(headers):
            headers = None

        return headers

    def _generate_proxies(self, proxies: Dict[str, Any] = {}):
        """
        Generate the proxies for the next request, considering the given list
        or the Tor configuration, if supplied.

        :param proxies: Dictionary of possible default values for the proxies

        :returns: The proxies to be used by the next request
        """
        if self.ip_rotate:
            if self.ip_rotation_type == 'tor':
                if self.ip_items_scraped >= self.ip_change_after:
                    logging.info('Changing Tor IP...')
                    self.ip_items_scraped = 0

                    new_ip = self.tor_controller.get_new_ip()
                    if not new_ip:
                        raise Exception('FatalError: Failed to find a new IP')

                    logging.info(f'New Tor IP: {new_ip}')

                proxies = {
                    'http': '127.0.0.1:8118',
                    'https': '127.0.0.1:8118'
                }

            elif self.ip_rotation_type == 'proxy':
                proxy_len = len(self.proxy_list)
                proxies = {
                    'http': self.proxy_list[self.ip_items_scraped % proxy_len],
                    'https': self.proxy_list[self.ip_items_scraped % proxy_len]
                }
            self.ip_items_scraped += 1

        return proxies if bool(proxies) else None

    def _generate_cookies(self, cookies: Dict[str, Any] = {}):
        """
        Generate the cookies for the next request.

        :param cookies: Dictionary of extra cookies to be included

        :returns: The cookies to be sent by the next request
        """
        if self.insert_cookies:
            for x in self.cookies:
                cookies = {**cookies, **x}

        return cookies if bool(cookies) else None

    def _send_request(self,
                     req_function: Callable,
                     *args, **kwargs) -> Any:
        """
        Apply all configured anti-blocking mechanisms and call the request
        function supplied.

        :param req_function: The function to be called to actually send the
                             request. It should take at least three named
                             arguments: headers, proxies and cookies, which
                             represent the respective values to be inserted.
                             Any extra values passed to this method are
                             redirected to the req_function.

        :returns: The response received from the supplied function
        """

        headers = self._generate_headers(kwargs.get('headers', {}))
        if 'headers' in kwargs:
            del kwargs['headers']

        proxies = self._generate_proxies(kwargs.get('proxies', {}))
        if 'proxies' in kwargs:
            del kwargs['proxies']

        cookies = self._generate_cookies(kwargs.get('cookies', {}))
        if 'cookies' in kwargs:
            del kwargs['cookies']

        self._apply_delay()

        response = req_function(headers=headers, proxies=proxies,
            cookies=cookies, *args, **kwargs)

        # Calculate next delay value
        self._generate_next_delay(response.elapsed.total_seconds(),
                                  response.status_code)

        self.time_last_request = time.perf_counter()

        return response
