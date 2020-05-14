import time 

from requests.sessions import Session
from requests import Response
from CamouflageHandler import CamouflageHandler

from typing import Union, Text

class TorRequestSession(CamouflageHandler, Session):
    def __init__(self, 
                # CamouflageHandler parameters
                tor_host: str = '127.0.0.1',
                tor_port: int = 9050,
                tor_password: str = '',
                tor_control_port: int = 9051,
                allow_reuse_ip_after: int = 5,
                # default user-agent is chrome 81.0 Linux
                user_agents: list = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'],
                time_between_calls: int = 0,
                random_time_between_calls: bool = False,
                min_time_between_calls: int = 0,
                max_time_between_calls: int = 10,
                # Paramters of this class 
                change_ip_after: int = 42,
                change_user_agent_after: int = -1):

        """ Starts a new session of TorRequestSession

        Keyword arguments:
            change_ip_after: Number of calls before changing the IP. (dafault 42).
            change_user_agent_after: Number of calls before changing the user-agent. If the number is negative, the user-agent never will be change (default -1)
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


        Session.__init__(self)

        # Configures the session to use Tor as a proxy server
        self.proxies = dict()
        self.proxies['http'] = f'socks5h://{tor_host}:{tor_port}'
        self.proxies['https'] = f'socks5h://{tor_host}:{tor_port}'

        self.number_of_requests_made = 0
        self.change_ip_after = change_ip_after
        
        # if negative, never change user-agent
        self.change_user_agent_after = change_user_agent_after

        self.current_user_agent = self.get_user_agent()  
        self.headers = {'User-Agent': self.current_user_agent}

    def get(self, url: Union[Text, bytes], **kwargs) -> Response:
        """Sends a GET request."""
        
        self.number_of_requests_made += 1

        if (self.change_user_agent_after > 0) and (self.number_of_requests_made % self.change_user_agent_after == 0):
            self.current_user_agent = self.get_user_agent()
            self.headers = {'User-Agent': self.current_user_agent}

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()
        
        else: 
            self.wait()

        self.last_timestamp = int(time.time())
        kwargs['headers'] = self.headers
        return super().get(url, **kwargs)

