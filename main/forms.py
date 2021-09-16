from django import forms
from .models import CrawlRequest, ParameterHandler, ResponseHandler
from django.core.exceptions import ValidationError


class CrawlRequestForm(forms.ModelForm):
    class Meta:
        model = CrawlRequest

        labels = {
            'request_type': 'Método da requisição',
            'form_request_type': 'Método da requisição ao injetar em formulários',
        }

        fields = [
            'source_name',
            'base_url',
            'request_type',
            'form_request_type',
            'obey_robots',
            'captcha',

            'sc_scheduler_persist',
            'sc_scheduler_queue_refresh',
            'sc_queue_hits',
            'sc_queue_window',
            'sc_queue_moderated',
            'sc_dupefilter_timeout',
            'sc_global_page_per_domain_limit',
            'sc_global_page_per_domain_limit_timeout',
            'sc_domain_max_page_timeout',
            'sc_scheduler_ip_refresh',
            'sc_scheduler_backlog_blacklist',
            'sc_scheduler_type_enabled',
            'sc_scheduler_ip_enabled',
            'sc_scheduler_item_retries',
            'sc_scheduler_queue_timeout',
            'sc_httperror_allow_all',
            'sc_retry_times',
            'sc_download_timeout',

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
            'dynamic_processing',
            'explore_links',

            'link_extractor_max_depth',
            'link_extractor_allow_url',
            'link_extractor_allow_domains',
            'link_extractor_tags',
            'link_extractor_attrs',
            'link_extractor_check_type',
            'link_extractor_process_value',

            'download_files',
            'download_files_allow_url',
            'download_files_allow_domains',
            'download_files_tags',
            'download_files_attrs',
            'download_files_process_value',
            'download_files_allow_extensions',
            'download_files_check_large_content',

            'download_imgs',
            'steps',
            'data_path',

            'encoding_detection_method'
        ]

class RawCrawlRequestForm(CrawlRequestForm):

    # BASIC INFO ##############################################################
    source_name = forms.CharField(
        label="Nome do coletor", max_length=200,
        widget=forms.TextInput(
            attrs={'placeholder': 'Diário oficial do Município'})
    )
    base_url = forms.CharField(
        label="URL Base", max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'www.example.com/data/{}',
            'onchange': 'detailBaseUrl();'
        })
    )
    obey_robots = forms.BooleanField(
        required=False, label="Obedecer robots.txt")

    data_path = forms.CharField(
        required=False, max_length=2000, label="Caminho para salvar arquivos",
        widget=forms.TextInput(
            attrs={'placeholder': '/home/user/Documents/<crawler_name>'}),
        validators=[CrawlRequest.pathValid]
    )

    # SCRAPY CLUSTER ##########################################################

    # página de detalhes do coletor
    sc_scheduler_persist = forms.BooleanField(
        required=False, initial=True, label="Don't cleanup redis queues, allows to pause/resume crawls.", widget=forms.CheckboxInput())
    
    sc_scheduler_queue_refresh = forms.IntegerField(
        required=False, initial=10, label='Seconds to wait between seeing new queues, cannot be faster than spider_idle time of 5', min_value=5)
    
    sc_queue_moderated = forms.BooleanField(
        required=False, initial=True, label='We want the queue to produce a consistent pop flow')
    
    sc_dupefilter_timeout = forms.IntegerField(
        required=False, initial=600, label='How long we want the duplicate timeout queues to stick around in seconds')
    
    sc_httperror_allow_all = forms.BooleanField(
        required=False, initial=True, label='Allow all return codes')

    sc_retry_times = forms.IntegerField(required=False, initial=3, label='Retry times')

    sc_download_timeout = forms.IntegerField(required=False, initial=10, label='Download timeout')
    
    sc_queue_hits = forms.IntegerField(required=False, initial=10, label='Queue hits')

    sc_queue_window= forms.IntegerField(required=False, initial=60, label='Queue Windows')

    sc_scheduler_type_enabled = forms.BooleanField(required=False, initial=True, label='Scheduler type enabled')
    
    sc_scheduler_ip_enabled = forms.BooleanField(required=False, initial=True, label='Scheduler ip enabled')
    
    sc_global_page_per_domain_limit = forms.IntegerField(required=False, label='Global page per domain limit')
    
    sc_global_page_per_domain_limit_timeout = forms.IntegerField(required=False, initial=600, label='Global page per domain timeout')
    
    sc_domain_max_page_timeout = forms.IntegerField(required=False, initial=600, label='Domain max page timeout')
    
    sc_scheduler_ip_refresh = forms.IntegerField(required=False, initial=60, label='Scheduler ip refresh')
    
    sc_scheduler_backlog_blacklist = forms.BooleanField(required=False, initial=True, label='Scheduler backlog blacklist')
    
    sc_scheduler_item_retries = forms.IntegerField(required=False, initial=3, label='Scheduler item retries')
    
    sc_scheduler_queue_timeout = forms.IntegerField(required=False, initial=3600, label='Scheduler queue timeout')


    # ANTIBLOCK ###############################################################
    # Options for Delay
    antiblock_download_delay = forms.IntegerField(
        required=False,
        label=(
            "Intervalo médio em segundos (ou intervalo mínimo se "
            "auto ajuste está ligado)."
        ),
        initial=2,
    )
    antiblock_autothrottle_enabled = forms.BooleanField(
        required=False,
        label="Habilitar auto ajuste de intervalo",

        widget=forms.CheckboxInput(
            attrs={
                "onclick": "autothrottleEnabled();",
            }
        )
    )
    antiblock_autothrottle_start_delay = forms.IntegerField(
        required=False,
        label="Intervalo inicial",
        initial=2,
    )
    antiblock_autothrottle_max_delay = forms.IntegerField(
        required=False,
        label="Intervalo máximo",
        initial=10,
    )

    # Options for mask type
    antiblock_mask_type = forms.ChoiceField(
        required=False, choices=(
            ('none', 'None'),
            # ('ip', 'Rotação de IP'),
            # ('user_agent', 'Rotação de user-agent'),
            # ('delay', 'Intervalos entre requisições'),
            # ('cookies', 'Usar cookies'),
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
        widget=forms.TextInput(
            attrs={
                'placeholder': (
                    "Cole aqui o conteúdo do seu arquivo de lista"
                    " de proxies"
                )
            }
        )
    )
    antiblock_max_reqs_per_ip = forms.IntegerField(
        required=False,
        label="Máximo de requisições por IP",
        initial=10,
    )
    antiblock_max_reuse_rounds = forms.IntegerField(
        required=False,
        label="Máximo de vezes que um IP pode ser reusado",
        initial=10,
    )

    # Options for User Agent rotation
    antiblock_reqs_per_user_agent = forms.IntegerField(
        required=False, label="Requisições por user-agents"
    )
    antiblock_user_agents_file = forms.CharField(
        required=False, max_length=2000, label="Arquivo de User-Agents",
        widget=forms.TextInput(
            attrs={
                'placeholder': (
                    'Cole aqui o conteúdo do seu arquivo'
                    ' de user-agents'
                )
            }
        )
    )

    # Options for Cookies
    antiblock_cookies_file = forms.CharField(
        required=False, max_length=2000, label="Arquivo de cookies",
        widget=forms.TextInput(
            attrs={
                'placeholder': (
                    'Cole aqui o conteúdo do seu arquivo'
                    ' de cookies'
                )
            }
        )
    )
    antiblock_persist_cookies = forms.BooleanField(
        required=False, label="Manter cookies entre requisições")

    # CAPTCHA #################################################################
    captcha = forms.ChoiceField(
        choices=(
            ('none', 'Nenhum'),
            ('image', 'Imagem'),
            ('sound', 'Áudio'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCaptcha();'})
    )
    # Options for Captcha
    has_webdriver = forms.BooleanField(
        required=False, label="Usar webdriver",
        widget=forms.CheckboxInput(
            attrs={'onchange': 'detailWebdriverType(); defineValid("captcha")'}
        )
    )
    webdriver_path = forms.CharField(
        required=False, max_length=2000, label="Endereço para baixar",
        widget=forms.TextInput(
            attrs={'placeholder': 'Caminho para o diretório de donwload'})
    )
    img_xpath = forms.CharField(
        required=False, label="Xpath da imagem", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '//div/...'})
    )
    sound_xpath = forms.CharField(
        required=False, label="Xpath do áudio", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '//div/...'})
    )

    # CRAWLER TYPE ############################################################
    dynamic_processing = forms.BooleanField(
        required=False, label="Processamento dinâmico",
        widget=forms.CheckboxInput(
            attrs={'onchange': 'detailDynamicProcessing();'}
        )
    )

    explore_links = forms.BooleanField(required=False, label="Explorar links")

    # Crawler Type - Static
    link_extractor_max_depth = forms.IntegerField(
        required=False,
        label="Profundidade máxima do link (deixe em branco para não limitar):",
    )
    link_extractor_allow_url = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Permitir urls que casem com o regex:"
            " (deixe em branco para não filtrar)"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': 'Regex para permitir urls'})
    )
    link_extractor_allow_domains = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Permitir só urls dos domínios:"
            "(em branco para não filtrar) (separado por vírgula)"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': ''})
    )
    link_extractor_tags = forms.CharField(
        required=False, max_length=2000,
        label="Extrair links de tags do tipo: (separado por vírgula)",
        widget=forms.TextInput(
            attrs={'placeholder': 'a'})
    )
    link_extractor_attrs = forms.CharField(
        required=False, max_length=2000,
        label="Extrair urls dos atributos: (separado por vírgula)",
        widget=forms.TextInput(
            attrs={'placeholder': 'href'})
    )
    link_extractor_check_type = forms.BooleanField(
        required=False, label="Checar tipo da página")
    link_extractor_process_value = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Função python para processar os atributos: "
            "(A função será chamada como 'eval(func)(attr)')"
        ),
        widget=forms.Textarea(
            attrs={'placeholder': 'lambda x: x'})
    )

    download_files = forms.BooleanField(
        required=False, label="Baixar arquivos"
    )
    download_files_allow_url = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Baixar arquivos de url que casem com o regex:"
            " (deixe em branco para não filtrar)"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': 'Regex para permitir urls'})
    )
    download_files_allow_extensions = forms.CharField(
        required=False, max_length=2000,
        label="Extensões de arquivo permitidas (separado por vírgula):",
        widget=forms.TextInput(attrs={'placeholder': 'pdf,xml'})
    )
    download_files_allow_domains = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Permitir só urls dos domínios:"
            "(em branco para não filtrar) (separado por vírgula)"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': ''})
    )
    download_files_tags = forms.CharField(
        required=False, max_length=2000,
        label="Extrair links de tags do tipo: (separado por vírgula)",
        widget=forms.TextInput(
            attrs={'placeholder': 'a'})
    )
    download_files_attrs = forms.CharField(
        required=False, max_length=2000,
        label="Extrair urls dos atributos: (separado por vírgula)",
        widget=forms.TextInput(
            attrs={'placeholder': 'href'})
    )

    download_files_process_value = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Função python para processar os atributos: "
            "(A função será chamada como 'eval(func)(attr)')"
        ),
        widget=forms.Textarea(
            attrs={'placeholder': 'lambda x: x'})
    )

    download_files_check_large_content = forms.BooleanField(
        required=False, initial=True,
        label="Checar o tamanho dos arquivos a serem baixados")

    download_imgs = forms.BooleanField(
        required=False, label="Baixar imagens")

    # Crawler Type - Page with form
    steps = forms.CharField(required=False, label="JSON dos passos",
                            max_length=9999999,
                            widget=forms.TextInput(
                                attrs={'placeholder': '{' + '}'})

                            )

    # Crawler Type - Single file
    # Crawler Type - Bundle file

    # ENCODE DETECTION METHOD
    encoding_detection_method = forms.ChoiceField(choices=CrawlRequest.ENCODE_DETECTION_CHOICES, 
                                                    label='Método de detecção de codificação das páginas',
                                                    initial=CrawlRequest.HEADER_ENCODE_DETECTION,
                                                    widget=forms.RadioSelect)

class ResponseHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of a single step in the
    response validation mechanism
    """
    class Meta:
        model = ResponseHandler
        exclude = []
        labels = {
            'handler_type': 'Tipo de validador',
            'opposite': 'Inverter',
            'text_match_value': ('Valor a buscar (não diferencia maiúsculas de'
                                 ' minúsculas)'),
            'http_status': 'Status HTTP'

        }
        widgets = {
            'handler_type': forms.Select(attrs={
                'onchange': 'detailResponseType(event);'
            }),
            'injection_type': forms.HiddenInput(),
        }


class ParameterHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of the request parameters
    to be injected
    """

    def __init__(self, *args, **kwargs):
        super(ParameterHandlerForm, self).__init__(*args, **kwargs)

        injection_type = ""
        if self.initial:
            injection_type = self.initial['injection_type']

        def filter_option(opt):
            if injection_type == "templated_url" and opt[0] == "const_value":
                return False
            return True

        # Templated URL forms shouldn't have a constant injector option
        choices = list(filter(filter_option, ParameterHandler.PARAM_TYPES))

        self.fields['parameter_type'] = forms.ChoiceField(
            choices=choices,
            label='Tipo de parâmetro',
            widget=forms.Select(attrs={
                'onchange': 'detailParamType(event);'
            })
        )

    def clean(self):
        """
        Validates form inputs which depend on other inputs' values
        """
        cleaned_data = super().clean()

        if cleaned_data.get('DELETE'):
            # Do not validate if this entry is to be deleted
            return cleaned_data

        param_type = cleaned_data.get('parameter_type')

        general_error = 'Verifique os campos abaixo'

        if param_type == 'process_code':
            # Validate if initial and final years are in order
            first_year = cleaned_data.get('first_year_proc_param')
            last_year = cleaned_data.get('last_year_proc_param')

            if first_year > last_year:
                msg = 'O primeiro ano deve ser menor que o último.'
                self.add_error('first_year_proc_param', msg)
                self.add_error('last_year_proc_param', msg)
                raise ValidationError(general_error)

        elif param_type == 'number_seq':
            # Validate if initial and final values are in order
            first_value = cleaned_data.get('first_num_param')
            last_value = cleaned_data.get('last_num_param')

            if first_value > last_value:
                msg = 'O primeiro número deve ser menor que o último.'
                self.add_error('first_num_param', msg)
                self.add_error('last_num_param', msg)
                raise ValidationError(general_error)

        elif param_type == 'date_seq':
            # Validate if initial and final dates are in order
            first_date = cleaned_data.get('start_date_date_param')
            last_date = cleaned_data.get('end_date_date_param')

            if first_date > last_date:
                msg = 'A primeira data deve ser menor que a última.'
                self.add_error('start_date_date_param', msg)
                self.add_error('end_date_date_param', msg)
                raise ValidationError(general_error)

        filter_range = cleaned_data.get('filter_range')
        cons_misses = cleaned_data.get('cons_misses')
        if filter_range and not cons_misses:
            # If the parameter is to be filtered, the cons_misses value is
            # required
            self.add_error('cons_misses', ('O número de falhas consecutivas '
                                           'deve ser fornecido'))
            raise ValidationError(general_error)

        return cleaned_data

    class Meta:
        model = ParameterHandler
        fields = '__all__'
        labels = {
            'first_num_param': 'Primeiro valor a gerar',
            'last_num_param': 'Último valor a gerar',
            'leading_num_param': 'Zeros à esquerda',
            'length_alpha_param': 'Tamanho da palavra',
            'num_words_alpha_param': 'Número de palavras',
            'no_upper_alpha_param': 'Apenas letras minúsculas',
            'date_format_date_param': 'Formato de data a usar',
            'start_date_date_param': 'Data inicial',
            'end_date_date_param': 'Data final',
            'frequency_date_param': 'Frequência a gerar',
            'first_year_proc_param': 'Primeiro ano a coletar',
            'last_year_proc_param': 'Último ano a coletar',
            'segment_ids_proc_param': ('Identificadores de órgãos a buscar, '
                                       'separados por vírgula'),
            'court_ids_proc_param': ('Identificadores de tribunais a buscar, '
                                     'separados por vírgula'),
            'origin_ids_proc_param': ('Identificadores de origens a buscar, '
                                      'separados por vírgula'),
            'value_list_param': 'Lista de valores a gerar (separados por vírgula)',
            'value_const_param': 'Valor a gerar',
            'filter_range': 'Filtrar limites',
            'parameter_label': 'Descrição do campo',
            'parameter_key': 'Nome do campo',
        }

        widgets = {
            'date_format_date_param': forms.TextInput(attrs={
                'placeholder': '%m/%d/%Y'
            }),
            'start_date_date_param': forms.DateInput(attrs={'type': 'date'}),
            'end_date_date_param': forms.DateInput(attrs={'type': 'date'}),
            'filter_range': forms.CheckboxInput(
                attrs={"onclick": "detailParamFilter(event);", }
            ),

            # Validate parameters which are lists of numbers (with possible
            # whitespaces between numbers)
            'segment_ids_proc_param': forms.TextInput(attrs={
                'pattern': ParameterHandler.LIST_REGEX,
                'title': 'Insira uma lista de números separados por vírgula.',
            }),
            'court_ids_proc_param': forms.TextInput(attrs={
                'pattern': ParameterHandler.LIST_REGEX,
                'title': 'Insira uma lista de números separados por vírgula.',
            }),
            'origin_ids_proc_param': forms.TextInput(attrs={
                'pattern': ParameterHandler.LIST_REGEX,
                'title': 'Insira uma lista de números separados por vírgula.',
            }),
            'injection_type': forms.HiddenInput(),
        }

    step_num_param = forms.IntegerField(initial=1, required=False,
                                        label='Tamanho do passo')

    cons_misses = forms.IntegerField(initial=100, required=False,
        label=('Falhas consecutivas necessárias para considerar um intervalo '
               'do parâmetro inválido'))


# Formset for ResponseHandler forms
ResponseHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ResponseHandler, form=ResponseHandlerForm, exclude=[], extra=0, min_num=0,
    can_delete=True)


# Formset for ParameterHandler forms
ParameterHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ParameterHandler, form=ParameterHandlerForm, exclude=[], extra=0,
    min_num=0, can_delete=True)
