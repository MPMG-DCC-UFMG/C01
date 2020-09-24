from django import forms
from .models import CrawlRequest
from django.core.validators import RegexValidator



class CrawlRequestForm(forms.ModelForm):
    class Meta:
        model = CrawlRequest
        """

        obey_robots = forms.BooleanField(required=False)

        # Options for antiblock
        antiblock_download_delay = forms.IntegerField(required=False)
        antiblock_autothrottle_enabled = forms.BooleanField(required=False)
        antiblock_autothrottle_start_delay = forms.IntegerField(required=False)
        antiblock_autothrottle_max_delay = forms.IntegerField(required=False)
        antiblock_mask_type = forms.ChoiceField(required=False)
        antiblock_ip_rotation_type = forms.ChoiceField(required=False)
        antiblock_proxy_list = forms.CharField(required=False)
        antiblock_max_reqs_per_ip = forms.IntegerField(required=False)
        antiblock_max_reuse_rounds = forms.IntegerField(required=False)
        antiblock_reqs_per_user_agent = forms.IntegerField(required=False)
        antiblock_user_agents_file = forms.CharField(required=False)
        antiblock_cookies_file = forms.CharField(required=False)
        antiblock_persist_cookies = forms.BooleanField(required=False)

        # Options for Captcha
        has_webdriver = forms.BooleanField(required=False)
        webdriver_path = forms.CharField(required=False)
        img_xpath = forms.CharField(required=False)
        sound_xpath = forms.CharField(required=False)

        # Crawler type
        crawler_type = forms.CharField(required=False)

        # Crawler type - Static
        explore_links = forms.BooleanField(required=False)
        link_extractor_max_depth = forms.IntegerField(required=False)
        link_extractor_allow = forms.CharField(required=False)
        # link_extractor_allow_domains =
        link_extractor_allow_extensions = forms.CharField(required=False)
        formatable_url = forms.CharField(required=False)
        post_dictionary = forms.CharField(required=False)

        http_status_response = forms.CharField(required=False)
        invert_http_status = forms.BooleanField(required=False)
        text_match_response = forms.CharField(required=False)
        invert_text_match = forms.BooleanField(required=False)
        """

        output_filename = forms.CharField(required=False)
        save_csv = forms.BooleanField(required=False)

        fields = [
            'source_name',
            'base_url',
            'obey_robots',
            'captcha',

            'antiblock_download_delay',
            'antiblock_autothrottle_enabled',
            'antiblock_autothrottle_start_delay',
            'antiblock_autothrottle_max_delay',
            'antiblock_mask_type',
            'antiblock_ip_rotation_type',
            'antiblock_max_reqs_per_ip',
            'antiblock_max_reuse_rounds',
            'antiblock_proxy_list',
            'antiblock_reqs_per_user_agent',
            'antiblock_user_agents_file',
            'antiblock_cookies_file',
            'antiblock_persist_cookies',

            'has_webdriver',
            'webdriver_path',
            'img_xpath',
            'sound_xpath',
            'crawler_type',
            'explore_links',
            'link_extractor_max_depth',
            'link_extractor_allow',
            'link_extractor_allow_extensions',
            'templated_url_type',
            'formatable_url',
            'post_dictionary',
            'http_status_response',
            'invert_http_status',
            'text_match_response',
            'invert_text_match',
            'save_csv',
            'output_path',
            'table_attrs',
        ]

        widgets ={'table_attrs': forms.HiddenInput()}


class RawCrawlRequestForm(CrawlRequestForm):

    # BASIC INFO #########################################################################
    source_name = forms.CharField(label="Source Name", max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Example'})
    )
    base_url = forms.CharField(label="Base URL", max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'www.example.com/data/'})
                               )
    obey_robots = forms.BooleanField(required=False, label="Obey robots.txt")

    output_path = forms.CharField(
        required=False, max_length=2000, label="Path to save the files",
        widget=forms.TextInput(attrs={'placeholder': '/home/user/Documents'}),
        validators=[CrawlRequest.pathValid]
    )
    
    # ANTIBLOCK ##########################################################################
    # Options for Delay
    antiblock_download_delay = forms.IntegerField(
        required=False,
        label="Average delay in Seconds (or min delay if autothrottle is on).",
        initial=2,
    )
    antiblock_autothrottle_enabled = forms.BooleanField(
        required=False,
        label="Enable autothrottle",

        widget=forms.CheckboxInput(
            attrs={
                "onclick": "autothrottleEnabled();",
            }
        )
    )
    antiblock_autothrottle_start_delay = forms.IntegerField(
        required=False,
        label="Starting delay",
        initial=2,
    )
    antiblock_autothrottle_max_delay = forms.IntegerField(
        required=False,
        label="Max delay",
        initial=10,
    )

    # Options for mask type
    antiblock_mask_type = forms.ChoiceField(
        required=False, choices=(
            ('none', 'None'),
            # ('ip', 'IP rotation'),
            # ('user_agent', 'User-agent rotation'),
            # ('delay', 'Delays'),
            # ('cookies', 'Use cookies'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailAntiblock();'})
    )

    # Options for IP rotation
    antiblock_ip_rotation_type = forms.ChoiceField(
        required=False, choices=(
            ('tor', 'Tor'),
            ('proxy', 'Proxy'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailIpRotationType();'})
    )
    antiblock_proxy_list = forms.CharField(
        required=False, max_length=2000, label="Proxy List",
        widget=forms.TextInput(attrs={'placeholder': 'Paste here the content of your proxy list file'})
    )
    antiblock_max_reqs_per_ip = forms.IntegerField(
        required=False,
        label="Max Requisitions per IP",
        initial=10,
    )
    antiblock_max_reuse_rounds = forms.IntegerField(
        required=False,
        label="Max Reuse Rounds",
        initial=10,
    )

    # Options for User Agent rotation
    antiblock_reqs_per_user_agent = forms.IntegerField(required=False, label="Requests per User Agent")
    antiblock_user_agents_file = forms.CharField(
        required=False, max_length=2000, label="User Agents File",
        widget=forms.TextInput(attrs={'placeholder': 'Paste here the content of your user agents file'})
    )

    # Options for Cookies
    antiblock_cookies_file = forms.CharField(
        required=False, max_length=2000, label="Cookies File",
        widget=forms.TextInput(attrs={'placeholder': 'Paste here the content of your cookies file'})
    )
    antiblock_persist_cookies = forms.BooleanField(required=False, label="Persist Cookies")

    # CAPTCHA ############################################################################
    captcha = forms.ChoiceField(
        choices=(
            ('none', 'None'),
            ('image', 'Image'),
            ('sound', 'Sound'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCaptcha();'})
    )
    # Options for Captcha
    has_webdriver = forms.BooleanField(
        required=False, label="Use webdriver",
        widget=forms.CheckboxInput(attrs={'onchange': 'detailWebdriverType(); defineValid("captcha")'})
    )
    webdriver_path = forms.CharField(
        required=False, max_length=2000, label="Download directory",
        widget=forms.TextInput(attrs={'placeholder': 'Download directory path'}))
    img_xpath = forms.CharField(
        required=False, label="Image Xpath", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Image Xpath'})
    )
    sound_xpath = forms.CharField(
        required=False, label="Sound Xpath", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Sound Xpath'})
    )

    # CRAWLER TYPE ########################################################################
    crawler_type = forms.ChoiceField(
        required=False, choices=(
            ('static_page', 'Static Page'),
            # ('form_page', 'Page with Form'),
            # ('single_file', 'Single File'),
            # ('bundle_file', 'Bundle File'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCrawlerType();'})
    )
    explore_links = forms.BooleanField(required=False, label="Explore links")

    # Crawler Type - Static
    link_extractor_max_depth = forms.IntegerField(
        required=False, label="Link extractor max depth (blank to not limit):"
    )
    link_extractor_allow = forms.CharField(
        required=False, max_length=2000, label="Allow urls that match with the regex (blank to not filter):",
        widget=forms.TextInput(attrs={'placeholder': 'Regex for allowing urls'})
    )
    link_extractor_allow_extensions = forms.CharField(
        required=False, max_length=2000, label="List of allowed extensions (comma separed):",
        widget=forms.TextInput(attrs={'placeholder': 'pdf,xml'})
    )
    # Crawler Type - Page with form
    # Crawler Type - Single file
    # Crawler Type - Bundle file

    # TEMPLATED URL ########################################################################
    templated_url_type = forms.ChoiceField(
        required=False, choices=(
            ('none', 'None'),
            ('get', 'GET'),
            ('post', 'POST'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailTemplatedUrlRequestType();'})
    )
    # templated url - GET
    formatable_url = forms.CharField(
        required=False, max_length=2000, label="Formatable URL (format: example.com/param={})",
        widget=forms.TextInput(attrs={'placeholder': 'https://obraspublicas.com/IDOBRA={}'})
    )
    # param

    # templated url - POST
    post_dictionary = forms.CharField(
        required=False, max_length=2000, label="Dictionary of post params (format: {'name':value;})",
        widget=forms.TextInput(attrs={'placeholder': '{\'name1\': value1; \'name2\': value2}'})
    )

    # PROBING ##############################################################################
    http_status_response = forms.CharField(
        required=False, max_length=2000, label="HTTP status response",
        widget=forms.TextInput(attrs={'placeholder': '200'})
    )
    invert_http_status = forms.BooleanField(required=False, label="Opposite")
    text_match_response = forms.CharField(
        required=False, max_length=2000, label="Text match response",
        widget=forms.TextInput(attrs={'placeholder': 'Processo não encontrado'})
    )
    invert_text_match = forms.BooleanField(required=False, label="Opposite")

    # PARSING #############################################################################
    save_csv = forms.BooleanField(required=False, label="Save a CSV file")
    table_attrs = forms.CharField(
        required=False, max_length=2000, label="Motor de extração",
        widget = forms.HiddenInput(attrs={'id':'table_attrs_hidden'})
    )
    
