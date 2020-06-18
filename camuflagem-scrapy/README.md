# antiblock-scrapy

Mecanismos antibloqueios para o Scrapy.

## Funcionalidades

Scrapy já vem com vários recursos antibloqueios que só precisam ser configurados, bem como muitos outros implementados por terceiros (alguns deles listados abaixo). 

Os recursos implementados foram:

- Rotacionador de user-agents
- Rotacionar de IPs via proxy Tor

## Instalação

Maneira mais fácil:

```bash
pip install antiblock-scrapy
```

## Instalação e configuração do Tor

É necessário configurar o **Tor**. Primeiramente, instale-o:

```bash
sudo apt-get install tor
```

Pare sua execução para realizar configurações:

```bash
sudo service tor stop
```

Abra seu arquivo de configuração como root, disponível em */etc/tor/torrc*, por exemplo, usando o nano:

```bash
sudo nano /etc/tor/torrc
```
Coloque as linhas abaixo e salve:

```
ControlPort 9051
CookieAuthentication 0
```

Reinicie o Tor:

```bash
sudo service tor start
```


É possível verificar o IP de sua máquina e comparar com o do Tor da seguinte forma:
- Para ver seu IP:
    ```bash
    curl http://icanhazip.com/
    ```
- Para ver o IP do TOR:
    ```bash
    torify curl http://icanhazip.com/   
    ```

Proxy do Tor não são suportados pelo Scrapy. Para contornar esse problema, é necessário o uso de um intermediário, nesse caso o **[Privoxy](https://www.privoxy.org/)**. 

> O servidor proxy do Tor se encontra, por padrão, no endereço 127.0.0.1:9050

### Instalação e configuração do **Privoxy**:
- Instalar: 
    ```bash
    sudo apt install privoxy
    ```
- Pare sua execução:
    ```bash
    sudo service privoxy stop
    ```
- Configurá-lo para usar Tor, abra seu arquivo de configuração:
    ```bash
    sudo nano /etc/privoxy/config
    ```
- Adicione as seguintes linhas:
    ```bash
    forward-socks5t / 127.0.0.1:9050 .
    ``` 
- Inicie-o: 
    ```
    service privoxy start
    ```

> Por padrão, privoxy executará no endereço 127.0.0.1:8118 

Teste: 
```bash
torify curl http://icanhazip.com/
```
```bash
curl -x 127.0.0.1:8118 http://icanhazip.com/
```
O IP mostrado nos dois passos acima deve ser o mesmo.

## Rotação de IPs via Tor

- Configure o middleware no arquivo de configuração de seu projeto (**settings.py**):
    ```python
    DOWNLOADER_MIDDLEWARES = {
        ...,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'antiblock_scrapy.middlewares.TorProxyMiddleware': 100
    }
    ```
    
- Habilite o uso da extensão:  
    ```python
    TOR_IPROTATOR_ENABLED = True
    TOR_IPROTATOR_CHANGE_AFTER = #número de requisições feitas em um mesmo endereço IP
    ```
Por padrão, um IP poderá ser reutilizado após 10 usos de outros. Esse valor pode ser alterado pela variável TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER, como abaixo:

```python
TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER = #
```

Um número grande demais pode tornar mais lento recuperar um novo IP para uso ou nem encontrar. Se o valor for 0, não haverá registro de IPs usados.

## Rotação de IPs via lista de proxies

Rotacionar IPs via Tor pode tornar o processo de coleta lento. Para isso existem ferramentas de terceiros que rotacionam uma lista de proxies dada, possivelmente deixando a coleta mais rápida (em comparação ao Tor), como:

- https://github.com/xiaowangwindow/scrapy-rotated-proxy
- https://github.com/TeamHG-Memex/scrapy-rotating-proxies

## Rotação de user-agents

- No arquivo de configuração de seu projeto Scrapy, adicione as seguintes linhas (**settings.py**):
    ```python
    DOWNLOADER_MIDDLEWARES = {
        ...,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'antiblock_scrapy.middlewares.RotateUserAgentMiddleware': 500,
    }
    ```
- Defina a lista de user-agents, ative o módulo e defina um uso mínimo e máximo de cada user-agent (o uso de um user-agent será aleatório entre esses números) (**settings.py**):
    ```python
    USER_AGENTS = ['user-agent-1', 'user-agent-2',...,'user-agent-n']
    ROTATE_USER_AGENT_ENABLED = True
    MIN_USER_AGENT_USAGE = #uso mínimo de user-agent
    MAX_USER_AGENT_USAGE = #uso máximo de user-agent
    ```

- É possível conferir o user-agent usado no site: https://www.whatismybrowser.com/detect/what-is-my-user-agent 

## Atrasos entre requisições

Essa funcionalidade já é disponível por padrão ao Scrapy por meio de [DOWNLOAD_DELAY](https://docs.scrapy.org/en/latest/topics/settings.html#download-delay).

Por padrão:
- O valor de DOWNLOAD_DELAY é de 0.25 segundos
- O tempo entre requisições não é fixo, um valor entre 0.5 * DOWNLOAD_DELAY e 1.5 * DOWNLOAD_DELAY é escolhido entre cada requisição

Para alterar o atraso entre requisição, faça (em **settings.py**):

```python
DOWNLOAD_DELAY = # tem em segundos entre requisições
```

Para forçar que o tempo entre requisições seja fixo, ao contrário do padrão aleatório, faça (em **settings.py**):
```python
RANDOMIZE_DOWNLOAD_DELAY = False
```
### AutoThrottle

Uma opção mais avançada de colocar atrasos entre requisições é o [AutoThrottle](https://docs.scrapy.org/en/latest/topics/autothrottle.html#autothrottle-extension). Ela alterará a velocidade entre requisições de acordo com a latência de resposta do servidor e a capacidade de processamento da engine de maneira automática.  

Por padrão, essa configuração está desativada. Mas pode ser ativada por meio do seguinte comando (em **settings.py**):

```python
AUTOTHROTTLE_ENABLED = True
```

É necessário definir um delay inicial que será ajustado ao longo das requisições automaticamente. Defina-o por meio do comando abaixo, o default de 5.0 segundos (em **settings.py**):

```python
AUTOTHROTTLE_START_DELAY = #delay inicial  
```

Defina também um delay máximo, o default de 60.0 segundos (em **settings.py**):

```python
AUTOTHROTTLE_MAX_DELAY = #delay máximo
```

O atraso das próximas requisições será ajustado para um valor respeitando DOWNLOAD_DELAY e AUTOTHROTTLE_MAX_DELAY, levando em conta a média de requisições paralelas enviadas ao servidor que, por padrão, é 1.0. Esse valor pode ser ajustado pelo comando abaixo (em **settings.py**): 

```python
AUTOTHROTTLE_TARGET_CONCURRENCY = #média de requisições concorrentes
```

Mais detalhes podem ser encontrados [aqui](https://docs.scrapy.org/en/latest/topics/autothrottle.html#throttling-algorithm).

## Gerenciamento de cookies

Scrapy já possui mecanismos de gerencialmente de cookies e detalhes podem ser encontrados [aqui](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.cookies).

Por exemplo, caso possua os cookies de acesso de um site que é necessário login, uma das possíveis abordagens é criar um Spider como o abaixo:

```python

import scrapy

# Cookies de login do site
COOKIES = [{},..., {}]

class LoginSpider(scrapy.Spider):
    name = 'foo'

    def start_requests(self):
        urls = ['site-com-login-1', 'site-com-login-2', ..., 'site-com-login-n']
        for url in urls:
            yield scrapy.Request(url='site-que-precisa-login', cookies=COOKIES, callback=self.parse)

    def parse(self, response):
        ...
```

Outras formas de lidar com cookies como, por exemplo, cada requisição com seu próprio cookie, podem ser feitas usando **cookiejar**, mais detalhes [aqui](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.cookies). 

Bibliotecas de terceiros permitem **persistência de cookies** e outros recursos, como [scrapy-cookies](https://scrapy-cookies.readthedocs.io/en/latest/intro/overview.html).  