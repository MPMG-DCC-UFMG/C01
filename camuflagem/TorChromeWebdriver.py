import time

from selenium import webdriver
from CamouflageHandler import CamouflageHandler

class TorChromeWebdriver(CamouflageHandler, webdriver.Chrome):
    def __init__(self, 
                executable_path='chromedriver',
                port=0, 
                options=None,
                service_args=None,
                desired_capabilities=None,
                service_log_path=None,
                chrome_options=webdriver.ChromeOptions(),
                keep_alive=True,
                user_agents: list = [],
                change_ip_after: int = 42,
                time_between_calls: int = 10,
                change_user_agent_after: int = -1):

        CamouflageHandler.__init__(self, user_agents=user_agents)

        chrome_options.add_argument(f'--proxy-server=socks5://{self.tor_host}:{self.tor_port}')
        webdriver.Chrome.__init__(self, executable_path=executable_path, port=port, options=options, service_args=service_args, desired_capabilities=desired_capabilities, service_log_path=service_log_path, chrome_options=chrome_options, keep_alive=keep_alive)

        self.change_ip_after = change_ip_after
        self.time_between_calls = time_between_calls
        self.change_user_agent_after = change_user_agent_after

        self.number_of_requests_made = 0
        self.last_timestamp = 0
    
    def get(self, url: str) -> None:
        """
        Loads a web page in the current browser session.
        """
        self.number_of_requests_made += 1

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()

        else:
            # Ensures that time between requests is respected
            time_sleep = int(time.time()) - self.last_timestamp
            if time_sleep <= self.time_between_calls:
                time.sleep(self.time_between_calls - time_sleep)

        self.last_timestamp = int(time.time())
        super().get(url)

# if __name__ == "__main__":
#     cw = TorChromeWebdriver('../../venv/bin/chromedriver', change_ip_after=5)

#     for _ in range(100):
#         cw.get('https://check.torproject.org/')
#         ip = cw.find_element_by_css_selector('body > div.content > p:nth-child(3) > strong').text
#         print(ip)
