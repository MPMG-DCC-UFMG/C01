import os
import time
import unittest

from selenium import webdriver

from antiblock_selenium.firefox import Firefox

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

class TestFirefox(unittest.TestCase):
    def test_change_ip(self):
        """Tests whether the IP changes after a number of calls"""
        
        # To avoid caching IPs
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False) 

        driver = Firefox(firefox_profile=profile , change_ip_after=2)
        driver.renew_ip()

        used_ips = dict()
        for it in range(10):
            driver.get('http://icanhazip.com/')
            ip = driver.find_element_by_css_selector('body').text.replace('\n','')
            
            if ip not in used_ips:
                used_ips[ip] = 0
            
            used_ips[ip] += 1

            # To avoid caching IPs
            driver.delete_all_cookies()

        result = True
        for ip in used_ips:
            if used_ips[ip] != 2:
                result = False
                break
        
        driver.close()

        self.assertTrue(result)

    def test_rotate_user_agent(self):
        """Tests whether the user-agent changes after a number of calls"""
        driver = Firefox(user_agents=USER_AGENTS, change_user_agent_after=2)

        used_user_agents = dict()
        for _ in range(10):
            driver.get('http://whatsmyuseragent.org/')
            user_agent = driver.find_element_by_css_selector('.user-agent').text

            if user_agent not in used_user_agents:
                used_user_agents[user_agent] = 0
            
            used_user_agents[user_agent] += 1

        result = True
        for user_agent in used_user_agents:
            if used_user_agents[user_agent] != 2:
                result = False
                break
        
        driver.close()

        self.assertTrue(result)

    def test_minimum_time_fixed_between_calls(self):
        """Tests whether the minimum time between requests is respected"""
        
        driver = Firefox(time_between_calls=15, random_delay=False)
        driver.get('http://icanhazip.com/') #because there is no minimum time for the first call

        time_elapsed = .0
        for _ in range(5):
            start = driver.last_call_timestamp
            driver.get('http://icanhazip.com/') #Because this site is light and fast to load
            end = round(time.time(), 2)

            time_elapsed += round(time.time() - start, 2)

        driver.close()
        average = time_elapsed / 5

        self.assertTrue(average >= 15.0)

    def test_minimum_time_random_between_calls(self):
        """Tests whether the minimum random time between requests is respected"""

        driver = Firefox(time_between_calls=15, random_delay=True)
        driver.get('http://icanhazip.com/')

        time_elapsed = .0
        for _ in range(5):
            start = driver.last_call_timestamp
            driver.get('http://icanhazip.com/') #Because this site is light and fast to load
            end = round(time.time(), 2)

            time_elapsed += round(time.time() - start, 2)

        driver.close()
        average = time_elapsed / 5

        self.assertTrue(average >= 15.0 * 0.5)

    def test_save_cookies_when_close(self):
        '''Tests whether cookies are saved when closing the session'''

        cookie_file = 'test_ff_cookies.pkl'

        driver = Firefox(persist_cookies_when_close=True, location_of_cookies=cookie_file)
        driver.get('https://www.google.com.br/')
        driver.close()

        self.assertTrue(os.path.exists(cookie_file))

    def test_persist_and_load_cookies(self):
        '''Tests whether cookies are persisted and loaded using sites that require login'''

        driver = Firefox(persist_cookies_when_close=True)
        driver.get('https://www.hackerrank.com/login')

        # Entering login data
        driver.find_element_by_xpath('//*[@id="input-1"]').send_keys("picece3768@tashjw.com")
        driver.find_element_by_xpath('//*[@id="input-2"]').send_keys("d/4SYk?fs,ACF6K")
        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/form/div[3]/div/label/div[1]/input').click()

        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/form/div[4]/button').click()

        time.sleep(60)
        driver.close()

        driver = Firefox(reload_cookies_when_start=True, cookie_domain='https://www.hackerrank.com/')
        driver.get('https://www.hackerrank.com/login')
        
        dashboard = driver.find_element_by_xpath('//*[@id="content"]/div/div/div/header/div/div/div[1]/div/h1').text.lower()
        driver.close()

        self.assertTrue(dashboard == 'dashboard')
