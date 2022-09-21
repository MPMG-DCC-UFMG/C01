from __future__ import annotations 

from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from crawling_utils.constants import (AUTO_ENCODE_DETECTION,
                                      HEADER_ENCODE_DETECTION)
from main.models import TimeStamped

class CrawlRequest(TimeStamped):

    # BASIC INFO ##############################################################
    source_name = models.CharField(max_length=200)
    base_url = models.TextField()
    obey_robots = models.BooleanField(blank=True, null=True)
    crawler_description = models.TextField(default='')
    
    CRAWLERS_TYPES = [
        ('Contratos', 'Contratos'),
        ('Despesas', 'Despesas'),
        ('Diários', 'Diários'),
        ('Licitação', 'Licitação'),
        ('Não Informado', 'Não Informado'),
        ('Processos', 'Processos'),
        ('Servidores', 'Servidores'),
        ('Transparência', 'Transparência'),
        ('Outro', 'Outro'),
    ]

    crawler_type_desc = models.CharField(max_length=15,
                                    choices=CRAWLERS_TYPES,
                                    default='Não Informado')

    crawler_issue = models.PositiveIntegerField(default=0)
    # This regex is a bit convolute, but in summary: it allows numbers,
    # letters, dashes and underlines. It allows forward and backward slashes
    # unless it occurs in the first character (since we don't allow absolute
    # paths).
    pathValid = RegexValidator(r'^[0-9a-zA-Z\-_][0-9a-zA-Z\/\\\-_]*$',
                               'Esse não é um caminho relativo válido.')
    data_path = models.CharField(max_length=2000, validators=[pathValid])

    # SCRAPY CLUSTER ##########################################################

    # Don't cleanup redis queues, allows to pause/resume crawls.
    sc_scheduler_persist = models.BooleanField(default=True)

    # seconds to wait between seeing new queues, cannot be faster than spider_idle time of 5
    sc_scheduler_queue_refresh = models.PositiveIntegerField(default=10,
        validators=[MinValueValidator(5)])

    # throttled queue defaults per domain, x hits in a y second window
    sc_queue_hits = models.PositiveIntegerField(default=10)
    sc_queue_window = models.PositiveIntegerField(default=60)

    # we want the queue to produce a consistent pop flow
    sc_queue_moderated = models.BooleanField(default=True)

    # how long we want the duplicate timeout queues to stick around in seconds
    sc_dupefilter_timeout = models.PositiveIntegerField(default=600)

    # how many pages to crawl for an individual domain. Cluster wide hard limit.
    sc_global_page_per_domain_limit = models.PositiveIntegerField(null=True, blank=True)

    # how long should the global page limit per domain stick around in seconds
    sc_global_page_per_domain_limit_timeout = models.PositiveIntegerField(default=600)

    # how long should the individual domain's max page limit stick around in seconds
    sc_domain_max_page_timeout = models.PositiveIntegerField(default=600)

    # how often to refresh the ip address of the scheduler
    sc_scheduler_ip_refresh = models.PositiveIntegerField(default=60)

    # whether to add depth >= 1 blacklisted domain requests back to the queue
    sc_scheduler_backlog_blacklist = models.BooleanField(default=True)

    # add Spider type to throttle mechanism
    sc_scheduler_type_enabled = models.BooleanField(default=True)

    # add ip address to throttle mechanism
    sc_scheduler_ip_enabled = models.BooleanField(default=True)

    # how many times to retry getting an item from the queue before the spider is considered idle
    sc_scheduler_item_retries = models.PositiveIntegerField(default=3)

    # how long to keep around stagnant domain queues
    sc_scheduler_queue_timeout = models.PositiveIntegerField(default=3600)

    # Allow all return codes
    sc_httperror_allow_all = models.BooleanField(default=True)

    sc_retry_times = models.PositiveIntegerField(default=3)

    sc_download_timeout = models.PositiveIntegerField(default=10)

    # ANTIBLOCK ###############################################################
    # Options for Delay
    antiblock_download_delay = models.IntegerField(blank=True, null=True)

    antiblock_autothrottle_enabled = models.BooleanField(default=False, blank=True)
    antiblock_autothrottle_start_delay = models.IntegerField(blank=True, null=True)
    antiblock_autothrottle_max_delay = models.IntegerField(blank=True, null=True)

    # Options for IP rotation
    antiblock_ip_rotation_enabled = models.BooleanField(default=False, blank=True)

    antiblock_ip_rotation_type = models.CharField(max_length=15, null=True, blank=True)
    antiblock_max_reqs_per_ip = models.IntegerField(blank=True, null=True)
    antiblock_max_reuse_rounds = models.IntegerField(blank=True, null=True)

    antiblock_proxy_list = models.TextField(blank=True, null=True)  # available for Proxy List

    # Options for User Agent rotation
    antiblock_user_agent_rotation_enabled = models.BooleanField(default=False, blank=True)

    antiblock_reqs_per_user_agent = models.IntegerField(blank=True, null=True)
    antiblock_user_agents_list = models.TextField(blank=True, null=True)

    # Options for Cookies
    antiblock_insert_cookies_enabled = models.BooleanField(default=False, blank=True)

    antiblock_cookies_list = models.TextField(blank=True, null=True)
    # antiblock_persist_cookies = models.BooleanField(blank=True, null=True)

    # CAPTCHA #################################################################
    CAPTCHA_TYPE = [
        ('none', 'None'),
        ('image', 'Image'),
        ('sound', 'Sound'),
    ]
    captcha = models.CharField(
        max_length=15, choices=CAPTCHA_TYPE, default='none')
    has_webdriver = models.BooleanField(blank=True, null=True)
    webdriver_path = models.CharField(max_length=1000, blank=True, null=True)
    # Options for captcha
    # Options for image
    img_xpath = models.CharField(max_length=100, blank=True, null=True)
    # Options for sound
    sound_xpath = models.CharField(max_length=100, blank=True, null=True)

    # Steps activation
    dynamic_processing = models.BooleanField(blank=True, null=True)

    # Browser options
    BROWSER_TYPE = [
        ('chromium', 'Chromium'),
        ('webkit', 'Webkit'),
        ('firefox', 'Mozilla Firefox'),
    ]
    browser_type = models.CharField(max_length=50, choices=BROWSER_TYPE, default='chromium')

    # If true, skips failing iterations with a warning, else, stops the crawler
    # if an iteration fails
    skip_iter_errors = models.BooleanField(default=False)
    browser_resolution_width = models.IntegerField(blank=True, null=True)
    browser_resolution_height = models.IntegerField(blank=True, null=True)


    # DETAILS #################################################################
    explore_links = models.BooleanField(blank=True, null=True)
    link_extractor_max_depth = models.IntegerField(blank=True, null=True)
    link_extractor_allow_url = models.CharField(
        max_length=1000, blank=True, null=True
    )
    link_extractor_allow_domains = models.CharField(
        max_length=1000, blank=True, null=True
    )
    link_extractor_tags = models.CharField(
        max_length=1000, blank=True, null=True
    )
    link_extractor_attrs = models.CharField(
        max_length=1000, blank=True, null=True
    )
    link_extractor_check_type = models.BooleanField(blank=True, null=True)
    link_extractor_process_value = models.TextField(
        max_length=1000, blank=True, null=True
    )

    download_files = models.BooleanField(blank=True, null=True)
    download_files_allow_url = models.CharField(
        max_length=1000, blank=True, null=True)
    download_files_allow_extensions = models.CharField(
        blank=True, null=True, max_length=2000)
    download_files_allow_domains = models.CharField(
        max_length=1000, blank=True, null=True
    )
    download_files_tags = models.CharField(
        max_length=1000, blank=True, null=True
    )
    download_files_attrs = models.CharField(
        max_length=1000, blank=True, null=True
    )
    download_files_process_value = models.TextField(
        max_length=1000, blank=True, null=True
    )
    download_files_check_large_content = models.BooleanField(default=True, blank=True, null=True)

    download_imgs = models.BooleanField(default=False)

    steps = models.CharField(
        blank=True, null=True, max_length=9999999, default='{}')

    ENCODE_DETECTION_CHOICES = [
        (HEADER_ENCODE_DETECTION, 'Via cabeçalho da resposta'),
        (AUTO_ENCODE_DETECTION, 'Automático'),
    ]

    encoding_detection_method = models.IntegerField(choices=ENCODE_DETECTION_CHOICES, default=HEADER_ENCODE_DETECTION)

    # CRAWLER QUEUE ============================================================
    EXP_RUNTIME_CAT_CHOICES = [
        ('fast', 'Rápido'),
        ('medium', 'Médio'),
        ('slow', 'Lento'),
    ]

    expected_runtime_category = models.CharField(
        null=False, max_length=8, default='medium', choices=EXP_RUNTIME_CAT_CHOICES)

    @staticmethod
    def process_parameter_data(param_list):
        """
        Processes the parameter data turning it into a format recognizable by
        the spider

        :param param_list: list of parameters (as specified in the
                           ParameterHandler model)

        :returns: list of parameters for the Templated URL
        """
        url_parameter_handlers = []
        for param in param_list:
            if 'id' in param:
                del param['id']
            if 'crawler_id' in param:
                del param['crawler_id']

            # Convert Date parameters into iso string for serialization into
            # JSON
            if param['start_date_date_param'] is not None:
                iso_str = param['start_date_date_param'].isoformat()
                param['start_date_date_param'] = iso_str

            if param['end_date_date_param'] is not None:
                iso_str = param['end_date_date_param'].isoformat()
                param['end_date_date_param'] = iso_str

            url_parameter_handlers.append(param)

        return url_parameter_handlers


    @staticmethod
    def process_response_data(resp_list):
        """
        Processes the response handler data turning it into a format
        recognizable by the spider

        :param resp_list: list of response handlers (as specified in the
                          ResponseHandler model)

        :returns: list of response handlers for the Templated URL
        """
        url_response_handlers = []
        for resp in resp_list:
            if 'id' in resp:
                del resp['id']
            if 'crawler_id' in resp:
                del resp['crawler_id']

            url_response_handlers.append(resp)

        return url_response_handlers


    @staticmethod
    def process_config_data(crawler, config):
        """
        Removes unnecessary fields from the configuration data and loads the
        data for modules that require access to other models

        :param crawler: the crawler instance for which we are configuring
        :param config:  dict containing the attributes for the CrawlRequest
                        instance

        :returns: dict with the configuration for the crawler
        """
        del config['creation_date']
        del config['last_modified']

        if config["data_path"][-1] == "/":
            config["data_path"] = config["data_path"][:-1]

        # Include information on parameter handling
        param_list = crawler.parameter_handlers.values()
        parameter_handlers = CrawlRequest.process_parameter_data(param_list)
        config['templated_url_parameter_handlers'] = parameter_handlers

        # Include information on response handling
        resp_list = crawler.response_handlers.values()
        response_handlers = CrawlRequest.process_response_data(resp_list)
        config['templated_url_response_handlers'] = response_handlers

        return config

    @property
    def running(self):
        return self.instances.filter(running=True).exists()

    @property
    def waiting_on_queue(self):
        on_queue = self.queue_items.all().exists()
        if on_queue:
            crawler_queue_item = self.queue_items.first()
            return not crawler_queue_item.running
        return False

    @property
    def running_instance(self):
        inst_query = self.instances.filter(running=True)
        if inst_query.exists():
            return inst_query.get()
        return None

    @property
    def last_instance(self):
        last_instance = self.instances.order_by('-creation_date')[:1]
        try:
            return last_instance[0]
        except:
            return None

    def __str__(self):
        return self.source_name