from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from crawlers.constants import *


class TimeStamped(models.Model):
    creation_date = models.DateTimeField()
    last_modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = timezone.now()

        self.last_modified = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class CrawlRequest(TimeStamped):

    # BASIC INFO ##############################################################
    source_name = models.CharField(max_length=200)
    base_url = models.CharField(max_length=200)
    obey_robots = models.BooleanField(blank=True, null=True)
    pathValid = RegexValidator(r'^[0-9a-zA-Z\/\\-_]*$',
                               'This is not a valid path.')
    data_path = models.CharField(max_length=2000,
                                 blank=True, null=True,
                                 validators=[pathValid])

    REQUEST_TYPES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
    ]
    request_type = models.CharField(max_length=15,
                                    choices=REQUEST_TYPES,
                                    default='GET')

    # ANTIBLOCK ###############################################################
    # Options for Delay
    antiblock_download_delay = models.IntegerField(blank=True, null=True)
    antiblock_autothrottle_enabled = models.BooleanField(blank=True, null=True)
    antiblock_autothrottle_start_delay = models.IntegerField(
        blank=True, null=True)
    antiblock_autothrottle_max_delay = models.IntegerField(
        blank=True, null=True)

    # Options for antiblock masks
    ANTIBLOCK_MASK_TYPE = [
        ('none', 'None'),
        ('ip', 'IP rotation'),
        ('user_agent', 'User-agent rotation'),
        ('cookies', 'Use cookies'),
    ]
    antiblock_mask_type = models.CharField(
        max_length=15,
        choices=ANTIBLOCK_MASK_TYPE,
        blank=True,
        null=True,
        default='none'
    )

    # Options for IP rotation
    IP_TYPE = [
        ('tor', 'Tor'),
        ('proxy', 'Proxy'),
    ]
    antiblock_ip_rotation_type = models.CharField(
        max_length=15, choices=IP_TYPE, null=True, blank=True)
    antiblock_proxy_list = models.CharField(
        max_length=2000, blank=True, null=True)  # available for Proxy List
    antiblock_max_reqs_per_ip = models.IntegerField(blank=True, null=True)
    antiblock_max_reuse_rounds = models.IntegerField(blank=True, null=True)

    # Options for User Agent rotation
    antiblock_reqs_per_user_agent = models.IntegerField(blank=True, null=True)
    antiblock_user_agents_file = models.CharField(
        max_length=2000, blank=True, null=True)

    # Options for Cookies
    antiblock_cookies_file = models.CharField(
        max_length=2000, blank=True, null=True)
    antiblock_persist_cookies = models.BooleanField(blank=True, null=True)

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

    # CRAWLER TYPE ############################################################
    CRAWLER_TYPE = [
        ('static_page', 'Static Page'),
        ('form_page', 'Page with Form'),
        ('single_file', 'Single File'),
        ('bundle_file', 'Bundle File'),
    ]
    crawler_type = models.CharField(
        max_length=15, choices=CRAWLER_TYPE, default='static_page')
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
    download_files_check_type = models.BooleanField(blank=True, null=True)
    download_files_process_value = models.TextField(
        max_length=1000, blank=True, null=True
    )


    download_imgs = models.BooleanField(default=False)

    wait_crawler_finish_to_download = models.BooleanField(default=False)
    time_between_downloads = models.IntegerField(blank=True, null=True)

    steps = models.CharField(
        blank=True, null=True, max_length=9999999, default='{}')

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

        if config["data_path"] is None:
            config["data_path"] = CURR_FOLDER_FROM_ROOT
        else:
            if config["data_path"][-1] == "/":
                config["data_path"] = config["data_path"][:-1]
            else:
                config["data_path"] = config["data_path"]

        # Include information on parameter handling
        parameter_handlers = []
        for param in crawler.parameter_handlers.values():
            del param['id']
            del param['crawler_id']

            # Convert Date parameters into iso string for serialization into
            # JSON
            if param['end_date_date_param'] is not None:
                iso_str = param['start_date_date_param'].isoformat()
                param['start_date_date_param'] = iso_str
            if param['end_date_date_param'] is not None:
                iso_str = param['end_date_date_param'].isoformat()
                param['end_date_date_param'] = iso_str

            parameter_handlers.append(param)

        # Include information on response handling for Templated URLs
        response_handlers = []
        for resp in crawler.response_handlers.values():
            del resp['id']
            del resp['crawler_id']
            response_handlers.append(resp)

        config['templated_url_response_handlers'] = response_handlers
        config['parameter_handlers'] = parameter_handlers
        return config

    # PARSING #########################################################
    save_csv = models.BooleanField(blank=True, null=True)
    table_attrs = models.CharField(max_length=20000, blank=True, null=True)


    @property
    def running(self):
        return self.instances.filter(running=True).exists()

    @property
    def running_instance(self):
        inst_query = self.instances.filter(running=True)
        if inst_query.exists():
            return inst_query.get()
        return None

    def __str__(self):
        return self.source_name


class ParameterHandler(models.Model):
    """
    Details on how to handle a parameter to be injected
    """

    LIST_REGEX = '^(\\s*[0-9]+\\s*,)*\\s*[0-9]+\\s*$'
    list_validator = RegexValidator(LIST_REGEX, ('Insira uma lista de números '
                                                 'separados por vírgula.'))

    # Crawler to which this handler is associated
    crawler = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                related_name="parameter_handlers")

    # Parameter key for request contents
    parameter_key = models.CharField(max_length=1000, blank=True)

    # Whether or not to filter the range for this parameter
    filter_range = models.BooleanField(default=False)
    # Number of consecutive entries to search during "binary search" if
    # parameter should be range-filtered
    cons_misses = models.PositiveIntegerField(null=True, blank=True)

    # Parameter configuration
    PARAM_TYPES = [
        ('process_code', 'Código de processo'),
        ('number_seq', 'Sequência numérica'),
        ('date_seq', 'Sequência de datas'),
        ('alpha_seq', 'Sequência alfabética'),
    ]

    parameter_type = models.CharField(max_length=15,
                                      choices=PARAM_TYPES,
                                      default='none')

    # Process code param
    first_year_proc_param = models.PositiveIntegerField(null=True, blank=True)
    last_year_proc_param = models.PositiveIntegerField(null=True, blank=True)
    segment_ids_proc_param = models.CharField(max_length=1000, blank=True,
                                              validators=[list_validator])
    court_ids_proc_param = models.CharField(max_length=1000, blank=True,
                                            validators=[list_validator])
    origin_ids_proc_param = models.CharField(max_length=1000, blank=True,
                                             validators=[list_validator])

    # Numeric param
    first_num_param = models.IntegerField(null=True, blank=True)
    last_num_param = models.IntegerField(null=True, blank=True)
    step_num_param = models.IntegerField(null=True, blank=True)
    leading_num_param = models.BooleanField(default=False)

    # Alphabetic string param
    length_alpha_param = models.PositiveIntegerField(null=True, blank=True)
    num_words_alpha_param = models.PositiveIntegerField(null=True, blank=True)
    no_upper_alpha_param = models.BooleanField(default=False)

    # Date param
    DATE_FREQ = [
        ('Y', 'Anual'),
        ('M', 'Mensal'),
        ('D', 'Diária'),
    ]
    date_format_date_param = models.CharField(max_length=1000, blank=True)
    start_date_date_param = models.DateField(null=True, blank=True)
    end_date_date_param = models.DateField(null=True, blank=True)
    frequency_date_param = models.CharField(max_length=15,
                                 choices=DATE_FREQ,
                                 default='D')


class ResponseHandler(models.Model):
    """
    Details on how to handle a response to a request
    """

    # Crawler to which this handler is associated
    crawler = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                related_name="response_handlers")

    HANDLER_TYPES = [
        ('text', 'Texto na página'),
        ('http_status', 'Código de status HTTP'),
        ('binary', 'Arquivo de tipo binário'),
    ]
    handler_type = models.CharField(max_length=15, choices=HANDLER_TYPES)
    text_match_value = models.CharField(max_length=1000, blank=True)
    http_status = models.PositiveIntegerField(null=True, blank=True)
    opposite = models.BooleanField(default=False)


class CrawlerInstance(TimeStamped):
    crawler_id = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                   related_name='instances')
    instance_id = models.BigIntegerField(primary_key=True)
    running = models.BooleanField()


class DownloadDetail(TimeStamped):
    """
    Details about file downloads requested by crawlers.
    """
    STATUS = [
        ('DOWNLOADING', 'DOWNLOADING'),
        ('WAITING', 'WAITING'),
        ('DONE', 'DONE'),
        ('ERROR', 'ERROR')
    ]
    status = models.CharField(
        max_length=20, choices=STATUS, default="WAITING")
    description = models.CharField(max_length=1000, blank=True)
    size = models.PositiveIntegerField(null=True, blank=True)
    progress = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.CharField(max_length=1000, null=True, blank=True)
