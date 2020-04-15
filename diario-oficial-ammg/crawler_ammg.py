from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.select import Select

import datetime
import time
import json
from pandas import date_range

SCREEN_ON = True

def initChromeWebdriver     (
    path_to_driver: str = None,
    use_window: bool = False,
    ignore_console: bool = True
) -> WebDriver:
    """
    Returns a ready to use chrome driver.
    It will not display warning and errors that the site prints on the
    navigator console.

    Keyword arguments:
    path_to_driver -- path to the chrome driver executable. No need to
    pass if the driver is set in path.
    use_window -- if True, a instance of chrome will be opened
    and one could watch the execution of the program
    print_console -- if true, log information printed in the navigator
    console will be printed in the output
    """
    # If the chrome webdriver is added to path, leave path_to_driver blank
    # else, pass path to executable

    # Setting Chrome Browser
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--window-size=1420,1080')
    # chrome_options.add_argument("disable-popup-blocking");
    if ignore_console:
        # will only print fatal errors
        chrome_options.add_argument('log-level=3')

    if not use_window:
        # --no-sandbox: needed for chrome to start headless.
        # Its a security feature on chrome, see linkg
        #  https://www.google.com/googlebooks/chrome/med_26.html
        # So, be careful with the pages being opened.
        chrome_options.add_argument('--no-sandbox')
        # --headless: web browser without a graphical user interface.
        chrome_options.add_argument('--headless')
        #
        chrome_options.add_argument('--disable-gpu')

    if path_to_driver is None:
        # if driver is not configured to path, it will raise an excpetion
        # selenium.common.exceptions.WebDriverException: Message: ‘geckodriver’ executable needs to be in PATH
        driver =  webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
        return driver
    else:
        driver = webdriver.Chrome(path_to_driver, options=chrome_options)
        driver.set_page_load_timeout(60)
        return driver

def checkForUrlNova(driver):
    container = driver.find_element_by_id("containerDownloadNova")
    if container.value_of_css_property("display") == "block":
        print("link found Nova")
        
        return driver.find_element_by_id("btDownloadSimples2").get_attribute("href")
    return ""

def checkForUrlExtra(driver):
    container = driver.find_element_by_id("exibeExtra")
    if container.value_of_css_property("display") == "block":
        print("link found extra")
        
        return driver.find_element_by_id("btDownloadExtra").get_attribute("href")
    return ""
    

def checkForUrlOld(driver):
    container = driver.find_element_by_id("containerDownload")
    if container.value_of_css_property("display") == "block":
        print("link found old")
        
        return driver.find_element_by_id("btDownloadSimples").get_attribute("href")
    return ""

def crawler():
    driver = initChromeWebdriver(
        'chromedriver_win_79-0-3945-36.exe',
        # use_window=SCREEN_ON
    )

    target = "http://www.diariomunicipal.com.br/amm-mg/"
    driver.get(target)

    urls = []

    # for dt in date_range("2014-01-01", "2020-04-13"): 2019-03-17
    for dt in date_range("2019-01-29", "2020-04-13"):
        print("starting", dt.strftime('%Y-%m-%d'))

        Select(driver.find_element_by_id("calendar_year")).select_by_value(str(dt.year))
        time.sleep(1)
        Select(driver.find_element_by_id("calendar_month")).select_by_value(str(dt.month))
        time.sleep(1)
        Select(driver.find_element_by_id("calendar_day")).select_by_value(str(dt.day))
        time.sleep(1)

        driver.find_element_by_css_selector(".selected").click()
        time.sleep(2)

        anchor = checkForUrlOld(driver)
        if anchor != "":
            urls.append((dt.strftime('%Y-%m-%d'), "regular", anchor))
        else:
            anchor = checkForUrlNova(driver)
            if anchor != "":
                urls.append((dt.strftime('%Y-%m-%d'), "regular", anchor))
            
        anchor = checkForUrlExtra(driver)
        if anchor != "":
            urls.append((dt.strftime('%Y-%m-%d'), "extra", anchor))

        if len(urls) >= 100:
            print("writing backup, adding links:", len(urls))
            try:
                f = open("links_ammg.txt", "r")
                data = json.loads(f.read())
                f.close()
            except FileNotFoundError:
                data = []

            data = data + urls

            f = open("links_ammg.txt", "w+")
            f.write(json.dumps(data))
            f.close()

            urls = []

        time.sleep(1)
        driver.find_element_by_xpath("//*[@id=\"popup\"]/div/article/a").click()
    
    driver.close()

    f = open("links_ammg.txt", "w+")
    f.write(json.dumps(urls))
    f.close()

    print("done.")

crawler()

