import random 
import time 

from os import system

class CamouflageHandler:
    def __init__(self, tor_host: str ='127.0.0.1', tor_port: int=9050, user_agents: list=[]):
        self.tor_host = tor_host
        self.tor_port = tor_port
        
        self.user_agents = user_agents

    def renew_ip(self) -> None:
        """
        Send signal to Tor to change IP
        """
        system('sudo service tor reload')

        # Time chosen arbitrarily/empirically. It is necessary to wait a while for the IP to be changed
        time.sleep(7.5) 

    def get_user_agent(self) -> str:
        """
        Returns a random user-agent.
        """
        return random.choice(self.user_agents) 
