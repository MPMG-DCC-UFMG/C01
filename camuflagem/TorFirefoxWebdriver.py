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
                    # end of parameters of webdriver.Firefox
                    user_agents: list = [],
                    change_ip_after: int = 42,
                    time_between_calls: int = 10,
                    change_user_agent_after: int = -1):

        """
        Starts a new session of TorFirefoxWebdriver.
        """
        CamouflageHandler.__init__(self, user_agents=user_agents)

        self.number_of_requests_made = 0
        self.last_timestamp = 0
        
        self.change_ip_after = change_ip_after
        self.time_between_calls = time_between_calls
        
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
            # Ensures that time between requests is respected
            time_sleep = int(time.time()) - self.last_timestamp
            if time_sleep <= self.time_between_calls:
                time.sleep(self.time_between_calls - time_sleep)

        self.last_timestamp = int(time.time())
        super().get(url)
