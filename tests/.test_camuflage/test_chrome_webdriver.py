import os
import time
import unittest

from selenium import webdriver

from antiblock_selenium.chrome import Chrome


class TestChrome(unittest.TestCase):
    def test_change_ip(self):
        """Tests whether the IP changes after a number of calls"""

        # To avoid caching IPs
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-application-cache')

        driver = Chrome(options=options, change_ip_after=3)
        driver.renew_ip()

        used_ips = dict()
        for it in range(12):
            driver.get('http://icanhazip.com/')
            ip = driver.find_element_by_css_selector('body').text.replace('\n','')
            
            if ip not in used_ips:
                used_ips[ip] = 0
            
            used_ips[ip] += 1

            # To avoid caching IPs
            driver.delete_all_cookies()

        result = True
        for ip in used_ips:
            if used_ips[ip] != 3:
                result = False
                break
        
        driver.close()
        self.assertTrue(result)

    def test_minimum_time_fixed_between_calls(self):
        """Tests whether the minimum time between requests is respected"""
        
        driver = Chrome(time_between_calls=15, random_delay=False)
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

        driver = Chrome(time_between_calls=15, random_delay=True)
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

        cookie_file = 'test_chrome_cookies.pkl'

        driver = Chrome(persist_cookies_when_close=True, location_of_cookies=cookie_file)
        driver.get('https://www.google.com.br/')
        driver.close()

        self.assertTrue(os.path.exists(cookie_file))

    def test_persist_and_load_cookies(self):
        '''Tests whether cookies are persisted and loaded using sites that require login'''

        driver = Chrome(persist_cookies_when_close=True)
        driver.get('https://www.hackerrank.com/login')

        # Entering login data
        driver.find_element_by_xpath('//*[@id="input-1"]').send_keys("picece3768@tashjw.com")
        driver.find_element_by_xpath('//*[@id="input-2"]').send_keys("d/4SYk?fs,ACF6K")
        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/form/div[3]/div/label/div[1]/input').click()

        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/form/div[4]/button').click()

        time.sleep(60)
        driver.close()

        driver = Chrome(reload_cookies_when_start=True, cookie_domain='https://www.hackerrank.com/')
        driver.get('https://www.hackerrank.com/login')
        
        dashboard = driver.find_element_by_xpath('//*[@id="content"]/div/div/div/header/div/div/div[1]/div/h1').text.lower()
        driver.close()

        self.assertTrue(dashboard == 'dashboard')
