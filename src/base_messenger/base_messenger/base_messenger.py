import json

# Only needed for the fix before kafka and sc integrations.
# Remove and these are done.
import time
import os
import shutil
import random


class BaseMessenger:
    @staticmethod
    def feed(address, content):
        """
        Feeder "gambiarra"
        Must be replaced by a kafka producer when integrations with Kafka and
        SC are complete.

        Keyword arguments:
        address -- str, address to folder that must contain the file
        content -- any, json serializable
        """
        name = int(random.random() * 100000)
        fname = f"{address}/{name}.json"

        with open(fname, "w+") as f:
            f.write(json.dumps(content))

    @staticmethod
    def stop_source(address):
        """
        Signals that the source should stop checking for new descriptions.
        
        Keyword arguments:
        address -- str, address to folder that contains flags.json file
        """
        with open(address + "/flags.json", "w") as f:
            f.write(json.dumps({"stop": True}))

    @staticmethod
    def source(address, testing=False):
        """
        Download source 'gambiarra'.
        Must be replaced by a kafka listener when integrations with Kafka and
        SC are complete.
        
        Keyword arguments:
        address -- str, address to folder that will contain new items
        testing -- do not use this argument. It is used to stop process if any
        error occurs during tests. (default False)
        """
        # Create essential files and folder
        try:
            shutil.rmtree(address)
        except FileNotFoundError:
            pass
        os.mkdir(address)

        flag_file = address + "/flags.json"
        with open(flag_file, "w") as f:
            f.write(json.dumps({"stop": False}))

        # Check for new files every 10 seconds
        # files are only yielded after they appeared in two checks
        stop = False
        file_check = {}
        count = 5
        while not stop:
            if testing:
                count -= 1
                if count == 0:
                    break

            new_files = os.listdir(address)
            print(new_files)
            to_yield = []
            for f in new_files:
                if f == "flags.json":
                    continue

                print(f"Found file {f}")

                if f not in file_check:
                    file_check[f] = 0
                else:
                    to_yield.append(f)

            for f in to_yield:
                name = address + "/" + f
                content = open(name, "r").read()
                print("Yielding file", f, ", content:", content)
                yield content

                del file_check[f]
                os.remove(name)

            time.sleep(10)
            with open(flag_file, "r") as f:
                flags = json.loads(f.read())
                print("flags:", flags)
                stop = flags["stop"]

        shutil.rmtree(address)
