import requests
import pytesseract
import cv2
import numpy as np
import scipy.ndimage

from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from skimage.color import rgb2gray, rgba2rgb


class ImageSolver:
    def __init__(self,
                 model=None,
                 preprocessing=None):
        """
        :model:         Character recognition model, default is None, so _ocr will be used
        :preprocessing: Image processing method, default is None, so _preprocess will be used
        """

        self.predict = model or self._ocr
        self.preprocess = preprocessing or self._preprocess

    def _from_url(self, url):
        """
        Download captcha image from a URL

        :url:       URL of the audio file in server
        """

        image = requests.get(url).content
        im = Image.open(BytesIO(image))
        return im

    def _preprocess(self, image):
        """
        Default image preprocessing for captcha images

        :image:     Binary image loaded
        """

        # change image color encoding
        img = np.array(image)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # apply mask to filter the desired color
        lower = np.array([0, 220, 50])
        upper = np.array([360, 255, 255])
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

        img = image or self._from_url(source)
        img = self.preprocess(img)
        return self.predict(img)
