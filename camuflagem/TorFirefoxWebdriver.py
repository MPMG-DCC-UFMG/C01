import time
from selenium import webdriver
from CamouflageHandler import CamouflageHandler

class TorFirefoxWebdriver(CamouflageHandler, webdriver.Firefox):
    def __init__(self, 
                    # webdriver.Firefox parameters start here
                    firefox_profile: webdriver.FirefoxProfile = webdriver.FirefoxProfile(), 
                    firefox_binary=None, 
                    timeout=30,
                    capabilities=None,
                    proxy=None,
                    executable_path="geckodriver",
                    options=None,
                    service_log_path="geckodriver.log",
                    firefox_options=None,
                    service_args=None,
                    desired_capabilities=None,
                    log_path=None, 
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
                    change_user_agent_after: int = -1):

        """
        Starts a new session of TorFirefoxWebdriver.

        Keyword arguments:
            change_ip_after: Number of calls before changing the IP. (dafault 42).
            change_user_agent_after: Number of calls before changing the user-agent. If the number of calls is negative, the user-agent never will change (default -1)
        """
        CamouflageHandler.__init__(self, 
                                    tor_host, 
                                    tor_port, 
                                    user_agents,
                                    time_between_calls,
                                    random_time_between_calls,
                                    min_time_between_calls,
                                    max_time_between_calls)

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after
        
        # if negative, never change user-agent
        self.change_user_agent_after = change_user_agent_after

        # Configures the driver instance to use Tor as a proxy server
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.socks", self.tor_host)
        firefox_profile.set_preference("network.proxy.socks_port", self.tor_port)
        firefox_profile.update_preferences()

        webdriver.Firefox.__init__(self, firefox_profile=firefox_profile)

        # Enables advanced Firefox preferences (to change user-agents)
        super().get('about:config')
        self.find_element_by_id('showWarningNextTime').click()
        self.find_element_by_id('warningButton').click()

    def renew_user_agent(self) -> None:
        """
        Change user-agent.
        """
        ua = self.get_user_agent()

        super().get('about:config')
        script = f"""
                    var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
                    prefs.setCharPref("general.useragent.override", "{ua}");
                    """
        self.execute_script(script)

    def get(self, url: str) -> None:
        """
        Loads a web page in the current browser session.
        """
        self.number_of_requests_made += 1

        if (self.change_user_agent_after > 0) and (self.number_of_requests_made % self.change_user_agent_after == 0):
            self.renew_user_agent()

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()
        
        else: 
            self.wait()

        self.last_timestamp = int(time.time())
        super().get(url)

# if __name__ == "__main__":
#     driver = TorFirefoxWebdriver(change_ip_after=5)

#     for _ in range(100):
#         driver.get('https://check.torproject.org/')
#         ip = driver.find_element_by_css_selector('body > div.content > p:nth-child(3) > strong').text
#         print(ip)
