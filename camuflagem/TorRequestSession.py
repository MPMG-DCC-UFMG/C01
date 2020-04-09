import time 

from requests.sessions import Session
from requests import Response
from CamouflageHandler import CamouflageHandler

from typing import Union, Text

class TorRequestSession(CamouflageHandler, Session):
    def __init__(self, 
                # default user-agent is chrome 81.0 Linux
                user_agents: list = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'],
                change_ip_after: int = 42,
                time_between_calls: int = 10,
                change_user_agent_after: int = -1):
        """
        Starts a new session of TorRequestSession
        """
        CamouflageHandler.__init__(self, user_agents=user_agents)
        Session.__init__(self)

        # Configures the session to use Tor as a proxy server
        self.proxies = dict()
        self.proxies['http'] = f'socks5h://{self.tor_host}:{self.tor_port}'
        self.proxies['https'] = f'socks5h://{self.tor_host}:{self.tor_port}'

        self.change_ip_after = change_ip_after
        self.time_between_calls = time_between_calls
        self.change_user_agent_after = change_user_agent_after
        
        self.number_of_requests_made = 0
        self.last_timestamp = 0

        self.current_user_agent = self.get_user_agent()  
        self.headers = {'User-Agent': self.current_user_agent}

    def get(self, url: Union[Text, bytes], **kwargs) -> Response:
        self.number_of_requests_made += 1

        if (self.change_user_agent_after > 0) and (self.number_of_requests_made % self.change_user_agent_after == 0):
            self.current_user_agent = self.get_user_agent()
            self.headers = {'User-Agent': self.current_user_agent}

        if self.number_of_requests_made % self.change_ip_after == 0:
            self.renew_ip()
        
        else: 
            # Ensures that time between requests is respected
            time_sleep = int(time.time()) - self.last_timestamp
            if time_sleep <= self.time_between_calls:
                time.sleep(self.time_between_calls - time_sleep)

        self.last_timestamp = int(time.time())
        kwargs['headers'] = self.headers
        return super().get(url, **kwargs)

# if __name__ == "__main__":
#     session = TorRequestSession(change_ip_after=2, time_between_calls=10)
#     for _ in range(10):
#         text = session.get('https://check.torproject.org/').text
#         print(text.split('<strong>')[-1].split('</strong>')[0])

