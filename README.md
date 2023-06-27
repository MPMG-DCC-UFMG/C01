# C01 

Existem coletores bases, que podem ser personalizados através da interface feita em django. Eles são capazes de coletar:

## Status atual

- Distribuição de spiders (funcionam cooperativamente em máquinas distintas)
- Problemas de escalabilidade no módulo de salvamento de coletas/arquivos
- Suporte a páginas estáticas e downloads de arquivos
- Suporte parcial a páginas dinâmicas (com bugs)
- Suporte a download de arquivos em páginas dinâmicas. Mas caso haja mais de uma instância de `spider_manager` executando em máquinas distintas, os arquivos serão salvos em locais diferentes.   
- Logs são transmitidos distribuidamente via Kafka
- Monitoramento parcial de coletas/coletores
    - É possível acompanhar o andamento da coleta de páginas/arquivos
    - Não é possível acompanhar a "saúde" dos `workers`/`spiders`
    
## TODOs

A lista atualizada pode ser vista [aqui](https://github.com/MPMG-DCC-UFMG/C01/issues?q=is%3Aissue+is%3Aopen+label%3A%22sistema+distribu%C3%ADdo%22): 

- [ ] Suporte total a páginas dinâmicas (há certos bugs na execução de coletas)
- [ ] Download centralizado de arquivos em páginas dinâmicas
    - Provavelmente será necessário suporte a sistema de arquivos distribuídos 
- [x] Suporte a mecânismos de passos (páginas dinâmicas)
- [ ] Resolver problemas de escalabilidade (módulos `writer` e `link_generator`)
    - Será necessário suporte à sistema de arquivos distribuídos para o módulo `writer`
- [ ] Melhorias no sistema de acompanhamento de andamento de coletas (o atual não esté "calibrado")
- [ ] Tela de monitoramento de coletas, como saúde dos `workers`/`spiders`
- [ ] Realização de testes, inclusive de robustez 

## Como executar

Temos 4 módulos que devem funcionar de maneira independente: `Crawler Manager (CM)` (que inicia junto com o servidor), `Link Generator (LG)`, `Spider Manager (SM)` e `Writer (W)`. 

Esses módulos, devidademente configurado os `hosts` do `Zookeeper`, `Kafka` e `Redis`, em um arquivo `settings.py` na respectiva pasta deles, podem ser executados em máquinas diferentes com as seguintes condições:

- Cada um devem ser iniciados manualmente, ainda não foram dockerizados.
- Deve haver apenas uma instância em execução dos seguintes módulos:
    - `Crawler Manager`: Naturalmente terá apenas uma instância em execução, pois é um processo filho do servidor.
    - `Link Generator`: Mais de uma instância em execução resultará em duplicação de requisições de coletas. Isso porque cada instância irá ler o comando de geração de requisições, então **é necessário adaptar a leitura de mensagens do Kafka para que apenas um consumer leia cada mensagem**.
    - `Writer`: Esse módulo tem o problema de escalabilidade de `Link Generator` (Kafka consumers lendo a mesma mensagem, portanto, gerando processamento duplicado), mas mais que isso, ter mais de uma instância em execução resultará em `fragmentação da coleta`. Isso pois cada módulo escreve dados no sistema de arquivos local de cada máquina. Portando, é `necessário suporte a sistema de arquivos distribuídos`.  
- Podem haver várias instâncias de `Spider Managers` em execução, inclusive na mesma máquina. Ao contrário dos problemas de escalabilidade relatado nos outros módulos que se comunicam via `Kafka`, a fila de coletas é gerenciado via `Redis`, de modo que não há processamento de uma mesma mensagem por consumidores diferentes.
    - No momento, um `Spider Manager` por gerir apenas um spider de uma mesma coleta.

> **Obs.**: Zookeeper, Kafka e Redis devem estar em execução e seus hosts e portas configuradas nos arquivos settings.py dos módulos. 

### Iniciando Kafka e Redis

Ao executar `python install.py` na raiz do projeto, tanto o `Kafka` quanto o `Redis` são baixados automaticamente. Para executá-los, execute os seguintes comandos (considerando que a pasta corrente é a raiz do projeto):

Inicie o `Zookeeper` para que o `Kafka` funcione corretamente:
```bash
cd kafka_2.13-2.4.0/
bin/zookeeper-server-start.sh config/zoo.properties
```

Abra um outro terminal e inicie o Kafka:

```bash
cd kafka_2.13-2.4.0/
bin/kafka-server-start.sh config/server.properties
```
Caso seu sistema não seja Linux, siga as instruções de instalação da Java Runtime para o seu sistema, as quais podem ser encontradas nesse [link](https://www.java.com/en/download/manual.jsp).

Abra outro terminal e inicie o `Redis`:

```bash
cd redis-5.0.10/
./src/redis-server
```

### Interface/servidor Django

Instale as dependências:

```bash

python3.7 -m venv venv
source venv/bin/activate
python install.py
```

Coloque-o para rodar:

```bash
python manage.py runserver --noreload
```

> Note a flag `--noreload`, ela é importante para que o servidor não reinicie durante sua execução e crie mais consumidores Kafka que o necessário (gerando duplicação de `logs`, por exemplo)

### Link Generator

Vá para a pasta do módulo e instale suas dependências:

```bash
cd link_generator/
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Execute-o:

```bash
cd src/
python main.py
```

### Spider Manager

Vá para a pasta do módulo e instale suas dependências:

```bash
cd spider_manager/
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

> Note que é usado python3.6. Isso é um requisito necessário, pois o módulo utiliza recursos do Scrapy-Cluster que só a suporte a essa versão do python.

Crie quandos processos desejar de Spider Managers, repetindo o comando abaixo:

```
cd src/
python comand_listener.py
```
### Writer

Vá para a pasta do módulo e instale suas dependências:

```
cd writer/
python3.7 -m venv venv
source venv/bin/activate
```

Execute-o:

```bash
cd src/
python writer.py
```
## Arquitetura atual da solução distribuída

![Arquitetura](sist_dist_diagram.png) 

O sistema possui 4 módulos principais:

- **Gerenciador de coletas** (`crawler_manager`)
    - Módulo acoplado ao servidor. 

    - É responsável por realizar a interface entre a aplicação Django e os módulos de processamento de coletas.

    - Recebe status de spiders (criação e encerramento) vindos de gerenciador de spiders. Com isso, é capaz de saber e informar ao servidor quando uma coleta terminou.

    - Também repassa os logs das coletas ao servidor, bem como o atualiza sobre o andamento das coletas, em geral.

- **Gerador de requisições de coletas** (`link_generator`, *um melhor nome pode ser atribuído)
    - Responsável por gerar as requisições iniciais de coletas. 

    - Útil para o caso de URLs parametrizadas não sobrecarreguem o servidor.

    - **Funcionamento atual**

        - O módulo recebe a configuração de um coletor e gera todas requisições de coletas possíveis. Um dos possíveis impactos disso é "inundar" o Redis.

    - **Funcionamento desejado/futuro**
        
        - Geração requisições de coletas sob demanda. 

- **Gerenciador de spiders** (`spider_manager`)
    - Responsável por gerenciar o ciclo de vida dos spiders, bem como informar ao gerenciador de coletas sobre o status dos mesmos e das coletas.

    - **Funcionamento atual**

        - Há suporte há apenas um spider por coleta para cada gerenciador de spiders. Mas podem haver múltiplos spiders gerenciados, desde que sejam de coletas diferentes.

        - Spiders são criados no início do processo de coleta, e, caso um spider fique ocioso por determinado tempo, ele é automaticamente encerrado.

    - **Funcionamento desejado/futuro**

        - Suporte a múltiplos spiders de um mesmo coletor.

        - Balanceamento de carga. Criação e encerramento de spiders a qualquer momento, de acordo com a necessidade. 

- **Escritor** (`writer`)
    - Responsável por persistir as coletas, bem como baixar e salvar os possíveis arquivos encontrados nela.

    - **Funcionamento atual**

        - Só é suportado que apenas um deste módulo execute ao mesmo tempo. Pois os dados coletados são salvos diretamente no sistema de arquivo da máquina hospedeira.

        - Mais de um deste módulo em execução implicaria em dados salvos em máquinas diferentes ou possíveis conflitos de arquivos.

        - Isso reflete em um possível gargalo ao salvar os dados coletados, como os dados coletados são transmitidos por um único tópico Kafka e o processamento por um única instância deste módulo.

    - **Funcionamento desejado/futuro**

        - Suporte a sistema de arquivos distribuídos e/ou salvamento dos dados coletados em banco de dados (para o caso das páginas), possibilitando múltiplas instâncias do módulo executando ao mesmo tempo.
