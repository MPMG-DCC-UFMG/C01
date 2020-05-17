# Módulo de camuflagem para Scrapy

Existem muitos módulos já disponíveis para o Scrapy para camuflagem dos coletores seja por terceiros ou por alterando suas configurações disponíveis. 

Os módulos tor_ip_rotator e user_agent_rotator foram desenvolvidas para que sejam mais personalizados que outras opções de terceiros já disponíveis. O primeiro trata-se de um rotacionador de IP via proxy Tor, enquanto o segundo para rotacionar user-agents. Ambos foram empacotados e publicados no gerenciador de pacotes Python [Pypi](https://pypi.org/) no intuito de facilitar seu uso. Mais detalhes estão disponíveis nos respectivos módulos.

Outras maneiras de se evitar que os coletores sejam detectados são possíveis alterando as configurações do Scrapy, como as abaixo.

### Controlar número de requisições por tempo

É possível definir um valor em segundos, por meio de [DOWNLOAD_DELAY](https://docs.scrapy.org/en/latest/topics/settings.html#download-delay) no arquivo de configuração, para controlar o tempo entre uma requisição e outra ao servidor. Em **settings.py**, adicione a seguinte linha:

```python
DOWNLOAD_DELAY = #tempo em segundos entre uma requisição e outra
```

Por padrão, o tempo entre uma requisição e outra não é fixo. Um valor entre 0.5 * DOWNLOAD_DELAY e 1.5 * DOWNLOAD_DELAY é escolhido aleatoriamente. Essa configuração pode ser desativada por meio de (em **settings.py**):

```python
RANDOMIZE_DOWNLOAD_DELAY = False
```

Porém ela é recomendada por dificultar a detecção de robôs, uma vez que usa aleatoriedade.

Outra funcionalidade interessante é a [AutoThrottle](https://docs.scrapy.org/en/latest/topics/autothrottle.html#autothrottle-extension). Ela alterará a velocidade entre requisições de acordo com a latência de resposta do servidor e a capacidade de processamento da engine de maneira automática.  

Por padrão, essa configuração está desativada. Mas pode ser ativada por meio do seguinte comando (em **settings.py**):

```python
AUTOTHROTTLE_ENABLED = True
```

É necessário definir um delay inicial que será ajustado ao longo das requisições automaticamente. Defina-o por meio do comando abaixo ou não para usar o default de 5.0 segundos (em **settings.py**):

```python
AUTOTHROTTLE_START_DELAY = #delay inicial  
```

Defina também um delay máximo ou não, se preferir usar o default de 60.0 segundos (em **settings.py**):

```python
AUTOTHROTTLE_MAX_DELAY = #delay máximo
```

O delay das próximas requisições serão ajustadas para um valor respeitando DOWNLOAD_DELAY e AUTOTHROTTLE_MAX_DELAY, levando em conta a média de requisições paralelas enviadas ao servidor que, por padrão, é 1.0. Esse valor pode ser ajustado pelo comando abaixo (em **settings.py**): 

```python
AUTOTHROTTLE_TARGET_CONCURRENCY = #média de requisições concorrentes
```

Mais detalhes podem ser encontrados [aqui](https://docs.scrapy.org/en/latest/topics/autothrottle.html#throttling-algorithm).

### Proxies de terceiros
Caso seja útil proxies que não sejam via Tor, já há opções para uso, como:
- https://github.com/xiaowangwindow/scrapy-rotated-proxy
- https://github.com/TeamHG-Memex/scrapy-rotating-proxies

Nesse caso, uma lista de proxies deverão ser passadas para que os mecanismos funcionem.

### Gerenciamento de cookies

Scrapy já possui mecanismos de gerencialmente de cookies e detalhes podem ser encontrados [aqui](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.cookies).