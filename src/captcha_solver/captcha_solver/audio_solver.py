import requests
import os
import speech_recognition as sr
from time import sleep

from io import BytesIO
from validators import url


class AudioSolver:
    def __init__(self,
                 model=None,
                 preprocessing=None,
                 webdriver=None,
                 download_dir=None):
        """
        :model:         Audio recognition model, default is None, so _ocr will be used
        :preprocessing: Audio processing method, default is None, so _preprocess will be used
        :webdriver:     Selenium webdrive loaded with the captcha page, default is None, so a new driver will be created
        :download_dir:  Webdriver download path, which contains the downloaded audios
        """
        self.predict = model or self._ocr
        self.preprocess = preprocessing or self._preprocess
        self.driver = webdriver
        self.download_dir = download_dir or "./"

    def _from_url(self, url):
        """
        Download captcha image from a URL
        the driver.get method triggers a download which is then treated in this function

        :url:       URL of the audio file in server
        """

        audio = self.driver.get(url)
        while not os.path.exists(self.download_dir + "audio.wav"):
            sleep(2)
        sleep(2)
        return sr.AudioFile(self.download_dir + "audio.wav")

    def _preprocess(self, audio):
        """
        Default audio preprocessing for captcha images which is None
        so this method return original audio content

        :audio:     Binary audio downloaded
        """

        return audio

    def _ocr(self, audio):
        """
        Defult character recognition, which uses google speach recognition library

        :audio:     Binary audio downloaded
        """

        recognizer = sr.Recognizer()
        with audio as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="pt-BR")
        return text

    def solve(self, audio=None, source=None):
        """
        User function to solve desired captcha

        :audio:     Binary audio loaded by user
        :source:    XPATH of the "Download audio" element in page
        """

        if audio and source:
            raise Exception("Usuário deve informar apenas uma fonte para audio")
        if not audio and not source:
            raise Exception("Usuário deve informar uma fonte para audio")

        aud = audio or self._from_url(source)
        aud = self.preprocess(aud)
        return self.predict(aud)
