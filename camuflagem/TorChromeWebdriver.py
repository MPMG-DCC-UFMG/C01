import time

from selenium import webdriver
from CamouflageHandler import CamouflageHandler

class TorChromeWebdriver(CamouflageHandler, webdriver.Chrome):
    def __init__(self, 
                # Chromedriver parameters
                executable_path='chromedriver',
                port=0, 
                options=None,
                service_args=None,
                desired_capabilities=None,
                service_log_path=None,
                chrome_options=webdriver.ChromeOptions(),
                keep_alive=True,
                # CamouflageHandler parameters
                tor_host: str = '127.0.0.1',
                tor_port: int = 9050,
                user_agents: list = [],
                time_between_calls: int = 0,
                random_time_between_calls: bool = False,
                min_time_between_calls: int = 0,
                max_time_between_calls: int = 10,
                # Parameters of this class
                change_ip_after: int = 42,
                clear_cookies_after: int = 100):
        """
        Creates a new instance of this class.

        Keyword arguments:
            change_ip_after -- Number of calls before changing the IP. (dafault 42)
            clear_cookies_after -- Number of calls before clear the cookies. (default 100)
        """

        CamouflageHandler.__init__(self,
                                   tor_host,
                                   tor_port,
                                   user_agents,
                                   time_between_calls,
                                   random_time_between_calls,
                                   min_time_between_calls,
                                   max_time_between_calls)

        chrome_options.add_argument(f'--proxy-server=socks5://{self.tor_host}:{self.tor_port}')
        webdriver.Chrome.__init__(self, 
                                    executable_path,
                                    port,
                                    options, 
                                    service_args,
                                    desired_capabilities,
                                    service_log_path,
                                    chrome_options,
                                    keep_alive)

        self.change_ip_after = change_ip_after
        self.clear_cookies_after = clear_cookies_after

        self.number_of_requests_made = 0
    
    def get(self, url: str) -> None:
        """
        Loads a web page in the current browser session.
        """
        self.number_of_requests_made += 1

        if self.number_of_requests_made % self.clear_cookies_after == 0:
            self.delete_all_cookies()

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()

        else:
            self.wait()

        self.last_timestamp = int(time.time())
        super().get(url)

if __name__ == "__main__":
    cw = TorChromeWebdriver('../../venv/bin/chromedriver', clear_cookies_after=2)

    for _ in range(100):
        cw.get('https://check.torproject.org/')
        ip = cw.find_element_by_css_selector('body > div.content > p:nth-child(3) > strong').text
        print(ip)
