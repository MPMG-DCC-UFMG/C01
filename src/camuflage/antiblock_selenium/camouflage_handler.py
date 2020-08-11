import time 
import random

from itertools import cycle
from antiblock_selenium.tor_controller import TorController

def frange(start: float, end: float, step: float = .01):
    """Customized range version for floats to two decimal places"""

    values = list()

    counter = start
    while counter <= end:
        values.append(round(counter, 2))
        counter += step 
    
    values.append(round(counter, 2))

    return values 

class EmptyUserAgentListError(Exception):
    pass

class CookieDomainError(Exception):
    pass

class CamouflageHandler:
    def __init__(self, user_agents: list = [], allow_reuse_ip_after: int = 10, time_between_calls: float = 0.25, random_delay: bool = True):
        """Creates a instance of CamouflageHandler.

        Keyword arguments:
            user_agents -- List of user-agents (default [])
            allow_reuse_ip_after -- When an IP is used, it can be used again only after this number (default 10)
            time_between_calls -- Delay in seconds between requests. Supports only up to 2 decimal places. (default 0.25)
            random_delay -- If the delay between requests is fixed or random, between 0.5 * time_between_calls * 1.5 (default True)
        """

        self.tor_controller = TorController(allow_reuse_ip_after=allow_reuse_ip_after)
        self.user_agents = cycle(user_agents)

        self.last_call_timestamp = 0

        if random_delay:
            self.delays = frange(.5 * time_between_calls, 1.5 * time_between_calls) 

        else:
            self.delays = [round(time_between_calls, 2)]

    def renew_ip(self) -> None:
        """Send signal to Tor to change IP"""

        if not self.tor_controller.renew_ip():
            raise Exception('FatalError: Could not change IP')
        
    def get_user_agent(self) -> str:
        """Returns a user-agent."""
        return next(self.user_agents)

    def wait(self) -> None:
        """Delays calls for a fixed or random time."""

        time_between_calls = random.choice(self.delays)
        time_elapsed_between_last_call = round(time.time(), 2) - self.last_call_timestamp

        if time_elapsed_between_last_call < time_between_calls:
            time.sleep(round(time_between_calls - time_elapsed_between_last_call, 2))
