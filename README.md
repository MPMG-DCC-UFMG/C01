# C04

Desenvolvimento de ferramentas para construção e manutenção de coletores de páginas da Web. (Em desenvolvimento)

## TODO

- [ ] Testes em máquinas diferentes
- [ ] Suporte a templated URLs
- [ ] Atualização da interface para gerir os spiders distribuídos
- [ ] Suporte a páginas dinâmicas
- [ ] Iniciação automáticas dos serviços

## Coletas distribuídas

Siga os passos abaixo para o correto funcionamento.

Para iniciar a interface:

- Crie um ambiente virtual com **python 3.7**: `python3.7 -m venv venv`
- Ative o ambiente virtual: `source venv/bin/activate`
- Instale as dependências: `python install.py`
- Inicie o Zookeeper, Kafka e Redis (a partir da pasta corrente)
    - Zookeeper: `kafka_2.13-2.4.0/bin/zookeeper-server-start.sh kafka_2.13-2.4.0/config/zoo.properties`
    - Kafka: `kafka_2.13-2.4.0/bin/kafka-server-start.sh kafka_2.13-2.4.0/config/server.properties`
    - Redis: `./redis-5.0.10/src/redis-server`
- Inicie a interface: `python manage.py runserver --noreload`
    - `--noreload` garantirá que o Django não criará mais de uma instâncias de objetos que precisam ser únicos (consumidores Kafka, se não as mensagens ficam duplicadas)

Para iniciar os gerenciadores de spiders:
- Vá para a pasta `spider_manager`: `cd spider_manager/`
- Crie um ambiente virtual **python 3.6**: `python3.6 -m venv venv`
- Inicie o ambiente virtual: `source venv/bin/activate`
- Vá para a pasta `src`: `cd src/`
- Instale as dependências: `pip install -U pip & pip install -r requirements.txt`
- Execute o listener de comandos: `python command_listener.py`
    - Para ter mais de uma instância de spider executando para uma mesma coleta, inicie mais processos de `command_listener`

   
<!-- 
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

## Instalação

Para usar o programa é necessário um _virtualenv_ ou uma máquina apenas com **Python 3.7+**, de maneira que os comandos _"python"_ referencie o Python 3.7+, e _"pip"_ procure a instalação de pacotes também do Python 3.7+.

Alguns serviços necessitam que o Java esteja rodando no sistema, o mesmo pode ser instalado por 
```
sudo apt install default-jre  
```

Para instalar todos os programas e suas dependencias execute o script install.py.
```
python install.py
```

Se deseja instalar apenas algum dos módulos implementados como o módulo de extração de parâmetros de formulários, navegue até a pasta do módulo e execute pip install:
```
cd src/form-parser
pip install .
```

## Execução

Para execução da interface basta executar o seguinte comando:
```
python run.py
```

E então basta acessar _http://localhost:8000/_

Se quiser acessar o programa através da rede, execute:
```
python run.py 0.0.0.0:8000
```
E então use o IP da máquina onde a interface está sendo executada para acessá-la. Por exemplo, se a máquina onde você rodou o comando acima tem endereço de IP _1.2.3.4_, e esse endereço é visível para sua máquina através da rede, você pode acessar _http://1.2.3.4:8000/_.


## Execução com Docker (standalone)

Antes de tudo, assegure-se de que o Docker está devidamente instalado no seu computador. Caso precise de instruições de como fazer isso, o seguinte link pode auxiliar nesse processo: https://docs.docker.com/get-docker/

Para instalação do sistema é necessário montar a imagem a partir do Dockerfile, para isso execute o seguinte comando a partir da raiz do repositório:
```
sudo docker build -t c01 .
```

Em seguida, é necessário executar a imagem. Ainda na raiz do respositório execute o comando responsável por isso:
```
sudo docker run --mount type=bind,source="$(pwd)/data",target=/data -p 8000:8000 -t c01
```

O comando acima garante que o container terá acesso ao disco da máquina, e esse aceso foi feito através da ligação da raiz do respositório com a raiz da imagem. Ou seja, ao configurar coletores com o seguinte caminho "/data/nome_coletor", os dados estarão sendo salvos na verdade no seguinte diretório da máquina: "caminho_da_raiz_repositório>/data/nome_coletor". É possível alterar o diretório na máquina hospedeira, para isso, basta alterar o trecho "$(pwd)" do comando para o diretório desejado.

Ao final do processo, basta acessar _http://localhost:8000/_


## Fluxo de interação com a interface
![Fluxograma](fluxo_interface_coletor_20200625.png) -->
