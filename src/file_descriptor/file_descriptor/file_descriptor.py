# External libs
import datetime
import json

# Project libs
from base_messenger.base_messenger import BaseMessenger

class FileDescriptor(BaseMessenger):
    TEMP_DESCRIPTION_FOLDER = "temp_description_folder"

    @staticmethod
    def feed_description(destination, description):
        """
        File source 'gambiarra'.
        BaseMessenger.feed must be changed to a kafka producer when
        integrations with Kafka and SC are complete.
        Keyword arguments:
        destination -- str, address of the folder that will containt the file
        description -- dict, dictionary of item descriptions
        """
        BaseMessenger.feed(
            FileDescriptor.TEMP_DESCRIPTION_FOLDER,
            {"destination": destination, "description": description}
        )

    @staticmethod
    def stop_description_source():
        """
        Signals that the source should stop checking for new descriptions.
        """
        BaseMessenger.stop_source(FileDescriptor.TEMP_DESCRIPTION_FOLDER)

    @staticmethod
    def description_source(testing=False):
        """
        Description source 'gambiarra'.
        BaseMessenger.source must be changed to a kafka producer when
        integrations with Kafka and SC are complete.
        
        Keyword arguments:
        testing -- do not use this argument. It is used to stop process if any
        error occurs during tests. (default False)
        """
        source = BaseMessenger.source(
            FileDescriptor.TEMP_DESCRIPTION_FOLDER, testing)
        for item in source:
            yield item

    @staticmethod
    def description_consumer(testing=False):
        """
        Writes description of items from FileDescriptor.description_source.
        Items must be json strings of dictionaries containing the following
        keys:
        - destination: str, address of the folder that contains the file
          file_description.jsonl
        - description: str, file description
        Keyword arguments:
        testing -- do not use this argument. It is used to stop process if any
        error occurs during tests. (default False)
        """
        print(
            "==============================================================\n",
            f"Starting file decription consumer at", 
            datetime.datetime.now().isoformat()
        )
        for item_json in FileDescriptor.description_source(testing):
            item = json.loads(item_json)
            FileDescriptor.write_description(item)

    @staticmethod
    def write_description(item):
        """
        Writes description of items from FileDescriptor.description_source.
        Keyword arguments:
        item -- a dict containing the following keys:
        - destination: str, address of the folder that contains the file
          file_description.jsonl
        - description: a dict with file description
        """
        if item["destination"][-1] != "/":
            item["destination"] = item["destination"] + "/"
        file_address = item["destination"] + "file_description.jsonl"
        
        with open(file_address, "a+") as f:
            f.write(json.dumps(item["description"]))
            f.write("\n")