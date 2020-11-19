# External libs
import datetime
import json
import wget
import requests
import heapq
import queue
import threading
import time
import subprocess

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
        cid = description["crawler_id"]
        wait = description["wait_crawler_finish_to_download"]
        time_between = description["time_between_downloads"]
        BaseMessenger.feed(
            FileDownloader.TEMP_FILES_FOLDER,
            {
                "url": url,
                "destination": destination,
                "description": description,
                "crawler_id": cid,
                "wait_crawler_finish_to_download": wait,
                "time_between_downloads": time_between,
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

        url_hash = crawling_utils.hash(item["url"].encode())
        old_file_name = item["description"]["file_name"]
        item["description"]["file_name"] = f"{url_hash}.csv"
        item["description"]["type"] = "csv"
        url_hash = crawling_utils.hash(item["url"].encode())

        success = False

        # # Not sure how binary extractor should work. Needs to check
        # new_file = f"{item['destination']}/csv/{url_hash}.csv"
        # try:
        #     out = binary.extractor.Extractor(new_file)
        #     out.extractor()
        #     success = True
        # except Exception as e:
        #     print(
        #         f"Could not extract csv files from {hsh}.{file_format} -",
        #         f"message: {str(type(e))}-{e}"
        #     )

        if success:
            FileDescriptor.feed_description(
                item['destination'] + "csv/", item['description'])

    @staticmethod
    def process_item(item):
        max_attempts = 3
        success = False
        error_message = ""

        # file size > 1e9 bytes
        big_file = crawling_utils.file_larger_than_giga(item["url"])

        url_hash = crawling_utils.hash(item["url"].encode())
        extension = item["url"].split(".")[-1]

        if len(extension) > 5 or len(extension) == 0:
            print("Could not identify extension of file:", item["url"])
            print("Saving it without extension.")
            extension = ""
            fname = url_hash
        else:
            fname = f"{url_hash}.{extension}"

        item["description"]["file_name"] = fname
        item["description"]["type"] = extension

        for attempt in range(1, max_attempts + 1):
            print(
                "Trying to download file "
                f"(attempt {attempt}/{max_attempts}): ",
                item["url"]
            )
            try:
                if big_file:
                    FileDownloader.download_large_file(item)
                else:
                    FileDownloader.download_small_file(item)

                print("Downloaded", item["url"], "successfully.")
                success = True

                FileDescriptor.feed_description(
                    item['destination'] + "files/", item['description'])
                FileDownloader.convert_binary(item)
                break

            except Exception as e:
                print(
                    f"{attempt}-th attempt to download \"{item['url']}\" "
                    f"failed. Error message: {str(type(e))}-{e}"
                )
                print("Will sleep for 10 seconds before trying again.")
                time.sleep(10 * attempt)
                error_message = str(e)

        if not success:
            print("All attempts to download", item["url"], "failed.")
            response = requests.put(
                f'http://localhost:8000/api/downloads/{item["id"]}/',
                data={
                    "status": "ERROR",
                    "error_message": error_message
                }
            )

        # downloads may create *.tmp files and leave them here.
        try:
            subprocess.run(["rm", "*.tmp"])
        except Exception as e:
            print(f"Cannot clean tmp files: {str(type(e))}-{e}")

    @staticmethod
    def internal_consumer(
        wait_line, heap, stop, in_heap,
        downloads_waiting, lock
    ):
        print("Starting internal_consumer")
        """
        Get items from domain downloaded as early as posisble, and check for
        politiness.
        - wait_line - list of itens to download by domain
        - heap - min heap of (last access, domain)
        - stop - says if threads were told to stop by file flag
        - in_heap - marks if domain is in the heap
        - downloads_waiting - marks downloads waiting craler to finish
        - lock - lock to access variables above
        """
        local_stop = False

        need_to_sleep = False

        while not local_stop:
            if need_to_sleep:
                time.sleep(5)
                need_to_sleep = False

            item_key = None
            item = None

            with lock:
                print("First on heap:", heap[:1])
                if len(heap) == 0 or time.time() < heap[0][0]:
                    local_stop = stop  # update local stop
                    need_to_sleep = True
                    print("Too soon to download. Sleeping...")
                    continue

                (_, item_key) = heapq.heappop(heap)
                item = wait_line[item_key].get()

            print(f"internal_consumer - Starting url: {item['url']}")

            FileDownloader.process_item(item)

            if item["time_between_downloads"] is None:
                add = 1
            else:
                add = item["time_between_downloads"]
            next_download = int(time.time()) + add

            with lock:
                if wait_line[item_key].qsize() > 0:
                    heapq.heappush(heap, (next_download, item_key))
                else:
                    in_heap[item_key] = False
                print(f"re-building heap: {heap}")
                local_stop = stop

    @staticmethod
    def internal_producer(
        wait_line, heap, stop, in_heap,
        downloads_waiting, lock,
        testing=False
    ):
        print("Starting internal_producer")
        """
        Get items from FileDownloader.download_source and put on wait heap,
        so we can change between domains.
        - wait_line - list of itens to download by domain
        - heap - min heap of (last access, domain)
        - stop - says if threads were told to stop by file flag
        - in_heap - marks if domain is in the heap
        - downloads_waiting - marks downloads waiting craler to finish
        - lock - lock to access variables above
        """
        domain_to_key = {}

        for item in FileDownloader.download_source(testing):
            print(f"internal_producer  - received {type(item)} {item}")
            item = json.loads(item)
            if item["destination"][-1] != "/":
                item["destination"] = item["destination"] + "/"

            with lock:
                domain = crawling_utils.get_url_domain(item["url"])

                if domain not in domain_to_key:
                    key = len(domain_to_key)
                    domain_to_key[domain] = key
                    wait_line[key] = queue.Queue()
                    in_heap[key] = False

                key = domain_to_key[domain]

                item = FileDownloader.log_item(item)  # gets item id on db
                wait_line[key].put(item)
                if item["wait_crawler_finish_to_download"]:
                    print(
                        "internal_producer  - item should wait "
                        "crawler to finish"
                    )
                    downloads_waiting.add((key, item["crawler_id"]))
                elif wait_line[key].qsize() == 1 and not in_heap[key]:
                    print("internal_producer  - insertind on heap")
                    heapq.heappush(heap, (1, key))
                else:
                    print(
                        "internal_producer  - this domain "
                        "already has itens on heap"
                    )

                size = wait_line[key].qsize()
                print(f"internal_producer - Received: {item['url']}")
                print(f"internal_producer - Domain key: {key}")
                print(f"internal_producer - Domain wait line size: {size}")
                print(f"internal_producer - heap: {heap}")

        with lock:
            stop = True

    @staticmethod
    def downloads_waiting_crawl_end(
        wait_line, heap, stop, in_heap,
        downloads_waiting, lock
    ):
        """
        Keeps track of downloads that must wait for the crawler to finish.
        Check for these every 60 seconds.
        - wait_line - list of itens to download by domain
        - heap - min heap of (last access, domain)
        - stop - says if threads were told to stop by file flag
        - in_heap - marks if domain is in the heap
        - downloads_waiting - marks downloads waiting craler to finish
        - lock - lock to access variables above
        """
        detail_url = "http://localhost:8000/api/crawlers/"
        local_stop = False
        while not local_stop:
            must_check = []
            with lock:
                for (key, cralwer_id) in downloads_waiting:
                    must_check.append({
                        "key": key,
                        "crawler_id": cralwer_id,
                    })

            print(
                "downloads_waiting_crawl_end",
                "- downloads waiting:",
                must_check
            )

            crawlers_done = []
            for i in must_check:
                crawler = requests.get(detail_url + str(i['crawler_id']) + "/")
                if crawler.json()["running"] is False:
                    crawlers_done.append(i)

            print("downloads_waiting_crawl_end - crawlers_done:", must_check)

            with lock:
                for i in crawlers_done:
                    downloads_waiting.remove((i["key"], i["crawler_id"]))
                    # if this file was discovered after the crawler
                    # finished, we want to avoid inserting it again
                    # in the heap
                    if not in_heap[i["key"]]:
                        heapq.heappush(heap, (time.time() + 60, i["key"]))
                        print(
                            "downloads_waiting_crawl_end - inserting on heap:",
                            i
                        )
                local_stop = stop

            time.sleep(60)

    @staticmethod
    def download_consumer(testing=False):
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
        wait_line = {}  # list of itens to download by domain
        heap = []  # min heap of (last access, domain)
        stop = False  # says if threads were told to stop by file flag
        in_heap = {}  # marks if domain is in the heap
        downloads_waiting = set()  # marks downloads waiting craler to finish
        lock = threading.Lock()  # lock to access variables above

        threads = []

        threads.append(threading.Thread(
            target=FileDownloader.internal_consumer,
            args=(
                wait_line, heap, stop, in_heap,
                downloads_waiting, lock,
            ),
            daemon=True,  # will be killed if only deamon threads are running
        ))

        threads.append(threading.Thread(
            target=FileDownloader.downloads_waiting_crawl_end,
            args=(
                wait_line, heap, stop, in_heap,
                downloads_waiting, lock,
            ),
            daemon=True,  # will be killed if only deamon threads are running
        ))

        threads.append(threading.Thread(
            target=FileDownloader.internal_producer,
            args=(
                wait_line, heap, stop, in_heap,
                downloads_waiting, lock,
                testing
            ),
            daemon=True,  # will be killed if only deamon threads are running
        ))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    @staticmethod
    def download_large_file(item):
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
        def log_progress(current, total, widht=None):
            FileDownloader.log_progress(item["id"], current, total)

        name = f"{item['destination']}files/{item['description']['file_name']}"
        wget.download(item["url"], name, bar=log_progress)

    @staticmethod
    def download_small_file(item):
        """Downloads file to memory then writes to disk."""
        response = requests.get(item["url"], allow_redirects=True)

        name = f"{item['destination']}files/{item['description']['file_name']}"
        with open(name, 'wb') as file:
            file.write(response.content)
        
        FileDownloader.log_progress(item["id"], 100, 100)

    @staticmethod
    def log_progress(item_id, current, total):
        """"""
        response = requests.put(
            f'http://localhost:8000/api/downloads/{item_id}/',
            data={
                "status": "DOWNLOADING" if total != current else "DONE",
                "size": total,
                "progress": current
            }
        )

    @staticmethod
    def log_item(item):
        """"""
        response = requests.post(
            'http://localhost:8000/api/downloads/',
            data={
                "status": "WAITING",
                "description": json.dumps(item),
            }
        )
        item["id"] = response.json()["id"]
        return item
