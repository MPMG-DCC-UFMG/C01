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

## Instalação

Para instalar todos os programas e suas dependencias execute o script install.py. Esse programa requer python>=3.6 e a instalação de pacotes usando pip.
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
python manage.py runserver
```

E então basta acessar _http://localhost:8000/_

## Fluxo de interação com a interface
![Fluxograma](fluxo_interface_coletor_20200625.png)
