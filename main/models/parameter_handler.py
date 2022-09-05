from django.core.validators import RegexValidator
from django.db import models

from main.models import  CrawlRequest

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
