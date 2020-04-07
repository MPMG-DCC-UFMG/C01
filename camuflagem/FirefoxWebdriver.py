import time
from selenium import webdriver
from CamouflageHandler import CamouflageHandler

class FirefoxWebdriver(CamouflageHandler, webdriver.Firefox):
    def __init__(self, profile: webdriver.FirefoxProfile = webdriver.FirefoxProfile(), user_agents: list=[], change_ip_after: int = 42, time_between_calls: int = 0, change_user_agent_after: int=-1):
        CamouflageHandler.__init__(self, user_agents=user_agents)

        self.number_of_requests_made = 0
        self.last_timestamp = 0
        
        self.change_ip_after = change_ip_after
        self.time_between_calls = time_between_calls
        
        # if negative, never change user-agent
        self.change_user_agent_after = change_user_agent_after

        # Configures the driver instance to use Tor as a proxy server
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", self.tor_host)
        profile.set_preference("network.proxy.socks_port", self.tor_port)
        # profile.set_preference("general.useragent.override", 'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36')
        profile.update_preferences()

        webdriver.Firefox.__init__(self, firefox_profile=profile)

        # Enables advanced Firefox preferences (to change IP without close)
        super().get('about:config')
        self.find_element_by_id('showWarningNextTime').click()
        self.find_element_by_id('warningButton').click()

    def renew_ip(self) -> None:
        """
        Change IP.
        """
        super().renew_ip()

        super().get('about:config')
        script = f"""
                var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
                prefs.setIntPref("network.proxy.type", 1);
                prefs.setCharPref("network.proxy.socks", "{self.tor_host}");
                prefs.setIntPref("network.proxy.socks_port", "{self.tor_port}");
                """
        self.execute_script(script)
        time.sleep(5)

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
                # FIXME: Time between requests is preventing IP changes
                time.sleep(self.time_between_calls - time_sleep)

        self.last_timestamp = int(time.time())
        super().get(url)
