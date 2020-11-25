from django import forms
from .models import CrawlRequest, ParameterHandler, ResponseHandler
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

import re


class CrawlRequestForm(forms.ModelForm):
    class Meta:
        model = CrawlRequest


        labels = {
            'request_type': 'Método da requisição',
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
            'link_extractor_allow_url',
            'download_files',
            'download_files_allow_url',
            'download_files_allow_extensions',
            'download_imgs',
            'wait_crawler_finish_to_download',
            'time_between_downloads',
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

    wait_crawler_finish_to_download = forms.BooleanField(
        required=False, label="Esperar coletor finalizar para baixar arquivos")

    time_between_downloads = forms.IntegerField(
        required=False,
        label="Tempo entre requisições de download de arquivos",
    )

    # Crawler Type - Page with form
    steps = forms.CharField(required=False, label="Steps JSON",
                            max_length=9999999,
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
        labels = {
            'handler_type': 'Tipo de validador',
            'opposite': 'Inverter',
            'text_match_value': ('Valor a buscar (não diferencia maiúsculas de'
                                 ' minúsculas)'),
            'http_status': 'Status HTTP'

        }
        widgets = {
            'handler_type': forms.Select(attrs={
                'onchange': 'detailTemplatedUrlResponseType(event);'
            }
            ),
        }


class ParameterHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of the request parameters
    to be injected
    """

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
            'parameter_type': 'Tipo de parâmetro',
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
            'filter_range': 'Filtrar limites',
        }

        widgets = {
            'parameter_type': forms.Select(attrs={
                'onchange': 'detailTemplatedUrlParamType(event);'
            }),
            'date_format_date_param': forms.TextInput(attrs={
                'placeholder': '%m/%d/%Y'
            }),
            'start_date_date_param': forms.DateInput(attrs={'type': 'date'}),
            'end_date_date_param': forms.DateInput(attrs={'type': 'date'}),
            'filter_range': forms.CheckboxInput(
                attrs={"onclick": "detailTemplatedURLParamFilter(event);", }
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
