import threading
from selenium.common import exceptions
import logging


class DownloadThread(threading.Thread):
    """DownloadThread should always e used in preference to threading.Thread.

    The interface provided by DownloadThread is identical to that of threading.Thread,
    however, if an exception occurs in the thread the error will be logged
    (using logging.exception) rather than printed to stderr.

    This is important in daemon style applications where stderr is redirected
    to /dev/null.

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run

    def _wrap_run(self):
        try:
            self._real_run()
        except exceptions.NoSuchElementException:
            logging.exception('File not available for download.')


class MoveFileThread(threading.Thread):
    """DownloadThread should always e used in preference to threading.Thread.

    The interface provided by DownloadThread is identical to that of threading.Thread,
    however, if an exception occurs in the thread the error will be logged
    (using logging.exception) rather than printed to stderr.

    This is important in daemon style applications where stderr is redirected
    to /dev/null.

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run

    def _wrap_run(self):
        try:
            self._real_run()
        except:
            logging.exception('File not found.')