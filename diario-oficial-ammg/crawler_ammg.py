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

def checkForUrl(driver, prev, dtype, container_id, btn_id):
    container = driver.find_element_by_id(container_id)
    css = container.value_of_css_property("display")
    if css == "block":
        print("link found", dtype)
        
        # must check display and if url changed, because it was repeating urls
        anchor = driver.find_element_by_id(btn_id).get_attribute("href")
        if anchor == prev:
            print("but repeated...")
            time.sleep(1)
            anchor = driver.find_element_by_id(btn_id).get_attribute("href")
            if anchor == prev:
                print("still repeated, giving up")
                return ""
            else:
                print("new url found, returning...")
                return anchor
        else:
            return anchor
    return ""

def checkForUrlNova(driver, prev):
    return checkForUrl(driver, prev, "Nova", "containerDownloadNova", "btDownloadSimples2")

def checkForUrlExtra(driver, prev):
    return checkForUrl(driver, prev, "extra", "exibeExtra", "btDownloadExtra")

def checkForUrlOld(driver, prev):
    return checkForUrl(driver, prev, "Old", "containerDownload", "btDownloadSimples")

def addProgress(urls):
    print(f"Saving progress, adding {len(urls)} links")
    try:
        f = open("links_ammg.json", "r")
        data = json.loads(f.read())
        f.close()
    except FileNotFoundError:
        data = []

    data = data + urls

    f = open("links_ammg.json", "w+")
    f.write(json.dumps(data, indent=1))
    f.close()

def lastFetchedDate():
    try:
        f = open("links_ammg.json", "r")
        data = json.loads(f.read())
        f.close()
        return data[-1]["date"]
    except FileNotFoundError:
        return "2014-01-01"

def crawler():
    driver = initChromeWebdriver(
        # 'chromedriver_win_79-0-3945-36.exe',
        # use_window=SCREEN_ON
    )

    target = "http://www.diariomunicipal.com.br/amm-mg/"
    driver.get(target)

    urls = []

    prev_old_url = ""
    prev_new_url = ""
    prev_extra_url = ""

    for dt in date_range(lastFetchedDate(), datetime.datetime.now().strftime('%Y-%m-%d')):
        print(f"starting {dt.strftime('%Y-%m-%d')} at {datetime.datetime.now()}")

        Select(driver.find_element_by_id("calendar_year")).select_by_value(str(dt.year))
        time.sleep(1)
        Select(driver.find_element_by_id("calendar_month")).select_by_value(str(dt.month))
        time.sleep(1)
        Select(driver.find_element_by_id("calendar_day")).select_by_value(str(dt.day))
        time.sleep(1)

        driver.find_element_by_css_selector(".selected").click()
        time.sleep(5)

        anchor = checkForUrlOld(driver, prev_old_url)
        if anchor != "":
            urls.append({"date": dt.strftime('%Y-%m-%d'), "type": "regular", "url": anchor})
            prev_old_url = anchor
        else:
            anchor = checkForUrlNova(driver, prev_new_url)
            if anchor != "":
                urls.append({"date": dt.strftime('%Y-%m-%d'), "type": "regular", "url": anchor})
                prev_new_url = anchor
            
        anchor = checkForUrlExtra(driver, prev_extra_url)
        if anchor != "":
            urls.append({"date": dt.strftime('%Y-%m-%d'), "type": "extra", "url": anchor})
            prev_extra_url = anchor

        if len(urls) >= 100:
            addProgress(urls)
            urls = []

        time.sleep(1)
        driver.find_element_by_xpath("//*[@id=\"popup\"]/div/article/a").click()
        time.sleep(1)
    
    driver.close()
    addProgress(urls)
    print("Done.")

crawler()

