# crawled_request_filter

Plugin simples capaz de filtrar requisições de coletas já realizadas pelo Scrapy Cluster, poupando recursos.

**TODOs**

- [ ] Instalação automática.

## Configurações

Instale a seguinte biblioteca:

```bash
pip install psycopg2==2.8.6
```

Adicione as seguintes configurações em `localsettings.py` do módulo `kafka-monitor` de Scrapy Cluster:
```python
PLUGINS = {
    'plugins.scraper_handler.ScraperHandler': 100,
    'plugins.crawled_filter.CrawledFilter': 150,  # (Novo)
    'plugins.action_handler.ActionHandler': 200,
    'plugins.stats_handler.StatsHandler': 300,
    'plugins.zookeeper_handler.ZookeeperHandler': 400,
}
``` 
Adicione os arquivos da pasta `/plugin` de  na pasta `plugins/` do `Scrapy Cluster`.

Adicione a pasta do módulo `crawled_request_filter/` a pasta `kafka-monitor/` do `Scrapy Cluster`.

## Uso 

Apenas adicione `filter_if_crawled = true` nas requisições feitas ao `Scrapy Cluster`.

