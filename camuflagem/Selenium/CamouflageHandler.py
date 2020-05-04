import random 
import time 

from tor_controller import TorController

class CamouflageHandler:
    def __init__(self, 
                tor_host: str = '127.0.0.1',
                tor_port: int = 9050,
                tor_password: str = '',
                tor_control_port: int = 9051,
                allow_reuse_ip_after: int = 5,
                user_agents: list = [],
                time_between_calls: int = 0,
                random_time_between_calls: bool = False,
                min_time_between_calls: int = 0,
                max_time_between_calls: int = 10):
        """Creates a instance of CamouflageHandler.

        Keyword arguments:
            tor_host -- Address of Tor host (default '127.0.0.1')
            tor_port -- Port of Tor (default 9050)
            tor_password -- Tor access password (default '')
            tor_control_port -- Tor control port (default 9051)
            allow_reuse_ip_after -- When an IP is used, it can be used again only after this number (default 5)
            user_agents -- List of user-agents (default [])
            time_between_calls -- Fixed time between calls (default 0)
            random_time_between_calls -- Defines whether the time between calls is fixed or random (default False)
            min_time_between_calls -- If the time between calls is random, this will be the minimum time possible between calls (default 0)
            max_time_between_calls -- If the time between calls is random, this will be the maximum time possible between calls (default 10)
        """

        self.tor_ctrl = TorController(control_port=tor_control_port, password=tor_password, host=tor_host, port=tor_port, allow_reuse_ip_after=allow_reuse_ip_after) 
        self.user_agents = user_agents

        self.last_timestamp = 0
        self.time_between_calls = time_between_calls

        self.random_time_between_calls = random_time_between_calls
        self.min_time_between_calls = min_time_between_calls
        self.max_time_between_calls = max_time_between_calls

    def renew_ip(self) -> None:
        """
        Send signal to Tor to change IP
        """
        if not self.tor_ctrl.renew_ip():
            raise Exception('FatalError: Could not change IP')

    def get_user_agent(self) -> str:
        """
        Returns a random user-agent.
        """
        return random.choice(self.user_agents) 

    def wait(self) -> None:
        """
        Delays calls for a fixed or random time.
        """
        if self.random_time_between_calls:
            time_between_calls = random.randint(self.min_time_between_calls, self.max_time_between_calls)
        else:
            time_between_calls = self.time_between_calls

        time_sleep = int(time.time()) - self.last_timestamp
        if time_sleep < time_between_calls:
            time.sleep(time_between_calls - time_sleep)

