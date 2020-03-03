from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException 
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException

from shutil import copyfile

from PyPDF2.utils import PdfReadError
from PyPDF2 import PdfFileReader

import requests
import json
import datetime
import locale
import time
import os
import PyPDF2
from tika import parser

SCREEN_ON = False

class LimitOfAttemptsReached(Exception):
    pass

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

def getLastNewspaperDate(driver: WebDriver) -> datetime.date:
    """Finds the date of the last newspaper published."""    
    last_newspaper = driver.find_element_by_xpath(
        "//div[@id='links-constantes-direita']/fieldset/table/tbody/tr/td/a"
    )
    last_newspaper_date = last_newspaper.get_attribute("text") 
    # now its like "Jornal de 01/02/2020"
    last_newspaper_date = last_newspaper_date.split(" ")[-1] 
    # now its like "01/02/2020"
    last_newspaper_date = last_newspaper_date.split("/") 
    # now its like ["01", "02", "2020"]
    last_newspaper_date = datetime.date(
        int(last_newspaper_date[2]),
        int(last_newspaper_date[1]),
        int(last_newspaper_date[0])
    )
    
    return last_newspaper_date

def getYear(driver: WebDriver, date: datetime.date) -> WebElement:
    """Finds the anchor for the year of <date>, if it exists."""
    yearly_navigation = driver.find_element_by_xpath(
        "//div[@id='links-constantes-direita']/fieldset/table/tbody"
    )
    anchors = yearly_navigation.find_elements_by_tag_name("a")
    
    print("Trying to find year...")

    for a in anchors:
        if a.get_attribute("text") == str(date.year):
            return a
    
    return None

def getMonth(driver: WebDriver, date: datetime.date) -> WebElement:
    """Finds the anchor for the month of <date>, if it exists."""
    month_table = driver.find_element_by_id("id-lista-subcomunidades")
    month_links = month_table.find_elements_by_tag_name("td")

    print("Trying to find month...")

    target_month = month_links[date.month - 1]
    try:
        return target_month.find_element_by_tag_name("a")
    except NoSuchElementException:
        return None    

def getDay(driver: WebDriver, date: datetime.date) -> WebElement:
    """Finds the anchor for the day of <date>, if it exists."""
    # will explore the column of the corresponding weekday to find the date
    print("Trying to find day...")

    column = date.weekday() + 1 # weekday() -> 0 == monday, 6 == sunday
    if column == 7: # if sunday
        column = 0

    calendar_table = driver.find_element_by_id("id-lista-subcomunidades")
    trs = calendar_table.find_elements_by_tag_name("tr")
    trs = trs[2:] # ignores lines with month name and week day

    target_day_td = None

    for tr in trs:
        tds = tr.find_elements_by_tag_name("td")

        text = tds[column].text
        if  text != "-" and int(text) == date.day:
            target_day_td = tds[column]

    if target_day_td is None:
        return None

    try:
        return target_day_td.find_element_by_tag_name("a")
    except NoSuchElementException:
        return None

def waitNavigationToLoad(driver: WebDriver, action_type: str):
    """
    Waits for a element to load, then returns it.
    For 128 attempts it will ignore NoSuchElementException and 
    StaleElementReferenceException if they occur while trying to get the
    element.

    type -- should be in ['month', 'day', 'news'].
    Waits for main navigation div to load.
    """
    if action_type == 'month':
        target_size = [12]
    elif action_type == 'day':
        target_size = [6, 7, 8]
    elif action_type == 'news':
        pass
    else:
        print("Wrong value for type")
        exit()

    time.sleep(2)

    attempt = 1

    while 1:
        try:
            nvg_table = driver.find_element_by_id("id-lista-subcomunidades")
            
            if action_type in ["month", "day"]:
                rows = nvg_table.find_elements_by_tag_name("tr")
                if len(rows) in target_size:
                    return
            else:
                if "Seg" not in nvg_table.text:
                    time.sleep(2)
                    return

        except NoSuchElementException:
            print("NoSuchElementException")
            pass
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            pass

        print(f"Attempt #{attempt} failed, waiting {action_type} navigation to load...")
        attempt += 1
        time.sleep(1)

        if attempt == 128:
            raise LimitOfAttemptsReached("Limit of attempts reached, aborting")

def getNewspaperLink(driver: WebDriver, date: datetime.date) -> str:
    """
    Checks if there is newspaper for a given date.
    Returns url of the pdf viewer page if so, None otherwise.
    """
    year_anchor = getYear(driver, date)
    if year_anchor is None:
        print(f"Unable to find year option for year {date.year}")
        return None
    year_anchor.click()
    waitNavigationToLoad(driver, "month")
    
    month_anchor = getMonth(driver, date)
    if month_anchor is None:
        print("Target month have no newspaper")
        return None
    month_anchor.click()
    waitNavigationToLoad(driver, "day")

    day_anchor = getDay(driver, date)
    if day_anchor is None:
        print("This day have no newspapers")
        return None
    day_anchor.click()
    waitNavigationToLoad(driver, "news")

    news_btn = driver.find_element_by_id("id-lista-subcomunidades")
    anchors = news_btn.find_elements_by_tag_name("a")

    links = {}
    for a in anchors:
        if len(a.text) == 0: # there are some broken links with empty texts
            continue
        links[a.text] = a.get_attribute("onclick").split("'")[1] 
    
    print("Url found!")
    return links

def switchFrame(driver: WebDriver, attempts: int = 1):
    """Swithcs driver to content frames when it loads."""
    try:
        driver.switch_to.frame("blockrandom")
    except NoSuchFrameException:
        try:
            h1 = driver.find_element_by_tag_name("h1")
            if h1.text == "504 Gateway Time-out":
                print("FATAL ERROR: 504 Gateway Time-out.")
                exit()
        except NoSuchElementException:
            print(f"Attempt #{attempts} failed...")
            
            if attempts == 128:
                raise LimitOfAttemptsReached("Limit of attempts reached, aborting")
            
            pass

        time.sleep(1)
        switchFrame(driver, attempts + 1)

def saveProgress(urls_listed: []):
    """Saves list of urls to file 'temp.json'."""
    open("temp.json", "w+").write(json.dumps(urls_listed, indent=1))

def listNewspaperToDownload() -> [(datetime.date, str)]:
    """Finds all newspapers not downloaded and returns a list with them."""
    # set language to be used for month and weekday names
    print(">>>>>>>> Checking for new newspaper")  

    locale.setlocale(locale.LC_TIME, "pt_BR") 

    driver = initChromeWebdriver(
        'chromedriver_win_79-0-3945-36.exe',
        use_window=SCREEN_ON
    )
    target = "http://www.iof.mg.gov.br/index.php?/ultima-edicao.html"

    driver.get(target)
    switchFrame(driver)

    # to check if there is new data available
    last_newspaper_date = getLastNewspaperDate(driver)
    try:
        configs = json.loads(open("config.json").read())
        last_date_crawled = datetime.date.fromisoformat(
            configs["last_date_crawled"]
        )
    except FileNotFoundError:
        last_date_crawled = datetime.date(2005, 6, 30)

    if last_newspaper_date <= last_date_crawled:
        print("No new newspaper to crawl. Exit()ting crawler.")
        exit()

    print(
        f"Last date crawled: {last_date_crawled},"
        " last newspaper: {last_newspaper_date}"
    )
    
    try: # trying to continue previous progress
        urls = json.loads(open("temp.json", "r").read())
        print("Continuing progress")

    except FileNotFoundError:
        urls = []

    if len(urls) > 0:
        last_saved = datetime.date.fromisoformat(urls[-1]["date"])
        next_date = last_saved + datetime.timedelta(days=1)
    else:
        next_date = last_date_crawled + datetime.timedelta(days=1)

    last_saved = 0
    count_results = 0

    while next_date <= last_newspaper_date:
        time.sleep(5) # politiness?
        print(f">>>> {count_results}. Checking for date:", next_date)
        new_urls = getNewspaperLink(driver, next_date)
        if new_urls is not None:
            new_urls["date"] = str(next_date)
            urls.append(new_urls)
            count_results += 1

        next_date += datetime.timedelta(days=1)
        
        if count_results > last_saved + 50:
            saveProgress(urls)
            last_saved = count_results
        
    print("Number of dates with newspaper:", len(urls))

    driver.close()

    return urls

def mergePdfFiles(files_to_merge: [str], output_file_address: str):
    """Merge pdf files listed in one single file in the order they are."""
    pdf_merger = PyPDF2.PdfFileMerger()
    for text_pdf_file in files_to_merge:
        pdf_merger.append(PyPDF2.PdfFileReader(text_pdf_file, strict=False))
    pdf_merger.write(output_file_address)
    pdf_merger.close()

def pdf2Txt(source_file: str, final_file: str):
    """Converts pdf file in a txt file."""
    raw = parser.from_file(source_file)
    open(final_file, "w", encoding="utf-8").write(raw['content'])

def createFolders():
    """Creates folders 'jornais/pdf/' and 'jornais/txt' if they do not exists."""
    try:
        os.mkdir('jornais')
    except FileExistsError:
        pass

    try:
        os.mkdir('jornais/pdf')
    except FileExistsError:
        pass

    try:
        os.mkdir('jornais/txt')
    except FileExistsError:
        pass

def openNextPage(driver: WebDriver):
    """Interacts with page to load next pdf page."""
    attempts = 0
    print("Opening next page")
    while True:
        try:
            next_page_div = driver.find_element_by_id(
                "id-div-pagina-posterior"
            )
            next_page_btn = next_page_div.find_element_by_tag_name("a")
            next_page_btn.click()
            time.sleep(1)
            return
        except NoSuchElementException:
            print("NoSuchElementException")
            time.sleep(1)
            pass
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            time.sleep(1)
            pass
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException")
            time.sleep(1)
            pass

        print(f"Attempt #{attempts} failed!")
        attempts += 1
        if attempts == 16:
            print("ERROR Limits of attempt reached")
            exit()

def getContentFrame(driver: WebDriver) -> WebElement:
    """Locate the main iframe tag and returns it."""
    attempts = 0
    print("Getting content page")
    while True:
        try:
            frame = driver.find_element_by_tag_name("iframe")
            return frame
        except NoSuchElementException:
            print("NoSuchElementException")
            time.sleep(1)
            pass
        except StaleElementReferenceException:
            print("StaleElementReferenceException")
            time.sleep(1)
            pass

        print(f"Attempt #{attempts} failed!")
        attempts += 1

        if attempts == 128:
            raise LimitOfAttemptsReached("Limit of attempts reached, aborting")

def downloadPdf(pdf_source: str, fname: str) -> bool:
    """Download pdf stored in url pdf_source and saves it in fname."""
    attempt = 0
    while True:
        myfile = requests.get(pdf_source)

        open(fname, 'wb').write(myfile.content)
        print("Page saved")

        print("Checking pdf...")
        try:
            PyPDF2.PdfFileReader(fname, strict=False)
            print("ok")
            return True
        except PdfReadError:
            print("PdfReadError, trying again...")
            pass

        print(f"Attempt #{attempt} to download pdf failed...", attempt)
        attempt += 1
        if attempt == 16:
            # not raising exception because some pdfs just have corrupted pages
            print("ERROR Limit of attempts reached!")
            return False

def downloadPdfPages(driver: WebDriver, date: str, n_pages: int, pdf_name: str) -> bool:
    """
    Download all pages of a newspaper and merge them.

    It will create temporary pdf files to contain the pages, then merge
    the files and delete them. File will be named 'jornais/pdf/<date>.pdf'
    """
    print("Number of pages:", n_pages)
    files_to_merge = []

    everything_ok = True

    page_count = 0
    while page_count < n_pages:
        everything_ok_with_this_page = True

        print(f"Starting page ({page_count}/{n_pages-1})", getNow())
        if page_count > 0:
            openNextPage(driver)

        pdf_frame = getContentFrame(driver)
        pdf_source = pdf_frame.get_attribute("src")

        fname = f'jornais/temp-{str(date)}-{page_count}.pdf'

        if fileDownloaded(fname):
            files_to_merge.append(fname)
        else:
            if not downloadPdf(pdf_source, fname):
                everything_ok = False
                everything_ok_with_this_page = False
            else:
                files_to_merge.append(fname)

            if everything_ok_with_this_page and page_count == 0:
                n_pages_download = checkPagesDownloaded(fname)
                if n_pages_download > 1:
                    if n_pages_download != n_pages:
                        print("More than one page downloaded, but not all. Giving up on this file.")
                        return False
                    else:
                        print("All pages in page one. Done.")
                        copyfile(fname, pdf_name)
                        os.remove(fname)
                        return True

        page_count += 1

    print("Merging pdf pages...")
    driver.close()
    mergePdfFiles(files_to_merge, pdf_name)

    print("Deleting temporary pdf")
    for file in files_to_merge:
        os.remove(file)
    
    return everything_ok

def fileDownloaded(fname: str) -> bool:
    try:
        f = open(fname, "r")
    except FileNotFoundError:
        return False
    f.close()
    return True

def getNumberOfPages(driver: WebDriver,) -> str:
    attempts = 0
    while attempts < 8:
        try:
            n_pages = driver.find_element_by_id("id-div-numero-pagina-corrente").text
            
            if n_pages is not None:
                return n_pages
        
        except NoSuchElementException:
            try:
                error_message = driver.find_element_by_id("id-area-principal-esquerda").text
                print("Problematic date. Returned page with message:")
                print(error_message)
                print("Ignoring it.")
                return ""
            except NoSuchElementException:
                pass
        
        print(f"Attempts {attempts} for get page number failed...")
        attempts += 1
        time.sleep(1)

    raise LimitOfAttemptsReached("ERROR Limit of attempts reached!")

def downloadNewspaper(newspaper: dict) -> bool:
    """
    Download correspondent newspaper, saves it in pdf and txt.

    Final files will have the address 'jornais/pdf/<date>.pdf',
    'jornais/txt/<date>.txt'.
    """
    date = newspaper['date']
    everything_ok = True

    downloaded_something = False

    for news_type in newspaper:
        everything_ok_with_this = True

        if news_type == 'date':
            continue

        news_type_holder = news_type.replace("/", " ")

        print(">>>>>>>> Starting download for", date, "-", news_type, "-", newspaper[news_type]) 

        pdf_name = f'jornais/pdf/{str(date)}-{news_type_holder}.pdf'

        # Delete 3 lines
        if fileDownloaded(pdf_name):
            print("Ja salvo")
            continue
        
        downloaded_something = True

        driver = initChromeWebdriver(
            'chromedriver_win_79-0-3945-36.exe',
            use_window=SCREEN_ON
        )
        target = newspaper[news_type]

        driver.get(target)
        time.sleep(1)

        
        n_pages = getNumberOfPages(driver)
        if len(n_pages) == 0:
            continue
        
        n_pages = n_pages.split(" ")[-1]

        # some newspapers have no page number and all pages are together
        if n_pages == "de": 
            print("Unique pdf, starting download...")
            pdf_frame = getContentFrame(driver)
            pdf_source = pdf_frame.get_attribute("src")

            pdf_name = f'jornais/pdf/{str(date)}-{news_type_holder}.pdf'
            if not downloadPdf(pdf_source, pdf_name):
                everything_ok_with_this = False
                everything_ok = everything_ok and everything_ok_with_this
        else:
            n_pages = int(n_pages)
            if not downloadPdfPages(driver, date, n_pages, pdf_name):
                everything_ok_with_this = False
                everything_ok = everything_ok and everything_ok_with_this

        if everything_ok_with_this:
            print("Creating txt version...")
            pdf2Txt(pdf_name, f'jornais/txt/{str(date)}-{news_type_holder}.txt')

        print("Sleeping...")
        time.sleep(60) # politiness?

    # return everything_ok
    return downloaded_something

def crawler():
    """
    Crawler to download newspaper from the page:
    http://www.iof.mg.gov.br/index.php?/ultima-edicao.html.

    It saves the date of the last newspaper downloaded in the file config.json.
    If file is not found, it will starting looking for newspapers after
    2015/06/30.
    It will save newspaper in pdf and txt in folders 'jornais/pdf' and
    'jornais/txt'.

    If it is not the first run and there are new newspaper, just execute
    the script again and it will check for updates.
    """
    
    # urls_to_download = listNewspaperToDownload() # UNCOMMENT

    # saveProgress(urls_to_download) # UNCOMMENT
    urls_to_download = json.loads(open("temp.json", "r").read()) # DELETE

    problematic_pdf = []

    createFolders()
    for i in range(len(urls_to_download)):
        url = urls_to_download[i]

        # Uncomment
        # if not downloadNewspaper(url):
        #     problematic_pdf.append(urls_to_download)

        if downloadNewspaper(url): # Delete
            saveProgress(urls_to_download[i + 1:])

    f = open("config.json", "w+")
    last_date_crawled = str(urls_to_download[-1][0])
    f.write(json.dumps({"last_date_crawled": last_date_crawled}, indent=1))
    f.close()

    print("Probably corrupted or mising pages:")
    print(problematic_pdf)

    try:
        os.remove("temp.json")
    except FileNotFoundError:
        pass

def getNow():
    date = datetime.datetime.now()
    return f"{date.hour}:{date.minute}:{date.second}"

def checkPagesDownloaded(pdf_name: str) -> int:
    f = open(pdf_name, "rb")
    reader = PdfFileReader(f)
    n_pages = reader.getNumPages() 
    f.close()
    return n_pages

if __name__ == "__main__":
    crawler()