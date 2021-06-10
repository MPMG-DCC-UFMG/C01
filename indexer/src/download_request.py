import mimetypes
import string
import re 
import hashlib
from datetime import datetime
import requests
import json 
import os

import settings

PUNCTUATIONS = "[{}]".format(string.punctuation)

class DownloadRequest:
    def __init__(self, 
                url: str, 
                data_path: str, 
                crawler_id: str, 
                instance_id: str,
                referer: str, 
                filename: str = '', 
                filetype: str = '', 
                crawled_at_date: str = '') -> None:

        self.url = url
        self.crawler_id = crawler_id
        self.instance_id = instance_id
        self.referer = referer
        self.filetype = filetype if bool(filetype) else self.__detect_filetype()
        self.filename = filename if bool(filename) else self.__generate_filename()
        self.path_to_save = f'{data_path}files/{self.filename}'
        self.crawled_at_date = crawled_at_date

        if not os.path.exists(f'{data_path}files/'):
            os.makedirs(f'{data_path}files/')

    def __generate_filename(self) -> str:        
        filename = hashlib.md5(self.url.encode()).hexdigest()
        filename += '.' + self.filetype if bool(self.filetype) else ''
        return filename

    def __filetype_from_url(self) -> str:
        """Detects the file type through its URL"""

        extension = self.url.split('.')[-1]
        if 0 < len(extension) < 6:
            return extension
        return ''

    def __filetype_from_filename_on_server(self, content_disposition: str) -> str:
        """Detects the file extension by its name on the server"""

        # content_disposition is a string with the following format: 'attachment; filename="filename.extension"'
        # the following operations are to extract only the extension
        extension = content_disposition.split(".")[-1]

        # removes any kind of accents
        return re.sub(PUNCTUATIONS, "", extension)

    def __filetype_from_mimetype(self, mimetype: str) -> str:
        """Detects the file type using its mimetype"""
        extensions = mimetypes.guess_all_extensions(mimetype)
        if len(extensions) > 0:
            return extensions[0].replace('.', '')

        return ''

    def __detect_filetype(self) -> str:
        """detects the file extension, using its mimetype, url or name on the server, if available"""
        filetype = self.__filetype_from_url()
        if len(filetype) > 0:
            return filetype

        response = requests.head(self.url, allow_redirects=True, headers=settings.REQUEST_HEADERS)
        
        content_type = response.headers.get("Content-type", "")
        content_disposition = response.headers.get("Content-Disposition", "")

        response.close()

        filetype = self.__filetype_from_filename_on_server(content_disposition)
        if len(filetype) > 0:
            return filetype

        self.__filetype_from_mimetype(content_type)
    
    def exec_download(self):
        with requests.get(self.url, stream=True, allow_redirects=True, headers=settings.REQUEST_HEADERS) as req:
            with open(self.path_to_save, "wb") as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)

        self.crawled_at_date = str(datetime.today())

    def jsonfy(self):
        return json.dumps({
            'url': self.url,
            'path_to_save': self.path_to_save,
            'crawler_id': self.crawler_id,
            'instance_id': self.instance_id,
            'referer': self.referer,
            'filename': self.filename,
            'filetype': self.filetype,
            'crawled_at_date': self.crawled_at_date
        })