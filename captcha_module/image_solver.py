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

class ImageSolver:
    def __init__(self, url, model=None, preprocessing=None, webdriver=None):
        if url is None:
            raise Exception("Usuário deve indicar uma url")
        self.url = url
        self.predict = model or self._ocr 
        self.preprocess = preprocessing or self._preprocess
        self.driver = webdriver or self._get_webdriver()

    def _get_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)
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
        self.driver.get(self.url)

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

    def solve(self, image=None, xpath=None, url=None):
        if xpath and url:
            raise Exception("Usuário deve informar apenas uma fonte para imagem")
        
        img = image or self._get_image(xpath or url)
        img = self.preprocess(img)
        text = self.predict(img)
        return text     
