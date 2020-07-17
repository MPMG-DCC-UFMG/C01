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

## Dependencias

É necessário instalar alguns pacotes para o funcionamento da interface. TODO: melhorar lista de dependencias

Dependências que vão deixar o programa rodar incorretamente e não te avisar:

```
pip install scrapy-selenium
pip install scrapy-rotated-proxy
```

## Execução
Antes da primeira execução é necessário criar o banco de dados que vai ser usado pela aplicação. Para isso execute:

```
python manage.py makemigrations main
python manage.py migrate
```

Para execução da interface então basta:

```
python manage.py runserver
```

A aplicação irá executar na porta 8000 por default (http://127.0.0.1:8000/).

## Fluxo de interação com a interface
![Fluxograma](fluxo_interface_coletor_20200625.png)
