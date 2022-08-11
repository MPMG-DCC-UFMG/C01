import datetime
from typing import List, Union

from crawler_manager.constants import *
from crawling_utils.constants import (AUTO_ENCODE_DETECTION,
                                      HEADER_ENCODE_DETECTION)
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.base import ModelBase
from django.utils import timezone
from typing_extensions import Literal, TypedDict

CRAWLER_QUEUE_DB_ID = 1


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
        on_queue = CrawlerQueueItem.objects.filter(crawl_request_id=self.pk).exists()
        if on_queue:
            return not CrawlerQueueItem.objects.get(crawl_request_id=self.pk).running
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

    value_list_param = models.CharField(max_length=50000, blank=True)


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
    crawler = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                related_name='instances')
    instance_id = models.BigIntegerField(primary_key=True)

    number_files_found = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_files_success_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_files_error_download = models.PositiveIntegerField(default=0, null=True, blank=True)

    number_pages_found = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_success_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_error_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_duplicated_download = models.PositiveIntegerField(default=0, null=True, blank=True)

    page_crawling_finished = models.BooleanField(default=False, null=True, blank=True)

    running = models.BooleanField()
    num_data_files = models.IntegerField(default=0)
    data_size_kbytes = models.BigIntegerField(default=0)

    @property
    def duration_seconds(self):
        if self.creation_date == None or self.last_modified == None:
            return 0

        start_timestamp = datetime.datetime.timestamp(self.creation_date)
        end_timestamp = datetime.datetime.timestamp(self.last_modified)

        return end_timestamp - start_timestamp

    @property
    def duration_readable(self):
        final_str = ''
        str_duration = str(datetime.timedelta(seconds=self.duration_seconds))
        if 'day' in str_duration:
            parts = str_duration.split(',')
            final_str += parts[0].replace('day', 'dia')
            parts = parts[1].split(':')
            hours = int(parts[0])
            if hours > 0:
                final_str += ' ' + str(hours) + 'h'
        else:
            parts = str_duration.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(float(parts[2]))
            if hours > 0:
                final_str += str(hours) + 'h'
                if minutes > 0:
                    final_str += ' ' + str(minutes) + 'min'
            elif minutes > 0:
                final_str += str(minutes) + 'min'
                if seconds > 0:
                    final_str += ' ' + str(seconds) + 's'
            else:
                final_str += str(seconds) + 's'

        return final_str

    @property
    def data_size_readable(self):
        size = self.data_size_kbytes
        for unit in ['kb', 'mb', 'gb', 'tb']:
            if size < 1000.0:
                break
            size /= 1000.0
        return f"{size:.{2}f}{unit}"


    def download_files_finished(self):
        return self.number_files_success_download + self.number_files_error_download == self.number_files_found


class Log(TimeStamped):
    instance = models.ForeignKey(CrawlerInstance, on_delete=models.CASCADE,
                                 related_name="log")
    log_message = models.TextField(blank=True, null=True)
    logger_name = models.CharField(max_length=50, blank=True, null=True)
    log_level = models.CharField(max_length=10, blank=True, null=True)
    raw_log = models.TextField(blank=True, null=True)


class CrawlerQueue(models.Model):
    max_fast_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)
    max_medium_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)
    max_slow_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)

    @classmethod
    def object(cls: ModelBase):
        if cls._default_manager.all().count() == 0:
            crawler_queue = CrawlerQueue.objects.create(id=CRAWLER_QUEUE_DB_ID)
            crawler_queue.save()

        return CrawlerQueue.objects.get(id=CRAWLER_QUEUE_DB_ID)

    @classmethod
    def to_dict(cls: ModelBase) -> dict:
        crawler_queue = CrawlerQueue.object()

        queue_items = list()
        for queue_item in crawler_queue.items.all():
            queue_items.append({
                'id': queue_item.id,
                'creation_date': round(queue_item.creation_date.timestamp() * 1000),
                'last_modified': round(queue_item.last_modified.timestamp() * 1000),
                'crawler_id': queue_item.crawl_request.id,
                'crawler_name': queue_item.crawl_request.source_name,
                'queue_type': queue_item.queue_type,
                'position': queue_item.position,
                'forced_execution': queue_item.forced_execution,
                'running': queue_item.running
            })

        data = {
            'max_fast_runtime_crawlers_running': crawler_queue.max_fast_runtime_crawlers_running,
            'max_medium_runtime_crawlers_running': crawler_queue.max_medium_runtime_crawlers_running,
            'max_slow_runtime_crawlers_running': crawler_queue.max_slow_runtime_crawlers_running,
            'items': queue_items
        }

        return data

    def num_crawlers_running(self, queue_type: str) -> int:
        return self.items.filter(queue_type=queue_type, running=True).count()

    def num_crawlers(self) -> int:
        return self.items.all().count()

    def __get_next(self, queue_type: str, max_crawlers_running: int, source_queue: str = None):
        next_crawlers = list()

        # um coletor irá executar na fila que não seria a sua. Como no caso onde
        # a fila de coletores lentos em execução está vazia e ele pode alocar para executar
        # coletores médios e curtos
        if source_queue:
            num_crawlers_running = self.num_crawlers_running(source_queue)

        else:
            num_crawlers_running = self.num_crawlers_running(queue_type)

        if num_crawlers_running >= max_crawlers_running:
            return next_crawlers

        candidates = self.items.filter(queue_type=queue_type, running=False).order_by('position').values()
        limit = max(0, max_crawlers_running - num_crawlers_running)

        return [(e['id'], e['crawl_request_id']) for e in candidates[:limit]]

    def get_next(self, queue_type: str):
        next_crawlers = list()
        has_items_from_another_queue = False

        if queue_type == 'fast':
            next_crawlers = self.__get_next('fast', self.max_fast_runtime_crawlers_running)

        elif queue_type == 'medium':
            next_crawlers = self.__get_next('medium', self.max_medium_runtime_crawlers_running)

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_medium_runtime_crawlers_running:
                fast_next_crawlers = self.__get_next(
                    'fast', self.max_medium_runtime_crawlers_running - len(next_crawlers), 'medium')
                next_crawlers.extend(fast_next_crawlers)
                has_items_from_another_queue = True

        elif queue_type == 'slow':
            next_crawlers = self.__get_next('slow', self.max_slow_runtime_crawlers_running)

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_slow_runtime_crawlers_running:
                medium_next_crawlers = self.__get_next(
                    'medium', self.max_slow_runtime_crawlers_running - len(next_crawlers), 'slow')
                next_crawlers.extend(medium_next_crawlers)
                has_items_from_another_queue = True

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_slow_runtime_crawlers_running:
                fast_next_crawlers = self.__get_next(
                    'fast', self.max_slow_runtime_crawlers_running - len(next_crawlers), 'slow')
                next_crawlers.extend(fast_next_crawlers)
                has_items_from_another_queue = True

        else:
            raise ValueError('Queue type must be fast, medium or slow.')

        return has_items_from_another_queue, next_crawlers


    def save(self, *args, **kwargs):
        self.pk = self.id = 1
        return super().save(*args, **kwargs)


class CrawlerQueueItem(TimeStamped):
    queue = models.ForeignKey(CrawlerQueue, on_delete=models.CASCADE, default=1, related_name='items')
    queue_type = models.CharField(max_length=8, default="medium")
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, unique=True)
    forced_execution = models.BooleanField(default=False)
    running = models.BooleanField(default=False, blank=True)
    position = models.PositiveIntegerField(null=False, default=1)

class Finish(TypedDict):
    '''Define qual parâmetro para parar de reagendar uma coleta, a saber:
        - never: o coletor é reagendado para sempre.
        - occurrence: o coletor é colocado para executar novamente <occurrence> vezes.
        - date: O coletor é colocado para executar até a data <date> 
    '''
    type: Literal['never','occurrence', 'date']
    additional_data: Union[None, int]

class MonthlyRepetitionConf(TypedDict):
    ''' Caso a repetição personalizado seja por mês, o usuário pode escolher 3 tipos de agendamento mensal:
        - first-weekday: A coleta ocorre no primeiro dia <first-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - last-weekday: A coleta ocorre no último dia <last-weekday> (domingo, segunda, etc) da semana do mês, contado a partir de 0 - domingo.
        - day-x: A coleta ocorre no dia x do mês. Se o mês não tiver o dia x, ocorrerá no último dia do mês.
    '''
    type: Literal['first-weekday', 'last-weekday', 'day-x']

    # Se <type> [first,last]-weekday, indica qual dia semana a coleta deverá ocorrer, contado a partir de 0 - domingo.
    # Se <type> day-x, o dia do mês que a coleta deverá ocorrer.
    value: int 

class PersonalizedRepetionMode(TypedDict):
    #Uma repetição personalizada pode ser por dia, semana, mês ou ano.    
    type: Literal['daily', 'weekly', 'monthly', 'yearly']

    # de quanto em quanto intervalo de tempo <type> a coleta irá ocorrer
    interval: int 

    ''' Dados extras que dependem do tipo da repetição. A saber, se <type> é:
        - daily: additional_data receberá null
        - weekly: additional_data será uma lista com dias da semana (iniciados em 0 - domingo)
                    para quais dias semana a coleta irá executar.
        - monthly: Ver classe MonthlyRepetitionConf.
        - yearly: additional_data receberá null
    '''
    additional_data: Union[None, List, MonthlyRepetitionConf]
    
    # Define até quando o coletor deve ser reagendado. Ver classe Finish.
    finish: Finish 

class TaskType(TypedDict):
    id: int
    crawl_request: int 
    runtime: str 
    crawler_queue_behavior: Literal['wait_on_last_queue_position', 'wait_on_first_queue_position', 'run_immediately'] 
    repeat_mode: Literal['no_repeat', 'daily', 'weekly', 'monthly', 'yearly', 'personalized']
    personalized_repetition_mode: Union[None, PersonalizedRepetionMode]

class Task(TimeStamped):
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, related_name='scheduler_jobs')

    # data e horário base para começar o agendamento de coletas
    runtime = models.DateTimeField()
    
    CRAWLER_QUEUE_BEHAVIOR_CHOICES = [
        ('wait_on_last_queue_position', 'Esperar na última posição da fila'),
        ('wait_on_first_queue_position', 'Esperar na primeira posição da fila'),
        ('run_immediately', 'Executar imediatamente'),
        
    ] 

    # O que o agendador deve fazer com o coletor ao inserí-lo na fila de coletas.
    crawler_queue_behavior = models.CharField(max_length=32, choices=CRAWLER_QUEUE_BEHAVIOR_CHOICES, default='wait_on_last_queue_position')

    REPETITION_MODE_CHOICES = [ 
        ('no_repeat', 'Não se repete'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensalmente'),
        ('yearly', 'Anual'),
        ('personalized', 'Personalizado')
    ]

    # modo de repetição da coleta agendada.
    repeat_mode = models.CharField(max_length=32, choices=REPETITION_MODE_CHOICES, default='no_repeat')

    # json com a configuração personalizada de reexecução do coletor
    personalized_repetition_mode: PersonalizedRepetionMode = models.JSONField(null=True, blank=True)
