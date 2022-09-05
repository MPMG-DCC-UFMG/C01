from typing import Any, Dict
from typing_extensions import TypedDict

class CrawlRequestDict(TypedDict):
    source_name: str 
    base_url: str
    obey_robots: bool 
    data_path: str
    
    crawler_description: str 
    crawler_type_desc: str 
    crawler_issue: int 

    sc_scheduler_persist: bool
    sc_scheduler_queue_refresh: int 
    sc_queue_hits: int
    sc_queue_window: int
    sc_queue_moderated: bool
    sc_dupefilter_timeout: int 
    sc_global_page_per_domain_limit: int
    sc_global_page_per_domain_limit_timeout: int
    sc_domain_max_page_timeout: int
    sc_scheduler_ip_refresh: int
    sc_scheduler_backlog_blacklist: bool
    sc_scheduler_type_enabled: bool
    sc_scheduler_ip_enabled: bool
    sc_scheduler_item_retries: int
    sc_scheduler_queue_timeout: int
    sc_httperror_allow_all: bool
    sc_retry_times: int
    sc_download_timeout: int

    antiblock_download_delay: int
    antiblock_autothrottle_enabled: bool
    antiblock_autothrottle_start_delay: int
    antiblock_autothrottle_max_delay: int
    antiblock_ip_rotation_enabled: bool
    antiblock_ip_rotation_type: str
    antiblock_max_reqs_per_ip: int 
    antiblock_max_reuse_rounds: int
    antiblock_proxy_list: str
    antiblock_user_agent_rotation_enabled: bool
    antiblock_reqs_per_user_agent: int 
    antiblock_user_agents_list: str
    antiblock_insert_cookies_enabled: bool
    antiblock_cookies_list: str

    captcha: str
    has_webdriver: bool
    webdriver_path: str
    img_xpath: str
    sound_xpath: str


    browser_type: str
    browser_resolution_width: int 
    browser_resolution_height: int 

    explore_links: bool
    link_extractor_max_depth: int
    link_extractor_allow_url: str
    link_extractor_allow_domains: str
    link_extractor_tags: str
    link_extractor_attrs: str
    link_extractor_check_type: bool
    link_extractor_process_value: str

    download_files: bool
    download_files_allow_url: str
    download_files_allow_extensions: str
    download_files_allow_domains: str
    download_files_tags: str
    download_files_attrs: str
    download_files_process_value: str
    download_files_check_large_content: bool
    download_imgs: bool
    
    encoding_detection_method: int
    expected_runtime_category: str
    
    dynamic_processing: bool
    skip_iter_errors: bool
    steps: Dict[str, Any]
