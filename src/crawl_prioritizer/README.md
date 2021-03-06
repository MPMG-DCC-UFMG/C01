# crawl-prioritizer

Plugin para o Scrapy Cluster capaz de determinar prioridades para coletas individuais.

**Recursos**

- Permite definir prioridades para requisições de coletas feitas ao Scrapy Cluster, baseado em seu histórico.


Este módulo faz uso de consultas a banco de dados definido no módulo de https://github.com/MPMG-DCC-UFMG/C04/issues/238 (acesse-a para mais detalhes). Abaixo o esquema da tabela:

| Tabela CRAWL_HISTORIC |
| :--- |
| String: crawlid (PK) |
| JsonB: crawl_historic |

## Testes

Para realizar os testes deste módulo, é necessário que o PostGreSQL esteja devidamente configurado, por esta razão, estão desabilitados.

O teste individual pode ser feito configurando os campos relacionados ao PostGreSQL em `crawl_prioritizer/settings.py` de acordo. E então executar:

```bash
# na pasta C04/tests/.crawl_prioritizer
python -m unittest test_crawl_prioritizer
```

Caso não possua o PostGreSQL instalado, pode-se seguir estes passos:

**Instalação**:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Configuração**:

Defina uma senha ao PostGreSQL para o usuário padrão. Em `crawl_prioritizer/settings.py`, a senha de demonstração é `my_password`, utilize ela caso não queira alterar o arquivo citado.

```bash
sudo -u postgres psql postgres
\password postgres

# para sair do terminal
\q
```

## Configurações

Adicione as seguintes configurações em `localsettings.py` do módulo `kafka-monitor` de Scrapy Cluster:
```python
PLUGINS = {
    'plugins.scraper_handler_with_prioritizer.ScraperHandlerWithPrioritizer': 100,
    'plugins.scheduler.SchedulerPlugin': 150,
    'plugins.action_handler.ActionHandler': 200,
    'plugins.stats_handler.StatsHandler': 300,
    'plugins.zookeeper_handler.ZookeeperHandler': 400,
}
``` 
O trecho acima fará com que o Scrapy Cluster deixe de usar o plugin `ScraperHandler` por `ScraperHandlerWithPrioritizer`, que possui uma instância da classe responsável por calcular prioridade de uma coleta.

Adicione o arquivo `scraper_handler_with_prioritizer.py` (em `/plugin`) na pasta de plugins do `kafka-monitor` do Scrapy Cluster.

Adicione a pasta com o módulo de priorizador de coletas `/crawl_prioritizer` a pastar `/kafka-monitor` do Scrapy Cluster.

No final, deverá ter uma estrutura de pastas como essa para a o módulo `kafka-monitor` do Scrapy Cluster: 
```bash
kafka-monitor/
├── crawl_prioritizer
│   ├── crawl_prioritizer.py
│   ├── __init__.py
│   ├── requirements.txt
│   ├── settings.py
│   └── utils.py
├── kafkadump.py
├── kafka_monitor.py
├── localsettings.py
├── plugins
│   ├── action_handler.py
│   ├── action_schema.json
│   ├── base_handler.py
│   ├── __init__.py
│   ├── scraper_handler.py
│   ├── scraper_handler_with_prioritizer.py
│   ├── scraper_schema.json
│   ├── stats_handler.py
│   ├── stats_schema.json
│   ├── zookeeper_handler.py
│   └── zookeeper_schema.json
├── requirements.txt
├── settings.py
└── tests
    ├── __init__.py
    ├── online.py
    ├── test_kafka_monitor.py
    └── test_plugins.py
```

Instale os requerimentos (em `crawl_prioritizer/`):

```bash
pip install -r requirements.txt
```

Altere as configurações de conexão com o PostgreSQL, bem como sobre onde as estatísticas das coletas foram salvas em `crawl_prioritizer/settings.py`, se necessário.

## Uso

Há cinco variáveis em `crawl_prioritizer/settings.py` que podem/devem ser configuradas:

- **PRIORITY_EQUATION**: É uma equação que deve ser definida para que seja calculada a prioridade de uma coleta. Pode ser usado três variáveis, que serão substituídas por valores reais pelo módulo. Sendo elas:
    - **domain_prio**: A prioridade do domínio da coleta a ser realizada.
    - **time_since_last_crawl**: Tempo, em segundos, desde a última coleta feita.
    - **change_frequency**: Frequência de mudanças estimada.
- **MAX_PRIORITY**: A prioridade máxima de uma coleta.
- **MIN_PRIORITY**: A prioridade mínima de uma coleta.
- **PRIORITY_NEVER_MADE_CRAWL**: Prioridade de coletas nunca antes feita.
- **DOMAIN_PRIORITY**: Um dicionário tendo como chaves um domínio e valor a prioridade atribuída a ele. Será usada por `PRIORITY_EQUATION` para calcular a prioridade de coletas deste domínio.  
