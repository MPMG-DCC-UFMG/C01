# C04

Desenvolvimento de ferramentas para construção e manutenção de coletores de páginas da Web. (Em desenvolvimento)

Existem 4 tipos de coletores bases, que podem ser personalizados através da interface feita em django:
1. Coletor de páginas estáticas
2. Coletor de páginas dinâmicas ou onde é necessário interagir com formulários.
3. Coletor para coleta de arquivos
4. Coletor para coleta de conjunto de arquivos

Os coletores são desenvolvidos em Scrapy em conjunto com Puppeteer para o caso de páginas dinâmicas. O gerenciamento dos coletores é feito com o Scrapy-cluster.

Dentre as funcionalidades disponíveis para os coletores, temos:
- Mecanismos para camuflagem dos coletores, como rotação de endereço de IP e gerenciamento de cookies.
- Mecanismos para tentar contornar Captchas e outras formas de bloqueio
- Ferramentas para gerar endereços automaticamente através de templates
- Ferramentas para extração e conversão de dados

Os coletores também podem ser gerenciados através de uma API RESTful.

## Configuração do cluster

No diretório ```/crawlers/scrapy-cluster```, há três diretórios principais usados pelo projeto: ```/rest```, ```/kafka-monitor``` e ```/redis-monitor```. Esses diretórios possuem um arquivos de configuração local chamados localsettings.py, que contêm informações relativas à _master_ (host do Kafka, do Zookeeper e da interface). Atualmente, essas configurações consideram a máquina des01 (endereço 10.21.0.131) como _master_.

É usado um arquivo de configuração para o Redis com uma senha padrão, que pode ser alterada em /C04/redis.conf na linha 507. Se alterada, essa senha deve ser atualizada nos arquivos de localsettings mencionados acima.

As instruções para instalar e configurar a _master_ e as _slaves_, bem como remover uma _slave_ são dadas a seguir.

## Instalação e configuração da _master_

Antes de intalar o projeto, instale a biblioteca libxss1 com o seguinte comando:
```
$ sudo apt-get install libxss1
```

Para a instalação do projeto na master, basta clonar o repositório na branch issue-261-mp, criar um ambiente virtual python 3.6 e rodar o script install.py, que instala o projeto e as dependências do Scrapy Cluster.

```
$ git clone -b issue-261-mp https://github.com/MPMG-DCC-UFMG/C04.git
$ cd C04
$ python3.6 -m venv env
$ source env/bin/activate
$ sudo chmod 777 /tmp/tika.log
$ python install.py
```

Após as instalações, é necessário inciar os seguintes componentes: Zookeeper, Kafka, serviço REST, monitor do Kafka e as n spiders desejadas. Os dois primeiros são inicializados ao executar run.py.

```
$ tmux new -s django
$ source env/bin/activate
$ python run.py   # se quiser acessar a interface da rede, execute python run.py 0.0.0.0:8000
ctrl + b + d   # para minimizar o tmux
```

O processo a seguir será feito manualmente, mas haverá uma automatização no futuro. Em uma nova janela, execute cada comando bash a seguir, e, após cada um, rode o comando ctrl + b + d para minimizar o tmux que será aberto.

```
$ cd crawlers/scrapy-cluster/start-sc
$ ./1-start-redis.sh   # ctrl + b + d
$ ./2-start-km.sh      # ctrl + b + d
$ ./3-start-rest.sh     # ctrl + b + d
```

## Instalação e configuração de uma _slave_

Para a instalação do projeto em uma slave, basta clonar o repositório na branch issue-261-mp, criar um ambiente virtual python 3.6 e rodar o script install.py, que instala o projeto e as dependências do Scrapy Cluster.

```
$ git clone -b issue-261-mp https://github.com/MPMG-DCC-UFMG/C04.git
$ cd C04
$ python3.6 -m venv env
$ source env/bin/activate
$ python install.py
```

Após as instalações, é necessário iniciar as spiders. O projeto do Scrapy Cluster recomenda abrir de cinco a 10 por máquina. Para iniciá-las, vá para o diretório de crawler do scrapy cluster.

```
$ cd crawlers/scrapy-cluster/crawler/
```

Para inciar as n spiders, abra um tmux com um nome para a sessão (você pode nomear as sessões como, por exemplo, s1, s2, …, sn), execute a spider e, em seguida, minimize a sessão com o comando ctrl + b + d. Repita o processo n vezes:

```
$ tmux new -s <nome_da_sessão>
$ scrapy runspider crawling/spiders/static_page.py
ctrl + b + d   # para minimizar o tmux
```

## Remoção de uma _slave_

Para remover uma slave, basta fechar as spiders que estão rodando nela. Para isso, veja as sessões existentes naquela máquina e repita o processo a seguir até que não haja spiders:

```
$ tmux ls   # para ver as sessões ativas
$ tmux attach -t <nome_da_sessão>
ctrl + c   # para matar a spider
ctrl + b + d   # para minimizar o tmux
```

## Interface

Para usar a interface, basta acessar _http://localhost:8000/_

Se quiser acessar o programa através da rede, use o IP da máquina onde a interface está sendo executada (no caso, a _master_). Por exemplo, se a máquina onde você rodou o run.py tem endereço de IP _1.2.3.4_, e esse endereço é visível para sua máquina através da rede, você pode acessar _http://1.2.3.4:8000/_.

## Fluxo de interação com a interface
![Fluxograma](fluxo_interface_coletor_20200625.png)
