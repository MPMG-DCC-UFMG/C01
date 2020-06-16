# antiblock_scrapy_selenium

Este módulo é uma extensão para o projeto de [scrapy-selenium](https://github.com/clemfromspace/scrapy-selenium). 

O principal uso do **scrapy-selenium** é para o caso de sites que precisam processar javascript para renderizar seu conteúdo. Por outro lado, mecanismos antibloqueios básicos de coletas não se encontram no projeto original.

Scrapy-selenium foi extendido usando como base [antiblock-selenium](https://github.com/elvesrodrigues/antiblock-selenium), que permite rotacionar IPs via Tor, definir delays entre requisições (aleatório ou fixo), rotacionar user-agents, além de persistir/carregar cookies.

**Obs.: Não há compatibilidade com selenium remoto neste projeto.** 

## Funcionalidades

Junção de **scrapy-selenium** com **antiblock-selenium**, ou seja:

- Permitir carregar sites que necessitam javascript ao Scrapy, entre outras funcionalidades do **scrapy-selenium**
- Evitar bloqueios em coletas, por meio de:
    - Rotação de IPs via Tor
    - Rotação de user-agents
    - Delays aleatórios ou fixos entre requisições
    - Persistir/carregar cookies

## Instalação

Maneira mais fácil:

```bash
pip install antiblock-scrapy-selenium
```
## Configuração

Siga os passos de configuração do Tor em [antiblock-selenium](https://github.com/elvesrodrigues/antiblock-selenium#configurando-tor).

Os navegadores suportados são:
- Chrome
- Firefox


## Uso

### Básico

- Ativação do Middleware: 
    ```bash
    DOWNLOADER_MIDDLEWARES = {
        'antiblock_scrapy_selenium.SeleniumMiddleware': 800
    }
    ```
- Adicione o navegador a ser usado, o local da executável do driver e os argumentos a serem passados:
    ```python
    #settings.py
    from shutil import which

    SELENIUM_DRIVER_NAME = 'firefox' #ou chrome
    SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
    SELENIUM_DRIVER_ARGUMENTS=['-headless']  # '--headless' se estiver usando chrome
    ```
- Opcionalmente, defina o local da executável do navegador:
    ```python
    SELENIUM_BROWSER_EXECUTABLE_PATH = which('firefox')
    ```
- Use `antiblock_scrapy_selenium.SeleniumRequest` ao invés de `Request` do Scrapy, como abaixo:
    ```python 
    from antiblock_scrapy_selenium import SeleniumRequest

    yield SeleniumRequest(url=url, callback=self.parse_result)
    ```
    - Exemplo com um Spider:
        ```python
        import scrapy

        from antiblock_scrapy_selenium import SeleniumRequest

        class FooSpider(scrapy.Spider):
            name = 'foo'
            
            def start_requests(self):
                url = 'https://alguma-url'

                yield SeleniumRequest(url=url, callback=self.parse)

            def parse(self, response):
                pass
        ```
- Utilize as demais funcionalidades do `scrapy-selenium` normalmente, disponíveis [aqui](https://github.com/clemfromspace/scrapy-selenium#additional-arguments).

> **O parâmetro SELENIUM_COMMAND_EXECUTOR do scrapy-selenium não é suportada.**

### Uso de mecanismos antibloqueios

Após seguir os passos de uso básico, configure de acordo com os mecanismos de camuflagem abaixo.

#### Rotação de IPs via Tor
Parâmetros:

- `SELENIUM_DRIVER_CHANGE_IP_AFTER`: Define com quantas requisições o IP será alterado `(Default 42)`
- `SELENIUM_DRIVER_ALLOW_REUSE_IP_AFTER`: Define quando um IP poderá ser reusado `(Default 10)`

Exemplo:

```python
SELENIUM_DRIVER_CHANGE_IP_AFTER = 42
SELENIUM_DRIVER_ALLOW_REUSE_IP_AFTER = 5
```

#### Rotação de user-agents

> Suporte a rotação de user-agent apenas para Firefox.

Parâmetros:

- `SELENIUM_DRIVER_USER_AGENTS`: Lista de user-agents a ser rotacionada.
- `SELENIUM_DRIVER_CHANGE_USER_AGENT_AFTER`: Quando o user-agent deverá se alterado `(Default 0 - user-agent não muda)`

Exemplo:

```python
# settings.py

SELENIUM_DRIVER_USER_AGENTS = ['user-agent-1', 'user-agent-2', ... , 'user-agent-n']
SELENIUM_DRIVER_CHANGE_USER_AGENT_AFTER = 721 #Requisições com mesmo user-agent Ex.: 10, 20, 30... 
```

#### Atrasos entre requisições

Permite atrasos aleatórios ou fixos entre requisições.

Parâmetros:

- `SELENIUM_DRIVER_TIME_BETWEEN_CALLS`: Tempo em segundos entre requisições. Aceita números com até 2 duas casas decimais `(Default 0.25)`
- `SELENIUM_DRIVER_RANDOM_DELAY`: Se o atraso entre requisições será fixo (definindo esse parâmetro como `False`) ou aleatório, escolhido entre `0.5 * SELENIUM_DRIVER_TIME_BETWEEN_CALLS` e `1.5 * SELENIUM_DRIVER_TIME_BETWEEN_CALLS` `(Default True)`

```python
# settings.py

SELENIUM_DRIVER_TIME_BETWEEN_CALLS = 2.5
SELENIUM_DRIVER_RANDOM_DELAY = False # Tempo mínimo fixo entre requisições
```

#### Gerência de Cookies

Parâmetros:
- `SELENIUM_DRIVER_PERSIST_COOKIES_WHEN_CLOSE`: Se quando o driver é fechado os cookies deles serão salvos `(Default False)`
- `SELENIUM_DRIVER_RELOAD_COOKIES_WHEN_START`: Se ao iniciar, cookies salvos na última sessão serão recarregados `(Default False)`
    - Se `True`, é necessário especificar o domínio dos cookies em `SELENIUM_DRIVER_COOKIE_DOMAIN` 
- `SELENIUM_DRIVER_LOCATION_OF_COOKIES`: Local onde os cookies serão salvos. `(Default 'cookies.pkl')` 
- `SELENIUM_DRIVER_LOAD_COOKIES`: Lista de cookies a serem carregados (Default [] - Lista vazia)
    - Se a lista não vazia for passada, é necessário especificar o domínio dos cookies em `SELENIUM_DRIVER_COOKIE_DOMAIN` 
- `SELENIUM_DRIVER_COOKIE_DOMAIN`: Domínio onde os cookies são válidos.  

Exemplo - Persistindo cookies:

```python
# settings.py

SELENIUM_DRIVER_PERSIST_COOKIES_WHEN_CLOSE = True
SELENIUM_DRIVER_RELOAD_COOKIES_WHEN_START = True
SELENIUM_DRIVER_COOKIE_DOMAIN = 'https://www.site-sendo-coletado.com/'

SELENIUM_DRIVER_LOCATION_OF_COOKIES = 'cookies-1.pkl'
```
Exemplo - Carregando cookies:

```python

cookie1 = {'country': 'BR', 'currency': 'dolar'}
cookie2 = {'lang': 'pt-br'}

SELENIUM_DRIVER_LOAD_COOKIES = [cookie1, cookie2]
SELENIUM_DRIVER_COOKIE_DOMAIN = 'https://www.site-sendo-coletado.com/' 
```