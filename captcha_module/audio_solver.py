import requests
import uuid
import os
import speech_recognition as sr
from time import sleep

from io import BytesIO
from selenium import webdriver
from validators import url

class AudioSolver:
    def __init__(self, url, model=None, preprocessing=None, webdriver=None, download_dir=None):
        if url is None:
            raise Exception("Usuário deve indicar uma url")
        self.url = url
        self.predict = model or self._ocr 
        self.preprocess = preprocessing or self._preprocess
        self.id = uuid.uuid4().hex
        self.download_dir = download_dir or  "./" + self.id
        self.driver = webdriver or self._get_webdriver()

    def _get_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False
        })
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)
        return driver

    def _get_audio(self, path):
        if not url(path):
            raise Exception("URL informada não é válida")
        return self._from_url(path)

    def _from_url(self, url):
        audio = self.driver.get(url)
        while not os.path.exists(self.download_dir + "/audio.wav"):
            sleep(2)
        sleep(2)
        return sr.AudioFile(self.download_dir + "/audio.wav")

    def _preprocess(self, audio):
        return audio

    def _ocr(self, audio):
        recognizer = sr.Recognizer()
        with audio as source:
            audio = recognizer.record(source)                        
        text = recognizer.recognize_google(audio, language = "pt-BR")
        return text

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def solve(self, audio=None, source=None):
        if audio and source:
            raise Exception("Usuário deve informar apenas uma fonte para audio")
        if not audio and not source:
            raise Exception("Usuário deve informar uma fonte para audio")

        aud = audio or self._get_audio(source)
        aud = self.preprocess(aud)
        text = self.predict(aud)
        return text     
