from typing_extensions import TypedDict

class CrawlerQueueItemDict(TypedDict):
    queue: int
    queue_type: str
    crawl_request: int 
    forced_execution: bool
    running: bool
    position: int