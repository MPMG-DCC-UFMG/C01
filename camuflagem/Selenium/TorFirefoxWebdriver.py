import random
import time

import bezier_curve

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

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
                    tor_password: str = '',
                    tor_control_port: int = 9051,
                    allow_reuse_ip_after: int = 5,
                    user_agents: list = [],
                    time_between_calls: int = 0,
                    random_time_between_calls: bool = False,
                    min_time_between_calls: int = 0,
                    max_time_between_calls: int = 10,
                    # Parameters of this class
                    change_ip_after: int = 42,
                    clear_cookies_after: int = 100,
                    change_user_agent_after: int = -1):

        """
        Starts a new session of TorFirefoxWebdriver.

        Keyword arguments:
            change_ip_after: Number of calls before changing the IP. (dafault 42)
            clear_cookies_after: Number of calls before clear the cookies. (default 100)
            change_user_agent_after: Number of calls before changing the user-agent. If the number is negative, the user-agent never will be changed (default -1)
        """
        CamouflageHandler.__init__(self, 
                                    tor_host,
                                    tor_port,
                                    tor_password,
                                    tor_control_port,
                                    allow_reuse_ip_after,
                                    user_agents,
                                    time_between_calls,
                                    random_time_between_calls,
                                    min_time_between_calls,
                                    max_time_between_calls)

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after
        self.clear_cookies_after = clear_cookies_after
        
        # if negative, never change user-agent
        self.change_user_agent_after = change_user_agent_after

        # Configures the driver instance to use Tor as a proxy server
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.socks", tor_host)
        firefox_profile.set_preference("network.proxy.socks_port", tor_port)
        firefox_profile.update_preferences()

        webdriver.Firefox.__init__(self, firefox_profile=firefox_profile)

        # Enables advanced Firefox preferences (to change user-agents)
        if change_user_agent_after > 0:
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

        if self.number_of_requests_made % self.clear_cookies_after == 0:
            self.delete_all_cookies()

        if (self.change_user_agent_after > 0) and (self.number_of_requests_made % self.change_user_agent_after == 0):
            self.renew_user_agent()

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()
        
        else: 
            self.wait()

        self.last_timestamp = int(time.time())
        super().get(url)
    
    def bezier_mouse_move(self, webelement_to_mouse_move = None, control_points: list = [], num_random_control_points: int = 7, plot: bool = True) -> None:
        '''Moves the mouse in the form of Bézier curves.
            
            Keywords arguments:
                webelement_to_mouse_move -- Webelement where the mouse will move (default html)
                control_points -- Control points for generating Bézier curves. If the list is empty, a random with num_random_control_points points will be generated.
                num_random_control_points -- Number of random control points to be generated, if control points are not defined. (default 7)
                plot -- If true, save the generated curve to a file. (default true) 
        '''
       
        if webelement_to_mouse_move is None:
            webelement_to_mouse_move = self.find_element_by_css_selector('html')
        
        # Generates random control points
        if len(control_points) < 2:
            we_size = webelement_to_mouse_move.size 
            
            width = we_size['width']
            height = we_size['height']
            
            for _ in range(num_random_control_points):
                x = random.randint(0, width)
                y = random.randint(0, height)

                control_points.append((x, y))

        bezier_points = bezier_curve.generate(control_points, intervals=25)

        action = ActionChains(self)

        x_offset = bezier_points[0][0]
        y_offset = bezier_points[0][1]

        action.move_to_element_with_offset(webelement_to_mouse_move, x_offset, y_offset)
        # action.click_and_hold()

        last_point = [x_offset, y_offset]
        for point in bezier_points[1:]:
            x_offset = point[0] - last_point[0]
            y_offset = point[1] - last_point[1]
            
            action.move_by_offset(x_offset, y_offset)

            last_point[0] = point[0]
            last_point[1] = point[1]

        # action.release()
        action.perform()

        if plot:
            bezier_curve.plot(bezier_points)