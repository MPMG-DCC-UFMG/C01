import requests
import os
import speech_recognition as sr
from time import sleep

from io import BytesIO
from validators import url

class AudioSolver:
    def __init__(self,
                 model=None,
                 preprocessing=None):
        """
        :model:         Audio recognition model, default is None, so _ocr will be used
        :preprocessing: Audio processing method, default is None, so _preprocess will be used
        """
        self.predict = model or self._ocr
        self.preprocess = preprocessing or self._preprocess

    def _from_file(self, filename):
        """
        Load audio file from filename

        :filename:  String representing the audio file
        """

        return sr.AudioFile(filename)

    def _preprocess(self, audio):
        """
        Default audio preprocessing for captcha images which is None
        so this method return original audio content

        :audio:     Binary audio
        """

        return audio

    def _ocr(self, audio):
        """
        Defult character recognition, which uses google speech recognition library

        :audio:     Binary audio
        """

        recognizer = sr.Recognizer()
        with audio as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language = "pt-BR")
        return text

    def solve(self, audio=None, source=None):
        """
        User function to solve desired captcha

        :audio:     Binary audio loaded by user
        :source:    String representing the audio file location
        """

        if audio and source:
            raise Exception("Usuário deve informar apenas uma fonte para audio")
        if not audio and not source:
            raise Exception("Usuário deve informar uma fonte para audio")

        aud = audio or self._from_file(source)
        aud = self.preprocess(aud)
        return self.predict(aud)
