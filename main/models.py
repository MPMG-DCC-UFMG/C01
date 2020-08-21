from django.db import models
from django.utils import timezone

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


class RequestConfiguration(models.Model):
    """
    Defines the fields required to configure the request process for an URL.
    This includes response handlers, parameter injection methods and range
    inference mechanisms
    """
    PARAM_TYPES = [
        ('none', 'No parameter'),
        ('formatted_str', 'Formatted code'),
        ('number_seq', 'Number sequence'),
        ('date_seq', 'Date sequence'),
        ('alpha_seq', 'Alphabetic sequence'),
    ]

    template_parameter_type = models.CharField(max_length=15,
                                               choices=PARAM_TYPES,
                                               default='none')

    # Numeric param
    first_num_param = models.IntegerField(null=True, blank=True)
    last_num_param = models.IntegerField(null=True, blank=True)
    step_num_param = models.IntegerField(null=True, blank=True)
    leading_num_param = models.BooleanField(default=False)
    # Alphabetic string param
    length_alpha_param = models.IntegerField(null=True, blank=True)
    num_words_alpha_param = models.IntegerField(null=True, blank=True)
    no_upper_alpha_param = models.BooleanField(default=False)
    # Date param
    date_format_date_param = models.CharField(max_length=1000, blank=True)
    start_date_date_param = models.DateField(null=True, blank=True)
    end_date_date_param = models.DateField(null=True, blank=True)
    DATE_FREQ = [
        ('Y', 'Yearly'),
        ('M', 'Monthly'),
        ('D', 'Daily'),
    ]
    frequency_date_param = models.CharField(max_length=15,
                                 choices=PARAM_TYPES,
                                 default='D')

    # POST case
    post_key = models.CharField(max_length=100, blank=True)
    post_dictionary = models.CharField(max_length=1000, blank=True, default="")


class CrawlRequest(TimeStamped):
    
    running = models.BooleanField(default=False)
    
    # BASIC INFO ####################################################################
    source_name = models.CharField(max_length=200)
    base_url  = models.CharField(max_length=200)
    obey_robots = models.BooleanField(blank=True, null=True)

    REQUEST_TYPES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
    ]
    request_type = models.CharField(max_length=15,
                                    choices=REQUEST_TYPES,
                                    default='GET')

    # ANTIBLOCK #####################################################################
    # Options for Delay
    antiblock_download_delay = models.IntegerField(blank=True, null=True)
    antiblock_autothrottle_enabled = models.BooleanField(blank=True, null=True)
    antiblock_autothrottle_start_delay = models.IntegerField(blank=True, null=True)
    antiblock_autothrottle_max_delay = models.IntegerField(blank=True, null=True)

    # Options for antiblock masks
    ANTIBLOCK_MASK_TYPE = [
        ('none', 'None'),
        ('ip', 'IP rotation'),
        ('user_agent', 'User-agent rotation'),
        ('cookies', 'Use cookies'),
    ]
    antiblock_mask_type = models.CharField(max_length=15, choices=ANTIBLOCK_MASK_TYPE, blank=True, null=True, default='none')
    
        # Options for IP rotation
    IP_TYPE = [
        ('tor', 'Tor'),
        ('proxy', 'Proxy'),
    ]
    antiblock_ip_rotation_type = models.CharField(max_length=15, choices=IP_TYPE, null=True, blank=True)
    antiblock_proxy_list = models.CharField(max_length=2000, blank=True, null=True) # available for Proxy List
    antiblock_max_reqs_per_ip = models.IntegerField(blank=True, null=True)
    antiblock_max_reuse_rounds = models.IntegerField(blank=True, null=True)

        # Options for User Agent rotation 
    antiblock_reqs_per_user_agent = models.IntegerField(blank=True, null=True)
    antiblock_user_agents_file = models.CharField(max_length=2000, blank=True, null=True)

        # Options for Cookies
    antiblock_cookies_file = models.CharField(max_length=2000, blank=True, null=True)
    antiblock_persist_cookies = models.BooleanField(blank=True, null=True)

    # CAPTCHA #######################################################################
    CAPTCHA_TYPE = [
        ('none', 'None'), 
        ('image', 'Image'),
        ('sound', 'Sound'),
    ]
    captcha = models.CharField(max_length=15, choices=CAPTCHA_TYPE, default='none')
    has_webdriver = models.BooleanField(blank=True, null=True)
    webdriver_path = models.CharField(max_length=1000, blank=True, null=True)
    # Options for captcha
        # Options for image
    img_xpath = models.CharField(max_length=100, blank=True, null=True)
        # Options for sound
    sound_xpath = models.CharField(max_length=100, blank=True, null=True)

    # CRAWLER TYPE ###################################################################
    CRAWLER_TYPE = [
        ('static_page', 'Static Page'), 
        ('form_page', 'Page with Form'),
        ('single_file', 'Single File'),
        ('bundle_file', 'Bundle File'),
    ]
    crawler_type = models.CharField(max_length=15, choices=CRAWLER_TYPE, default='static_page')
    explore_links = models.BooleanField(blank=True, null=True)
    link_extractor_max_depht = models.IntegerField(blank=True, null=True)
    link_extractor_allow = models.CharField(max_length=1000, blank=True, null=True)
    link_extractor_allow_extensions = models.CharField(blank=True, null=True, max_length=2000)

    probing_config = models.ForeignKey(RequestConfiguration,
        on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.source_name


class ResponseHandler(models.Model):
    """Details on how to handle a response during probing"""

    # Configuration to which this handler is associated
    config = models.ForeignKey(RequestConfiguration, on_delete=models.CASCADE,
                                related_name="response_handlers")

    HANDLER_TYPES = [
        ('text', 'Text match'),
        ('http_status', 'HTTP status code'),
        ('binary', 'Binary file type'),
    ]
    handler_type = models.CharField(max_length=15, choices=HANDLER_TYPES)
    text_match_value = models.CharField(max_length=1000, blank=True)
    http_status = models.PositiveIntegerField(null=True, blank=True)
    opposite = models.BooleanField(default=False)


class CrawlerInstance(TimeStamped):
    crawler_id = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE)
    instance_id = models.BigIntegerField(primary_key=True)
    running = models.BooleanField()
