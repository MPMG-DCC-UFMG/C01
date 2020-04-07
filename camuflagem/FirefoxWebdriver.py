import time
from selenium import webdriver
from CamouflageHandler import CamouflageHandler

class FirefoxWebdriver(CamouflageHandler, webdriver.Firefox):
    def __init__(self, profile: webdriver.FirefoxProfile = webdriver.FirefoxProfile(), change_ip_after: int = 42, time_between_calls: int = 0):
        CamouflageHandler.__init__(self)

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after

        self.time_between_calls = time_between_calls
        self.last_timestamp = 0

        # Configures the driver instance to use Tor as a proxy server
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", self.tor_host)
        profile.set_preference("network.proxy.socks_port", self.tor_port)
        profile.update_preferences()

        webdriver.Firefox.__init__(self, firefox_profile=profile)

        # Enables advanced Firefox preferences (to change IP without close)
        super().get('about:config')
        self.find_element_by_id('showWarningNextTime').click()
        self.find_element_by_id('warningButton').click()

    def renew_ip(self):
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

    def get(self, url: str) -> None:
        """
        Loads a web page in the current browser session.
        """
        if self.number_of_requests_made < self.change_ip_after:
            # Ensures that time between requests is respected
            time_sleep = int(time.time()) - self.last_timestamp
            if time_sleep <= self.time_between_calls:
                # FIXME: Time between requests is preventing IP changes
                time.sleep(self.time_between_calls - time_sleep)
            self.number_of_requests_made += 1

        else: 
            self.renew_ip()
            self.number_of_requests_made = 1

        self.last_timestamp = int(time.time())
        super().get(url)

# Only for tests
if __name__ == "__main__":
    driver = FirefoxWebdriver(change_ip_after=5)
    for _ in range(100):
        driver.get('https://api.ipify.org/')
        print(driver.find_element_by_css_selector('pre').text)
