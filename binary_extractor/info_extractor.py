import abc
import csv
import os

class InfoExtractor():

    __metaclass__ = abc.ABCMeta

    def __init__(self, path):
        self.path = path
        self.content = None
        self.metadata = None

    @abc.abstractmethod
    def extract(self):
        raise AssertionError

    @abc.abstractmethod
    def process(self):
        raise AssertionError

    @abc.abstractmethod
    def write():
        raise AssertionError

#TODO:
#put some exceptions!
