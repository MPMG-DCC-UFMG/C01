from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator




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

    # BASIC INFO ####################################################################
    source_name = models.CharField(max_length=200)
    base_url = models.CharField(max_length=200)
    obey_robots = models.BooleanField(blank=True, null=True)
    pathValid = RegexValidator(r'^[0-9a-zA-Z\/\\-_]*$', 'This is not a valid path.')
    data_path = models.CharField(max_length=2000, blank=True, null=True, validators=[pathValid])

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
    antiblock_mask_type = models.CharField(max_length=15, choices=ANTIBLOCK_MASK_TYPE,
                                           blank=True, null=True, default='none')

    # Options for IP rotation
    IP_TYPE = [
        ('tor', 'Tor'),
        ('proxy', 'Proxy'),
    ]
    antiblock_ip_rotation_type = models.CharField(max_length=15, choices=IP_TYPE, null=True, blank=True)
    antiblock_proxy_list = models.CharField(max_length=2000, blank=True, null=True)  # available for Proxy List
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
    link_extractor_max_depth = models.IntegerField(blank=True, null=True)
    link_extractor_allow = models.CharField(max_length=1000, blank=True, null=True)
    link_extractor_allow_extensions = models.CharField(blank=True, null=True, max_length=2000)

    # TEMPLATED URL ###################################################################
    TEMPLATED_URL_TYPE = [
        ('none', 'None'),
        ('get', 'GET'),
        ('post', 'POST'),
    ]
    # GET case
    templated_url_type = models.CharField(max_length=15, choices=TEMPLATED_URL_TYPE, default='none')
    formatable_url = models.CharField(max_length=200, blank=True, null=True)
    param = models.CharField(max_length=200, blank=True, null=True)

    # POST case
    post_dictionary = models.CharField(max_length=1000, blank=True, null=True)

    # PROBING #########################################################################
    http_status_response = models.CharField(max_length=15, blank=True, null=True)
    invert_http_status = models.BooleanField(blank=True, null=True)
    text_match_response = models.CharField(max_length=2000, blank=True, null=True)
    invert_text_match = models.BooleanField(blank=True, null=True)

    # PARSING #########################################################################
    save_csv = models.BooleanField(blank=True, null=True)


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


class CrawlerInstance(TimeStamped):
    crawler_id = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, related_name='instances')
    instance_id = models.BigIntegerField(primary_key=True)
    running = models.BooleanField()
