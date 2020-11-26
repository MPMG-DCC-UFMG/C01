# crawled_request_filter

Extensão simples capaz de filtrar links de coletas já realizadas pelo Scrapy Cluster.

Registros de coletas realizadas são salvos conforme o módulo definido na [issue-238](https://github.com/MPMG-DCC-UFMG/C04/issues/238). Assim, este módulo basicamente verifica se existe registro para uma requisição de coleta feita ao Scrapy Cluster e, se sim, ela é descartada. 

Este módulo faz uso de consultas a banco de dados definido em no módulo https://github.com/MPMG-DCC-UFMG/C04/issues/238 (acesse-a para mais detalhes). Abaixo o esquema da tabela:

| Tabela CRAWL_HISTORIC |
| :--- |
| String: crawlid (PK) |
| JsonB: crawl_historic |

## Testes

Para realizar os testes deste módulo, é necessário que o PostGreSQL esteja devidamente configurado, por esta razão, estão desabilitados.

O teste individual pode ser feito configurando os campos relacionados ao PostGreSQL em `crawled_request_filter/settings.py` de acordo. E então executar:

```python
# na pasta C04/tests/.crawled_request_filter

python -m unittest test_crawled_request_filter
```

Caso não possua o PostGreSQL instalado, pode-se seguir estes passos:

**Instalação**:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Configuração**:

Defina uma senha ao PostGreSQL para o usuário padrão. Em `crawled_request_filter/settings.py`, a senha de demonstração é `my_password`, utilize ela caso não queira alterar o arquivo citado.

```bash
sudo -u postgres psql postgres
\password postgres

# para sair do terminal
\q
```

## Configurações

Para o correto funcionamento desta extensão, é necessário que o módulo [auto_scheduler](https://github.com/MPMG-DCC-UFMG/C04/tree/master/src/auto_scheduler) esteja também habilitado.

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
Copie os arquivos da pasta `/plugin` para a pasta `plugins/` de `kafka-monitor` do `Scrapy Cluster`.

## Uso 

Apenas adicione `"filter_if_crawled": true` nas requisições feitas ao `Scrapy Cluster`. Por exemplo: 

```bash
python kafka_monitor.py feed '
{
    "url": "https://www.some_site.com/content/id=56",
    "appid": "testapp",
    "crawlid": "xyz",
    "filter_if_crawled": true
}'
```

Assim, se a requisição de coleta acima já tiver sido realizada, o log do `kafka_monitor` deverá indicar algo como "This crawl has already been made.". Caso contrário, seguirá o funcionamento padrão do Scrapy Cluster, com um log de sucesso indicando "Added crawl to Redis".