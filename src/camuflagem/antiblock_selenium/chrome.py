import time 
import os 
import pickle

from selenium import webdriver
from antiblock_selenium.camouflage_handler import CamouflageHandler, CookieDomainError

class Chrome(CamouflageHandler, webdriver.Chrome):
    def __init__(self,
                    # Chromedriver parameters
                    executable_path='chromedriver',
                    port=0, 
                    options=webdriver.ChromeOptions(),
                    service_args=None,
                    desired_capabilities=None,
                    service_log_path=None,
                    chrome_options=None,
                    keep_alive=True,
                    # CamouflageHandler parameters
                    allow_reuse_ip_after: int = 10,
                    time_between_calls: float = 0.25,
                    random_delay: bool = True,
                    # Parameters of this class
                    change_ip_after: int = 42,
                    cookie_domain: str = '',
                    persist_cookies_when_close: bool = False,
                    reload_cookies_when_start: bool = False,
                    location_of_cookies: str = 'cookies.pkl'):

        """Starts a new session of TorFirefoxWebdriver.

        Keyword arguments:
            change_ip_after -- Number of calls before changing the IP. (default 42)
            cookie_domain -- Domain of the cookie, eg., https://example.com/ (default '')
            persist_cookies_when_close -- Whether to save cookies when closing the driver (default False) 
            reload_cookies_when_start -- Whether to reload the cookies that were saved when closing the last driver session (default False)
            location_of_cookies -- Where to save cookies (default 'cookies.pkl')
        """

        CamouflageHandler.__init__(self,
                            allow_reuse_ip_after=allow_reuse_ip_after,
                            time_between_calls=time_between_calls,
                            random_delay=random_delay)

        options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
        webdriver.Chrome.__init__(self, 
                                    executable_path = executable_path,
                                    port = port,
                                    options = options, 
                                    service_args = service_args,
                                    desired_capabilities = desired_capabilities,
                                    service_log_path = service_log_path,
                                    chrome_options = chrome_options,
                                    keep_alive = keep_alive)

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after

        self.cookie_domain = cookie_domain
        self.persist_cookies_when_close = persist_cookies_when_close
        self.location_of_cookies = location_of_cookies

        if reload_cookies_when_start:
            if not self.cookie_domain:
                raise CookieDomainError('To reload cookies, you need to specify their domain')

            self.reload_cookies()

    def get(self, url: str) -> None:
        """Loads a web page in the current browser session.

            Keywords arguments:
                url -- URL of the website to be accessed
        """

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()

        else:
            self.wait()

        self.last_call_timestamp = round(time.time(), 2)
        super().get(url)

        self.number_of_requests_made += 1

    def save_cookies(self): 
        """Save session cookies to location_of_cookies"""

        with open(self.location_of_cookies, 'wb') as f:
            pickle.dump(self.get_cookies(), f)
            f.close()

    def load_cookies(self, cookies: list, cookie_domain: str):
        """Load cookies in the current session to domain location_domain

            Keyword arguments:
                cookies -- List of cookies to load 
                cookie_domain -- Domain of the cookie, eg., https://example.com/
        """
        if not cookie_domain:
            raise CookieDomainError('To reload cookies, you need to specify their domain')

        self.delete_all_cookies()

        super().get(cookie_domain)
        for cookie in cookies:
            self.add_cookie(cookie)

    def reload_cookies(self):
        """Reloads cookies from the last session, if they have been saved"""

        if os.path.exists(self.location_of_cookies):
            with open(self.location_of_cookies, 'rb') as f:
                cookies = pickle.load(f)
                self.load_cookies(cookies, self.cookie_domain)
                
                f.close()

    def close(self):
        """Closes the current window."""
        if self.persist_cookies_when_close:
            self.save_cookies()

        super().close()

    def quit(self):
        """Closes the browser and shuts down the ChromeDriver executable that is started when starting the ChromeDriver"""
        if self.persist_cookies_when_close:
            self.save_cookies()

        super().quit()

            