# External libs
import datetime
import json
import wget

# Project libs
import binary
import crawling_utils
from crawlers.file_descriptor import FileDescriptor
from crawlers.base_messenger import BaseMessenger


class FileDownloader(BaseMessenger):
    TEMP_FILES_FOLDER = "temp_files_to_download" 

    @staticmethod
    def feed_downloader(url, destination, description):
        """
        Download source 'gambiarra'.
        BaseMessenger.feed must be changed to a kafka producer when
        integrations with Kafka and SC are complete.

        Keyword arguments:
        url -- str, file url
        destination -- str, address of the folder that will containt the file
        description -- dict, dictionary of item descriptions
        """
        BaseMessenger.feed(
            FileDownloader.TEMP_FILES_FOLDER,
            {
                "url": url,
                "destination": destination,
                "description": description
            }
        )

    @staticmethod
    def stop_downloader_source():
        """
        Signals that the source should stop checking for new descriptions.
        """
        BaseMessenger.stop_source(FileDownloader.TEMP_FILES_FOLDER)

    @staticmethod
    def download_source(testing=False):
        """
        Download source 'gambiarra'.
        BaseMessenger.source must be changed to a kafka producer when
        integrations with Kafka and SC are complete.
        
        Keyword arguments:
        testing -- do not use this argument. It is used to stop process if any
        error occurs during tests. (default False)
        """
        source = BaseMessenger.source(
            FileDownloader.TEMP_FILES_FOLDER, testing)
        for item in source:
            yield item
        
    @staticmethod
    def convert_binary(item):
        """
        Items must be a dictionary with the following keys:
        - url: str, file url
        - destination: str, address of the folder that will containt the file
        - description: dict, dictionary of item descriptions
        """
        item["description"]["file_name"] = f"{url_hash}.{csv}"
        item["description"]["type"] = "csv"
        url_hash = crawling_utils.hash(item["url"])

        success = False

        new_file = f"{item['destination']}/csv/{url_hash}.{csv}"
        try:
            out = binary.extractor.Extractor(new_file)
            out.extractor()
            success = True
        except Exception as e:
            print(
                f"Could not extract csv files from {hsh}.{file_format} -",
                f"message: {str(type(e))}-{e}"
            )

        if success:
            FileDescriptor.feed_description(
                item['destination'] + "csv/", item['description'])

    @staticmethod
    def download_consumer(max_attempts=3, testing=False):
        """
        Download items from FileDownloader.download_source.
        Items must be json strings of dictionaries containing the following
        keys:
        - url: str, file url
        - destination: str, address of the folder that will containt the file
        - description: dict, dictionary of item descriptions
        It will try to download a file 3 times before giving up.

        Keyword arguments:
        max_attempts -- max number of attempts to download a file
        testing -- do not use this argument. It is used to stop process if any
        error occurs during tests. (default False)
        """
        print(
            "==============================================================\n",
            f"Starting file downloader at", 
            datetime.datetime.now().isoformat()
        )
        for item_json in FileDownloader.download_source(testing):
            item = json.loads(item_json)
            if item["destination"][-1] != "/":
                item["destination"] = item["destination"] + "/"

            success = False
            for attempt in range(1, max_attempts + 1):
                print(
                    "Trying to download file "
                    f"(attempt {attempt}/{max_attempts}): ",
                    item["url"]
                )
                try:
                    FileDownloader.download_file(item)
                    print("Downloaded", item["url"], "successfully.")
                    success = True

                    FileDownloader.convert_binary(item)
                    break
                except Exception as e:
                    print(
                        f"{attempt}-th attempt to download \"{item['url']}\" "
                        f"failed. Error message: {str(type(e))}-{e}"
                    )

            if not success:
                print("All attempts to download", item["url"], "failed.")

    @staticmethod
    def download_file(item):
        """
        Download an item using wget.download.
        The file name will be a hash function of the file url.
        It will print a progress bar on stdout, and will add the file name to
        the description.

        Keyword arguments:
        item -- a dictionary with the following keys:
        - url: str, file url
        - destination: str, address of the folder that will containt the file
        - description: dict, dictionary of item descriptions
        """
        url_hash = crawling_utils.hash(item["url"])
        extension = item["url"].split(".")[-1]
        fname = f"{url_hash}.{extension}"
        item["description"]["file_name"] = fname
        item["description"]["type"] = extension


        full_name = item["destination"] + "files/" + fname
        print("FILE NAME:", full_name)
        wget.download(item["url"], full_name)
        print() # because the line above prints a progress bar without a \n
        
        FileDescriptor.feed_description(
            item['destination'] + "files/", item['description'])
