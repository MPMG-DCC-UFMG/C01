from typing_extensions import TypedDict

class CrawlerInstance(TypedDict):
    crawler: int 
    instance_id: int 

    number_files_found: int 
    number_files_success_download: int 
    number_files_error_download: int 

    number_pages_found: int
    number_pages_success_download: int
    number_pages_error_download: int
    number_pages_duplicated_download: int

    page_crawling_finished: bool

    running: bool
    num_data_files: int
    data_size_kbytes: int    

