# Scheduler

Este módulo trata-se de um plugin para o Monitor Kafka do Scrapy Cluster que permite agendar visitas e revisitas.

**Recursos**:

- Agendar coletas para o Scrapy Cluster com repetição em intervalos regulares de tempo baseado em:
    - Minutos
    - Horas
        - Em um minuto específico
        - De uma hora até outra
    - Dias
        - Em hora e minuto específico
        - De um dia da semana até outro
    - Semanas
        - Em dia, hora e minuto específico

## A Fazer

- [ ] Definir os parâmetros de recoletas automaticamente.
- [ ] Maior cobertura de testes.

## Instalação

É necessário que os arquivos `scheduler.py` e `scheduler_schema.json` (em `scheduler/`) estejam na pasta de plugins do Kafka Monitor do Scrapy Cluster `scrapy-cluster > kafka-monitor > plugins`. 

Ative o plugin, por meio do `localsettings.py` junto com os demais do Scrapy Cluster:

```python
# scrapy-cluster/kafka-monitor/localsettings.py

PLUGINS = {
    'plugins.scraper_handler.ScraperHandler': 100,
    'plugins.scheduler.SchedulerPlugin': 150, # (Novo)
    'plugins.action_handler.ActionHandler': 200,
    'plugins.stats_handler.StatsHandler': 300,
    'plugins.zookeeper_handler.ZookeeperHandler': 400,
}
 
```

## Uso

Utilize a api de envio de requisições de coletas do Scrapy Cluster como de costume. Caso queira agendar uma coleta, basta especificar um objeto json `scheduler` dentro das requisições envidas, com os seguintes campos:

- `repeat`: (opcional) Um dicionário que especifica repetições de coletas, como os seguintes campos:
    
    - `interval`: Informa o intervalo das recoletas. Pode ser: `minutes`, `hours`, `days`, `weeks`.
    - `every`: Tamanho do passo da repetição em `interval`. Por exemplo, `every = 3` e `interval = 'days'`, repetirá uma coleta de 3 em 3 dias.
    - `at_minute`: (opcional) Se `interval` for `hours`, `days` ou `weeks` o minuto que a coleta deverá ser realizada.
    - `at_hour`: (opcional) Se `interval` for `days` ou `weeks` a hora que a coleta deverá ser realizada.
    - `at_weekday`: (opcional) Se `interval` for `weeks`, o dia da semana que a coleta deve ocorrer. Deve ser inteiro, sendo segunda = 0 ... domingo = 6.
    - `from` e `to`: Se `interval` for `hours` ou `days`, restringe a hora ou dia que as coletas devem ocorrer, respectivamente.

- `visit_at`: (opcional) É possível explicitar quando uma coleta será realizada manualmente. É necessário seguir o padrão `Y-m-d H:M`, onde **Y** é o ano, **m** o mês, **d** o dia, **H** a hora e *M* o minuto que a coleta deve ser realizada. Caso `repeat` estiver definido, uma coleta será realizada em `visit_at` e se repetirá tendo como base esse horário e de acordo com `repeat`. Se não, a coleta será realizada em `visit_at` e não se repetirá mais. Caso `visit_at` não estiver definido, e `repeat` sim, recoletas ocorrerão tendo como base o horário corrente.

## Exemplos

**Agendar uma coleta SEM REPETIÇÃO para 25 de dezembro de 2021 às 21:30:**

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.google.com",
    "appid": "testapp",
    "crawlid": "xyz",
    "scheduler": {
        "start_at": "2021-12-25 21:30"
    }
}'
```

**Agendar uma coleta para 21 de dezembro de 2021 às 21:30 e repetir diariamente de segunda a sexta:**

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.google.com",
    "appid": "testapp",
    "crawlid": "xyz",
    "scheduler": {
        "start_at": "2021-12-21 21:30",
        "repeat": {
            "every": 1,
            "interval": "days",
            "from": 0,
            "to": 4
        }
    }
}'
```

**Agendar uma coleta de 3 em 3 horas, das 18h até 6h, a partir de agora:**

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.google.com",
    "appid": "testapp",
    "crawlid": "xyz",
    "scheduler": {
        "repeat": {
            "every": 3,
            "interval": "hours",
            "from": 18,
            "to": 6
        }
    }
}'
```

**Agenda uma coleta de segunda a sexta, às 23:30, a partir de hoje:**

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.google.com",
    "appid": "testapp",
    "crawlid": "xyz",
    "scheduler": {
        "repeat": {
            "every": 1,
            "interval": "days",
            "at_hour": 23,
            "at_minute": 30,
            "from": 0,
            "to": 4
        }
    }
}'
```

**Agenda uma coleta toda semana na sexta às 19:15, a partir de hoje:**

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.google.com",
    "appid": "testapp",
    "crawlid": "xyz",
    "scheduler": {
        "repeat": {
            "every": 1,
            "interval": "weeks",
            "at_weekday": 4,
            "at_hour": 19,
            "at_minute": 15
        }
    }
}'
```