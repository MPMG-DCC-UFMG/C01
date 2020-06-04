import os
import pickle
import random
import time

from selenium import webdriver

from antiblock_selenium.camouflage_handler import (CamouflageHandler,
                                             EmptyUserAgentListError, 
                                             CookieDomainError)

class Firefox(CamouflageHandler, webdriver.Firefox):
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
                    user_agents: list = [],
                    allow_reuse_ip_after: int = 10,
                    time_between_calls: float = 0.25,
                    random_delay: bool = True,
                    # Parameters of this class
                    change_ip_after: int = 42,
                    change_user_agent_after: int = 0,
                    cookie_domain: str = '',
                    persist_cookies_when_close: bool = False,
                    reload_cookies_when_start: bool = False,
                    location_of_cookies: str = 'cookies.pkl'):

        """Starts a new session of TorFirefoxWebdriver.

        Keyword arguments:
            change_ip_after -- Number of calls before changing the IP. (default 42)
            change_user_agent_after -- Number of calls before changing the user-agent. If the number is zero, the user-agent never will be changed (default 0)
            cookie_domain -- Domain of the cookie, eg., https://example.com/ (default '')
            persist_cookies_when_close -- Whether to save cookies when closing the driver (default False) 
            reload_cookies_when_start -- Whether to reload the cookies that were saved when closing the last driver session (default False)
            location_of_cookies -- Where to save cookies (default 'cookies.pkl')
        """

        CamouflageHandler.__init__(self,
                                    user_agents=user_agents, 
                                    allow_reuse_ip_after=allow_reuse_ip_after,
                                    time_between_calls=time_between_calls,
                                    random_delay=random_delay)

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after
        
        self.change_user_agent_after = change_user_agent_after

        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.socks", '127.0.0.1')
        firefox_profile.set_preference("network.proxy.socks_port", 9050)
        firefox_profile.update_preferences()

        webdriver.Firefox.__init__(self, 
                                    firefox_profile=firefox_profile,
                                    firefox_binary=firefox_binary, 
                                    timeout=timeout,
                                    capabilities=capabilities,
                                    proxy=proxy,
                                    executable_path=executable_path,
                                    options=options,
                                    service_log_path=service_log_path,
                                    firefox_options=firefox_options,
                                    service_args=service_args,
                                    desired_capabilities=desired_capabilities,
                                    log_path=log_path, 
                                    keep_alive=keep_alive)

        # Enables advanced Firefox preferences (to change user-agents)
        if change_user_agent_after > 0:
            if len(user_agents) > 0:    
                super().get('about:config')
                self.find_element_by_id('showWarningNextTime').click()
                self.find_element_by_id('warningButton').click()
            
            else:
                raise EmptyUserAgentListError('You are trying to rotate user-agent with an empty list of user-agents.')
        
        self.cookie_domain = cookie_domain
        self.persist_cookies_when_close = persist_cookies_when_close
        self.location_of_cookies = location_of_cookies

        if reload_cookies_when_start:
            if not self.cookie_domain:
                raise CookieDomainError('To reload cookies, you need to specify their domain')

            self.reload_cookies()

    def renew_user_agent(self) -> None:
        """Change user-agent."""

        ua = self.get_user_agent()

        super().get('about:config')
        script = f"""
                    var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
                    prefs.setCharPref("general.useragent.override", "{ua}");
                    """
        self.execute_script(script)
    
    def get(self, url: str) -> None:
        """Loads a web page in the current browser session.

            Keyword arguments:
                url -- URL of the website to be accessed
        """

        if (self.change_user_agent_after > 0) and (self.number_of_requests_made % self.change_user_agent_after == 0):
            self.renew_user_agent()

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
        """Quits the driver and close every associated window."""
        if self.persist_cookies_when_close:
            self.save_cookies()
        
        super().quit()