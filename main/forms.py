from django import forms
from .models import CrawlRequest, ParameterHandler, ResponseHandler
from django.core.validators import RegexValidator


class CrawlRequestForm(forms.ModelForm):
    class Meta:
        model = CrawlRequest


        labels = {
            'request_type': 'Request method',
        }

        output_filename = forms.CharField(required=False)
        save_csv = forms.BooleanField(required=False)

        fields = [


            'source_name',
            'base_url',
            'request_type',
            'obey_robots',
            'captcha',

            'antiblock_download_delay',
            'antiblock_autothrottle_enabled',
            'antiblock_autothrottle_start_delay',
            'antiblock_autothrottle_max_delay',
            'antiblock_ip_rotation_enabled',
            'antiblock_ip_rotation_type',
            'antiblock_max_reqs_per_ip',
            'antiblock_max_reuse_rounds',
            'antiblock_proxy_list',
            'antiblock_user_agent_rotation_enabled',
            'antiblock_reqs_per_user_agent',
            'antiblock_user_agents_list',
            'antiblock_insert_cookies_enabled',
            'antiblock_cookies_list',
            # 'antiblock_persist_cookies',

            'has_webdriver',
            'webdriver_path',
            'img_xpath',
            'sound_xpath',
            'crawler_type',
            'explore_links',
            'link_extractor_max_depth',
            'link_extractor_allow_url',
            'download_files',
            'download_files_allow_url',
            'download_files_allow_extensions',
            'download_imgs',
            'steps',
            'save_csv',
            'table_attrs',
            'data_path',
        ]

        widgets = {'table_attrs': forms.HiddenInput()}


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
            'placeholder': 'www.example.com/data/',
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

    # ANTIBLOCK ###############################################################
    # Options for Delay
    antiblock_download_delay = forms.IntegerField(
        required=False,
        label=(
            "Intervalo médio em segundos (ou intervalo mínimo se "
            "auto ajuste está ligado)."
        ),
        initial=2,
        min_value=0
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
        min_value=1
    )
    antiblock_autothrottle_max_delay = forms.IntegerField(
        required=False,
        label="Intervalo máximo",
        initial=10,
        min_value=1
    )

    # Options for mask type
    # antiblock_mask_type = forms.ChoiceField(
    #     required=False, choices=(
    #         ('none', 'None'),
    #         # ('ip', 'Rotação de IP'),
    #         # ('user_agent', 'Rotação de user-agent'),
    #         # ('delay', 'Intervalos entre requisições'),
    #         # ('cookies', 'Usar cookies'),
    #     ),
    #     widget=forms.Select(attrs={'onchange': 'detailAntiblock();'})
    # )

    # Options for IP rotation
    antiblock_ip_rotation_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    antiblock_ip_rotation_enabled = forms.BooleanField(
        required=False,
        label="Rotacionar IPs",
        widget=forms.CheckboxInput(
            attrs={
                "onclick": "ipRotationEnabled();",
            }
        )
    )

    antiblock_max_reqs_per_ip = forms.IntegerField(
        required=False,
        label="Máximo de requisições por IP",
        initial=10,
        min_value=1
    )

    antiblock_max_reuse_rounds = forms.IntegerField(
        required=False,
        label="Número de rodadas que um IP pode ser reusado",
        initial=10,
        min_value=1
    )

    antiblock_proxy_list = forms.CharField(
        required=False, 
        label="Insira a lista de proxy",
        widget=forms.Textarea(
            attrs={
                'placeholder': (
                    "Coloque aqui os proxies (um por linha)"
                )
            }
        )
    )
    

    # Options for User Agent rotation

    antiblock_user_agent_rotation_enabled = forms.BooleanField(
        required=False, 
        label="Rotacionar User-Agents",
        widget=forms.CheckboxInput(
            attrs={
                "onclick": "userAgentRotationEnabled();",
            }
        )
    )

    antiblock_reqs_per_user_agent = forms.IntegerField(
        required=False, 
        label="Requisições por User-Agent",
        initial=100,
        min_value=1
    )

    antiblock_user_agents_list = forms.CharField(
        required=False, 
        label="Lista de User-Agent",
        widget=forms.Textarea(
            attrs={
                'placeholder': (
                    'Um user-agent por linha. Ex.:\n'
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)...\n'
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
                )
            }
        )
    )

    # Options for Cookies
    antiblock_insert_cookies_enabled = forms.BooleanField(
        required=False,
        label="Inserir cookies",
        widget=forms.CheckboxInput(
            attrs={
                "onclick": "insertCookiesEnabled();",
            }
        )
    )

    antiblock_cookies_list = forms.CharField(
        required=False,
        label="Lista de cookie",
        widget=forms.Textarea(
            attrs={
                'placeholder': (
                    'Um cookie por linha como objeto javascript. Ex.:\n'
                    '{"authenticated": true, "access_token": "a93f31b19257193d49a971023dcd95f7"}\n'
                    '{"valid_until": 1605225253, "private_key": "429b10192642a52276605047ddda9d45"}'
                )
            }
        )
    )

    # antiblock_persist_cookies = forms.BooleanField(
    #     required=False, 
    #     label="Manter cookies entre requisições")

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
    crawler_type = forms.ChoiceField(
        required=False, choices=(
            ('static_page', 'Página estática'),
            ('form_page', 'Páginas com formulário'),
            # ('single_file', 'Arquivo único'),
            # ('bundle_file', 'Conjunto de arquivos'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCrawlerType();'})
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
            "Permitir urls que casem com o regex"
            " (deixe em branco para não filtrar):"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': 'Regex para permitir urls'})
    )

    download_files = forms.BooleanField(
        required=False, label="Baixar arquivos")

    download_files_allow_url = forms.CharField(
        required=False, max_length=2000,
        label=(
            "Baixar arquivos de url que casem com o regex"
            " (deixe em branco para não filtrar):"
        ),
        widget=forms.TextInput(
            attrs={'placeholder': 'Regex para permitir urls'})
    )

    download_files_allow_extensions = forms.CharField(
        required=False, max_length=2000,
        label="Extensões de arquivo permitidas (separado por vírgula):",
        widget=forms.TextInput(attrs={'placeholder': 'pdf,xml'})
    )

    download_imgs = forms.BooleanField(
        required=False, label="Baixar imagens")

    # Crawler Type - Page with form
    steps = forms.CharField(required=False, label="Steps JSON", max_length=9999999,
                            widget=forms.TextInput(
                                attrs={'placeholder': '{' + '}'})
                            )

    # Crawler Type - Single file
    # Crawler Type - Bundle file

    # PARSING #################################################################
    save_csv = forms.BooleanField(
        required=False, label="Salvar arquivo csv",
        widget=forms.CheckboxInput(attrs={'checked': True})
    )
    table_attrs = forms.CharField(
        required=False, max_length=2000, label="Motor de extração",
        widget=forms.HiddenInput(attrs={'id': 'table_attrs_hidden'})
    )


class ResponseHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of a single step in the
    response validation mechanism
    """
    class Meta:
        model = ResponseHandler
        exclude = []
        widgets = {
            'handler_type': forms.Select(attrs={
                'onchange': 'detailTemplatedUrlResponseParams(event);'
            }
            ),
        }


class ParameterHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of the request parameters
    to be injected
    """

    class Meta:
        model = ParameterHandler
        fields = '__all__'
        labels = {
            'first_num_param': 'Primeiro valor a gerar:',
            'last_num_param': 'Último valor a gerar:',
            'step_num_param': 'Tamanho do passo:',
            'leading_num_param': 'Zeros à esquerda',
            'length_alpha_param': 'Tamanho da palavra:',
            'num_words_alpha_param': 'Número de palavras:',
            'no_upper_alpha_param': 'Apenas letras minúsculas',
            'date_format_date_param': 'Formato de data a usar:',
            'start_date_date_param': 'Data inicial:',
            'end_date_date_param': 'Data final:',
            'frequency_date_param': 'Frequência a gerar',
        }

        widgets = {
            'parameter_type': forms.Select(attrs={
                'onchange': 'detailTemplatedUrlParamType(event);'
            }),
            'date_format_date_param': forms.TextInput(attrs={
                'placeholder': '%m/%d/%Y'
            }),
            'start_date_date_param': forms.DateInput(attrs={'type': 'date'}),
            'end_date_date_param': forms.DateInput(attrs={'type': 'date'})
        }


# Formset for ResponseHandler forms
ResponseHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ResponseHandler, form=ResponseHandlerForm, exclude=[], extra=1, min_num=0,
    can_delete=True)


# Formset for ParameterHandler forms
ParameterHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ParameterHandler, form=ParameterHandlerForm, exclude=[], extra=1,
    min_num=0, can_delete=True)
