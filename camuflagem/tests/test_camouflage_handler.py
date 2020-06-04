import unittest
import time 
from antiblock_selenium.camouflage_handler import CamouflageHandler

USER_AGENTS = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
    'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
]

TIME_BETWEEN_CALLS = 2.5

class TestCamouflageHandler(unittest.TestCase):
    def test_get_user_agent(self):
        camouflage_handler = CamouflageHandler(user_agents=USER_AGENTS)
        user_agent = camouflage_handler.get_user_agent()
        self.assertIn(user_agent,USER_AGENTS)

    def test_fixed_time_between_calls(self):
        camouflage_handler = CamouflageHandler(time_between_calls=TIME_BETWEEN_CALLS, random_delay=False)

        camouflage_handler.last_call_timestamp = start = time.time()
        camouflage_handler.wait()

        time_elapsed = round(time.time() - start, 2)

        self.assertAlmostEqual(TIME_BETWEEN_CALLS, time_elapsed)

    def test_random_time_between_calls(self):
        camouflage_handler = CamouflageHandler(time_between_calls=TIME_BETWEEN_CALLS, random_delay=True)

        camouflage_handler.last_call_timestamp = start = round(time.time(), 2) # because the time is in 2 decimal places
        camouflage_handler.wait()
        time_elapsed = round(time.time(), 2) - start

        self.assertTrue(round(0.5 * TIME_BETWEEN_CALLS, 2) <= time_elapsed <= round(TIME_BETWEEN_CALLS * 1.5, 2))

if __name__ == "__main__":
    unittest.main()