# crawled_request_filter

Extensão simples capaz de filtrar links de coletas já realizadas pelo Scrapy Cluster.

Este módulo faz uso de consultas a banco de dados definido em no módulo https://github.com/MPMG-DCC-UFMG/C04/issues/238 (acesse-a para mais detalhes). Abaixo o esquema da tabela:

| Tabela CRAWL_HISTORIC |
| :--- |
| String: crawlid (PK) |
| JsonB: crawl_historic |

## Configurações

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
Adicione os arquivos da pasta `/plugin` na pasta `plugins/` de `kafka-monitor` do `Scrapy Cluster`.

Adicione a pasta do módulo `crawled_request_filter/` a pasta `kafka-monitor/` do `Scrapy Cluster`.

## Uso 

Apenas adicione `filter_if_crawled = true` nas requisições feitas ao `Scrapy Cluster`.

