# auto-scheduler

Mecanismo para atualizar configurações de agendamentos de revisitas, baseado no histórico de coletas.

**Recurso**:

- Estima a frequência de mudança de uma coleta baseado em seu histórico, atualizando as recoletas de acordo.
- Salva os metadados de coletas feitas pelo Scrapy Cluster.
    - Para isso, adicione o nome do(s) metadado(s) a serem salvos em `ADDITIONAL_METADATA_TO_SAVE`, em `auto_scheduler/settings.py`. O `timestamp`, `url` e `hash` do conteúdo da página coleta, por padrão, é sempre salvo.

## Tabela de Dados

Os dados são salvos segundo o esquema abaixo:

| Tabela CRAWL_HISTORIC |
| :--- |
| String: crawlid (PK) |
| JsonB: crawl_historic |

Onde `crawlid` é a chave primária e registra o hash md5 da url da coleta. Por sua vez, `crawl_historic` registra o histórico de coletas como json, que segue o seguinte esquema: 

```

{
    "grupo de visita 1": [
        {
            //visita 1
        },
        .
        .
        .,
        {
            //visita #NUMBER_VISITS_TO_GENERATE_ESTIMATE
        }
    ],
    .
    .
    .,
    "grupo de visita n": [
        {
            //visita 1
        },
        .
        .
        .
    ],
    "estimated_frequency_changes": x,
    "last_visit_timestamp": y
}
```

Onde `grupo de visita n` é o conjunto de visitas feitas para gerar a estimativa de mudanças para as próximas coletas que ficaram registradas no grupo de visitas `n + 1`. O tamanho desses grupos é determinados por `NUMBER_VISITS_TO_GENERATE_ESTIMATE`. Por sua vez, `estimated_frequency_changes` é a frequẽncia de mudanças estimada em segundos, enquanto `last_visit_timestamp` é o timestamp da última visita realizada.

## Uso

Configure as variáveis em `auto_scheduler/settings.py` de acordo com seu sistema para o Redis e Kafka, bem como o número de visitas para gerar estimativa de quando uma coleta muda e variáveis do Scrapy Cluster.

É necessário que o plugin de agendamento de coletas para o Scrapy Cluster esteja ativo, e que elas estejam agendadas para se repetir em algum intervalo de tempo.

Instale os requerimentos:

```bash
pip install -r auto_scheduler/requirements.txt
```

Então execute:

```python
from auto_scheduler import CrawledConsumer
CrawledConsumer.run()
```

O comando acima executará um consumidor Kafka para o tópico de saída das coletas do Scrapy Cluster. Ao receber uma coleta, alguns de seus metadados serão persistidos e então verificado se houve alteração ou não em seu conteúdo a partir de uma eventual outra coleta que tenha sido realizada. Quando o número de coletas for suficiente para gerar uma estimativa (definido em `NUMBER_VISITS_TO_GENERATE_ESTIMATE` - `auto_scheduler/settings.py`), ela será gerada e enviada ao plugin de agendamento de coletas do Scrapy Cluster para que a frequência de visitas para a coleta em questão seja atualizado.

Por razões de desempenho e eficiência, o ideal é que `CrawledConsumer.run()` não seja executado em produção, mas sim que o método que ele chama para persistir os metadados das coletas quando elas chegam (`MetadataIndexer.persist(coleta_realizada)`) fique incluído no módulo principal de processamento de coletas. 

## Estimadores

Os estimadores são baseados em [Cho-Thesis](https://oak.cs.ucla.edu/~cho/papers/cho-thesis.pdf), e é possível escolher dois por meio da variável `ESTIMATOR` - `auto_scheduler/settings.py`:

- `changes`: A estimativa de frequência de mudança é baseado no número médio de alterações detectadas nas visitas. Seus resultados se mostraram melhores que o próximo estimador. É o valor padrão. 
- `nochanges`: É baseado no número de visitas que não houveram mudanças. A principal vantagem em relação ao primeiro é que ele pode fazer estimativas abaixo do intervalo previamente configurado para gerar estimativa.