import requests
import pytesseract
import cv2
import numpy as np
import scipy.ndimage

from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from selenium import webdriver
from validators import url
from skimage.color import rgb2gray, rgba2rgb
from selenium.common.exceptions import NoSuchElementException        


class ImageSolver:
    def __init__(self, 
                 url, 
                 model=None,
                 preprocessing=None,
                 webdriver=None):

        if url is None:
            raise Exception("Usuário deve indicar uma url")
        self.url = url
        self.predict = model or self._ocr 
        self.preprocess = preprocessing or self._preprocess
        self.driver = webdriver or self._get_webdriver()

    def _get_webdriver(self):
        """
        This functions intantiate the webdriver in case the user
        didn't passed the webdriver to be used
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)
        driver.get(self.url)
        return driver

    def _get_image(self, path):
        if url(path):
            return self._from_url(path)
        return self._from_screenshot(path)

    def _from_url(self, url):
        image = requests.get(url).content
        im = Image.open(BytesIO(image))
        return im

    def _from_screenshot(self, xpath):
        screenshot = self.driver.get_screenshot_as_png() # saves screenshot of entire page
        element = self.driver.find_element_by_xpath(xpath)
        location = element.location
        size = element.size

        im = Image.open(BytesIO(screenshot)) # uses PIL library to open image in memory
        x, y = location['x'], location['y']
        width, height = x + size['width'], y + size['height']

        return im.crop((int(x), int(y), int(width), int(height)))

    def _preprocess(self, image):
        img = np.array(image)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
        lower = np.array([0,220,50])
        upper = np.array([360,255,255])
        mask = cv2.inRange(hsv, lower, upper) 
        img = cv2.bitwise_and(img, img, mask=mask) 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return img

    def _ocr(self, image):
        return pytesseract.image_to_string(image)

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def solve(self, image=None, source=None):
        if image and source:
            raise Exception("Usuário deve informar apenas uma fonte para imagem")
        if not image and not source:
            raise Exception("Usuário deve informar uma fonte para imagem")

        img = image or self._get_image(source)
        img = self.preprocess(img)
        text = self.predict(img)
        return text     
