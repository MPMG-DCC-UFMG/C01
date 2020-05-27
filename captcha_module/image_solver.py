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
        """
        :url:           Base URL of the desired website
        :model:         Character recognition model, default is None, so _ocr will be used
        :preprocessing: Image processing method, default is None, so _preprocess will be used
        :webdriver:     Selenium webdrive loaded with the captcha page, default is None, so a new driver will be created
        """

        if url is None:
            raise Exception("Usuário deve indicar uma url")
        self.url = url
        self.predict = model or self._ocr 
        self.preprocess = preprocessing or self._preprocess
        self.driver = webdriver or self._get_webdriver()

    def _get_webdriver(self):
        """
        Instantiate webdriver in case the user
        didn't pass the webdriver to be used
        """
 
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)

        #start a session in the desired url
        driver.get(self.url)
        return driver

    def _get_image(self, path):
        """
        Check if the path represents an URL or an xpath
        and return the downloaded image

        :path:      Path to the captch image, which can be an URL or XPATH of the image element
        """

        if url(path):
            return self._from_url(path)
        return self._from_screenshot(path)

    def _from_url(self, url):
        """
        Download captcha image from a URL

        :url:       URL of the audio file in server
        """

        image = requests.get(url).content
        im = Image.open(BytesIO(image))
        return im

    def _from_screenshot(self, xpath):
        """
        Download captcha image from XPATH using Selenium's screenshot feature 

        :xpath:     XPATH of the image element in page
        """

        screenshot = self.driver.get_screenshot_as_png()
        element = self.driver.find_element_by_xpath(xpath)
        location = element.location
        size = element.size

        im = Image.open(BytesIO(screenshot))
        x, y = location['x'], location['y']
        width, height = x + size['width'], y + size['height']

        return im.crop((int(x), int(y), int(width), int(height)))

    def _preprocess(self, image):
        """
        Default image preprocessing for captcha images

        :image:     Binary image loaded
        """

        # change image color encoding
        img = np.array(image)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 

        # apply mask to filter the desired color
        lower = np.array([0,220,50])
        upper = np.array([360,255,255])
        mask = cv2.inRange(hsv, lower, upper) 
        img = cv2.bitwise_and(img, img, mask=mask)

        # transform colored images into greyscale then into binary image (black and white only)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return img

    def _ocr(self, image):
        """
        Defult character recognition, which uses tesseract library

        :image:     Binary image loaded
        """

        return pytesseract.image_to_string(image)

    def check_exists_by_xpath(self, xpath):
        """
        Check if XPATH element is present in the page

        :xpath:     XPATH of the image element in page
        """ 

        try:
            # this method raises NoSuchElementException when the element is not found 
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def solve(self, image=None, source=None):
        """
        User function to solve desired captcha

        :image:     Binary image loaded by user
        :source:    XPATH of the image element in page or the image URL
        """

        if image and source:
            raise Exception("Usuário deve informar apenas uma fonte para imagem")
        if not image and not source:
            raise Exception("Usuário deve informar uma fonte para imagem")

        img = image or self._get_image(source)
        img = self.preprocess(img)
        text = self.predict(img)
        return text     
