from datetime import datetime
import hashlib
import mimetypes
import os
import re
import requests
import string
import time
from bs4 import BeautifulSoup

import settings
from crawling_utils import notify_file_downloaded_with_error

PUNCTUATIONS = "[{}]".format(string.punctuation)

MAX_ATTEMPTS = 3
INTERVAL_BETWEEN_ATTEMPTS = 30


class DownloadRequest:
    def __init__(self,
                url: str,
                data_path: str,
                crawler_id: str,
                instance_id: str,
                referer: str,
                filename: str = '',
                filetype: str = '',
                crawled_at_date: str = '',
                attrs: dict = {},
                cookies: dict = {}) -> None:

        self.attrs = attrs,
        self.url = url
        self.crawler_id = crawler_id
        self.instance_id = instance_id
        self.referer = referer
        self.filetype = filetype if bool(filetype) else self.__detect_filetype()
        self.filename = filename if bool(filename) else self.__generate_filename()

        self.temp_path_to_save = os.path.join(settings.OUTPUT_FOLDER, data_path,
            str(instance_id), 'data', 'files', 'temp', self.filename)

        self.path_to_save = os.path.join(settings.OUTPUT_FOLDER, data_path,
            str(instance_id), 'data', 'files', self.filename)

        self.data_path = data_path
        self.content_hash = None
        self.crawled_at_date = crawled_at_date
        self.cookies = cookies


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

    def exec_download(self, worker_name: str) -> bool:
        print(f"[{datetime.now()}] [FD] {worker_name} Worker: Downloading {self.url}")

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            self.content_hash = hashlib.md5()
            with requests.get(self.url, stream=True, allow_redirects=True,
                headers=settings.REQUEST_HEADERS, cookies=self.cookies) as req:
                if req.status_code != 200:
                    attempt += 1
                    time.sleep(attempt * INTERVAL_BETWEEN_ATTEMPTS)
                    continue

                # Create a BeautifulSoup object to parse the HTML content of the requested page.
                soup = BeautifulSoup(req.content, "html.parser")
                # Find any meta tag with an http-equiv attribute equal to "refresh".
                meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
                # If such a meta tag is found:
                if meta_refresh:
                    # Print a message indicating that the URL uses a meta-tag.
                    print(f"[FD] A página {self.url} utiliza meta-tag")
                    # Get the value of the "content" attribute of the meta-refresh tag.
                    content = meta_refresh["content"]
                    # Check if there is a substring "url=" within the content value.
                    url_index = content.find("url=")
                    # If the substring is found:
                    if url_index != -1:
                        # Extract the final URL from the content value.
                        final_url = content[url_index + 4:]
                        # Print a message indicating the final URL.
                        print("[FD] URL final: ", final_url)
                        # Update the URL to the final URL extracted from the meta tag.
                        self.url = "https://www.cristais.mg.gov.br"+final_url
                        # Continue looping through the code since the URL has been updated.
                        continue
                
                with open(self.temp_path_to_save, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
                        self.content_hash.update(chunk)
                    self.content_hash = self.content_hash.hexdigest()
                    break

        if attempt == MAX_ATTEMPTS:
            notify_file_downloaded_with_error(self.instance_id)
            return False

        else:
            self.crawled_at_date = str(datetime.today())
            return True

    def cancel(self):
        os.remove(self.temp_path_to_save)

    def save(self):
        os.replace(self.temp_path_to_save, self.path_to_save)

    def get_description(self) -> dict:
        return {
            'url': self.url,
            'data_path': self.data_path,
            'relative_path': self.path_to_save,
            'crawler_id': self.crawler_id,
            'instance_id': self.instance_id,
            'referer': self.referer,
            'file_name': self.filename,
            'type': self.filetype,
            'attrs': self.attrs,
            'content_hash': self.content_hash,
            'crawled_at_date': self.crawled_at_date,
            'cookies': self.cookies,
            'extracted_files': [

            ]
        }
