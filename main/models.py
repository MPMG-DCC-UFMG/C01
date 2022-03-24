from statistics import mode
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
    base_url = models.TextField()
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
    form_request_type = models.CharField(max_length=15,
                                    choices=REQUEST_TYPES,
                                    default='POST')

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

    # ENCODING DETECTION =======================================================
    HEADER_ENCODE_DETECTION = 1
    AUTO_ENCODE_DETECTION = 2

    ENCODE_DETECTION_CHOICES = [
        (HEADER_ENCODE_DETECTION, 'Via cabeçalho da resposta'),
        (AUTO_ENCODE_DETECTION, 'Automático'),
    ]

    encoding_detection_method = models.IntegerField(choices=ENCODE_DETECTION_CHOICES, default=HEADER_ENCODE_DETECTION)

    @staticmethod
    def process_parameter_data(param_list):
        """
        Processes the parameter data turning it into a format recognizable by
        the spider, while also separating Templated URL and Static Form params

        :param param_list: list of parameters (as specified in the
                           ParameterHandler model)

        :returns: tuple of parameter lists, for the Templated URLs and Static
                  Forms, respectively
        """
        url_parameter_handlers = []
        form_parameter_handlers = []
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

            if param['injection_type'] == 'templated_url':
                url_parameter_handlers.append(param)
            elif param['injection_type'] == 'static_form':
                form_parameter_handlers.append(param)

        return url_parameter_handlers, form_parameter_handlers


    @staticmethod
    def process_response_data(resp_list):
        """
        Processes the response handler data turning it into a format
        recognizable by the spider, while also separating Templated URL and
        Static Form response handlers

        :param resp_list: list of response handlers (as specified in the
                          ResponseHandler model)

        :returns: tuple of response handler lists, for the Templated URLs and
                  Static Forms, respectively
        """
        url_response_handlers = []
        form_response_handlers = []
        for resp in resp_list:
            if 'id' in resp:
                del resp['id']
            if 'crawler_id' in resp:
                del resp['crawler_id']

            if resp['injection_type'] == 'templated_url':
                url_response_handlers.append(resp)
            elif resp['injection_type'] == 'static_form':
                form_response_handlers.append(resp)

        return url_response_handlers, form_response_handlers


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
        param_list = crawler.parameter_handlers.values()
        parameter_handlers = CrawlRequest.process_parameter_data(param_list)
        config['templated_url_parameter_handlers'] = parameter_handlers[0]
        config['static_form_parameter_handlers'] = parameter_handlers[1]

        # Include information on response handling
        resp_list = crawler.response_handlers.values()
        response_handlers = CrawlRequest.process_response_data(resp_list)
        config['templated_url_response_handlers'] = response_handlers[0]
        config['static_form_response_handlers'] = response_handlers[1]

        return config

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

    # Specify if this is a URL or form parameter
    INJECTION_TYPES = [
        ('templated_url', 'Templated URL'),
        ('static_form', 'Static Form'),
    ]
    injection_type = models.CharField(max_length=15,
                                      choices=INJECTION_TYPES,
                                      default='none')

    # Parameter key and label for form parameters
    parameter_key = models.CharField(max_length=1000, blank=True)
    parameter_label = models.CharField(max_length=1000, blank=True)

    # Whether or not to filter the range for this parameter
    filter_range = models.BooleanField(default=False)
    # Number of consecutive entries to search during "binary search" if
    # parameter should be range-filtered
    cons_misses = models.PositiveIntegerField(null=True, blank=True)

    # Parameter configuration
    PARAM_TYPES = [
        ('number_seq', 'Sequência numérica'),
        ('date_seq', 'Sequência de datas'),
        ('alpha_seq', 'Sequência alfabética'),
        ('process_code', 'Código de processo'),
        ('value_list', 'Lista pré-definida'),
        ('const_value', 'Valor constante'),
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

    value_const_param = models.CharField(max_length=5000, blank=True)
    value_list_param = models.CharField(max_length=50000, blank=True)


class ResponseHandler(models.Model):
    """
    Details on how to handle a response to a request
    """

    # Crawler to which this handler is associated
    crawler = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                related_name="response_handlers")

    # Specify if this is a URL or form validation
    INJECTION_TYPES = [
        ('templated_url', 'Templated URL'),
        ('static_form', 'Static Form'),
    ]
    injection_type = models.CharField(max_length=15,
                                      choices=INJECTION_TYPES,
                                      default='none')

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

class CrawlerQueue(models.Model):
    max_crawlers_running = models.PositiveIntegerField(default=5, blank=True)

    @classmethod
    def object(cls):
        if cls._default_manager.all().count() == 0:
            CrawlerQueue().save()

        return cls._default_manager.all().first()

    def num_crawlers_running(self):
        return self.items.filter(running=True).count()

    def num_crawlers(self):
        return self.items.all().count()

    def get_next(self):
        next_crawlers = list()
       
        if self.num_crawlers_running >= self.max_crawlers_running:
            return next_crawlers
        
        candidates = self.items.filter(running=True).values()
        return candidates
        

    def save(self, *args, **kwargs):
        self.pk = self.id = 1
        return super().save(*args, **kwargs)

class CrawlerQueueItem(TimeStamped):
    queue = models.ForeignKey(CrawlerQueue, on_delete=models.CASCADE, default=1, related_name='items')
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE)
    running = models.BooleanField(default=False, blank=True)