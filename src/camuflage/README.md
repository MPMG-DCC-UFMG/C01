# antiblock-selenium
Chrome e Firefox selenium webdrivers com alguns mecanismos antibloqueios.  

## Recursos

* Rotação de IPs via Tor
* Rotação de user-agents (Apenas para Firefox)
* Delays aleatórios ou fixos entre requisições
* Persistência e carregamento de cookies
    * Permite salvar informações de login, por exemplo 

## Instalação

A maneira mais simples:

```bash
pip install antiblock-selenium
```

### Configurando Tor

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

## Uso

As classes **Firefox** e **Chrome** de **antiblock_selenium** herdam de selenium.webdriver.Firefox e selenium.webdriver.Chrome, respectivamente. Então as use como habitualmente. 

**Uso básico**

```python
from antiblock_selenium import Firefox, Chrome

chrome = Chrome()
firefox = Firefox()

#use os drivers como habitualmente faz com webdrivers
```

As funcionalidades extras a estes webdrivers são listadas abaixo. 

### Rotacionar IPs via Tor
**Parâmetros de configuração**:

* **allow_reuse_ip_after**: Tipo **Int** - default **10**. Quando um IP é usado, ele poderá ser reusado novamente após allow_reuse_ip_after outros IPs serem usados. Se o número for 0, um IP pode ser reusado em qualquer momento. 
* **change_ip_after**: Tipo **Int** - default **42**. Número de requisições feitas por um mesmo IP.

Exemplo:

```python
from antiblock_selenium import Firefox, Chrome

chrome = Chrome(allow_reuse_ip_after = 5, change_ip_after = 100)
firefox = Firefox(allow_reuse_ip_after = 5, change_ip_after = 100)

# use chrome/firefox como habitualmente usa os webdrivers
```

### Rotacionar user-agents

Por enquanto, funcionalidade disponível apenas para Firefox.

**Parâmetros de configuração**:
- **user_agents**: Tipo **List** - default [] (lista vazia). Lista de user-agents para ser rotacionada.
- **change_user_agent_after**: Tipo **Int** - default 0. Número de requisições feitas com o mesmo user-agent. Se o valor for 0, o user-agent não será alterado.

Exemplo:

```python
from antiblock_selenium import Firefox

user_agents = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
  ]

firefox = Firefox(user_agents = user_agents, change_user_agent_after = 100)

#use firefox como habitualmente usa webdrivers 
...
```

### Delays aleatórios ou fixos

Por padrão, o atraso entre uma requisição e outra é uma valor escolhido ao acaso entre 0.5 * 0.25 e 0.25 * 1.5, o mesmo comportamento do Scrapy.

**Parâmetros de configuração**:
- **time_between_calls**: Tipo **Float** - default 0.25. Tempo em segundos entre uma requisição e outra. 
- **random_delay**: Tipo **Bool** - default True. Se True, um valor entre 0.5 * time_between_calls e 1.5 * time_between_calls será o delay escolhido entre cada requisição. Se False, o delay entre uma requisição e outra será fixo de time_between_calls segundos.

Exemplo:

```python
from antiblock_selenium import Firefox, Chrome

# Tempo fixo de 10 segundos entre requisições
chrome = Chrome(time_between_calls = 10, random_delay = False)

# Tempo aleatório entre 0.5 * 10 e 1.5 * 10 entre cada requisição
firefox = Firefox(time_between_calls = 10, random_delay = True)

# use chrome/firefox como habitualmente usa os webdrivers
```

### Persistência e carregamento de cookies

O selenium já possui mecanismos de gerenciamentos de cookies, disponíveis [aqui](https://www.selenium.dev/documentation/en/support_packages/working_with_cookies/). As funcionalidades abaixo são apenas facilitadores de uso, sendo:

- Salvar cookies ao fechar o driver
- Recarregar os últimos cookies salvos (salvos de uma última sessão do driver)
- Carregar uma lista de cookies

**Parâmetros de configuração**:

- **cookie_domain**: Tipo **String** - default ''. Para carregar cookies, o selenium precisa acessar o site onde os cookies são válidos. Esse parâmetro representa esse site.
- **persist_cookies_when_close**: Tipo **Bool** - default False. Define se os cookies do driver serão salvos quando ele for fechado.
- **reload_cookies_when_start**: Tipo **Bool** - default False. Define se os cookies salvos de uma outra sessão do driver que foi fechada será recarregada. **Se esse parâmetro for True, cookie_domain não pode ser vazio**.
- **location_of_cookies**: Tipo **String** - default 'cookies.pkl'. Nome ou local onde os cookies serão salvos, se persist_cookies_when_close for definido como True.

Exemplo:

```python
from antiblock_selenium import Firefox, Chrome

chrome = Chrome(persist_cookies_when_close = True)
firefox = Firefox(persist_cookies_when_close = True)

chrome.get('algum-site-que-requer-login')
firefox.get('algum-site-que-requer-login')

#Preencha os dados de login

chrome.close()
firefox.close()

chrome = Chrome(reload_cookies_when_start = True, cookie_domain = 'https://dominio-site-com-login.com')
firefox = Firefox(reload_cookies_when_start = True, cookie_domain = 'https://dominio-site-com-login.com')

```
Nem todos sites será possível salvar informação de login apenas salvando cookies.

Também é possível carregar uma lista de cookies para um domínio, use a função abaixo:

- **load_cookies**
    - Parâmetros: 
        - **cookies**: Tipo **List**. Lista de cookies.
        - **cookie_domain**: Tipo **String**. Domínio válido do cookie.

Exemplo:

```python
from antiblock_selenium import Firefox, Chrome

chrome = Chrome()
firefox = Firefox()

cookies = [{'domain': 'www.google.com.br', 'expiry': 1591216842, 'httpOnly': False, 'name': 'UULE', 'path': '/', 'secure': False, 'value': 'a+cm9sZToxIHByb2R1Y2VyOjEyIHByb3ZlbmFuY2U6NiB0aW1lc3RhbXA6MTU5MTE5NTIzNzI5OTAwMCBsYXRsbmd7bGF0aXR1ZGVfZTc6NDY4MTgxODgwIGxvbmdpdHVkZV9lNzo4MjI3NTEyMH0gcmFkaXVzOjY0MDg4Nzgw'}, {'domain': '.google.com.br', 'expiry': 2145916801, 'httpOnly': False, 'name': 'CONSENT', 'path': '/', 'secure': False, 'value': 'WP.287758'}, {'domain': '.google.com.br', 'expiry': 1593787242, 'httpOnly': False, 'name': '1P_JAR', 'path': '/', 'secure': True, 'value': '2020-6-3-14'}, {'domain': '.google.com.br', 'expiry': 1607006421, 'httpOnly': True, 'name': 'NID', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '204=aZfE182RJB7HoA9WXJImPNFy4xT0-VCU9t2NhB8byzsMGdSdjnDQo7YkIexDtBsMKQxU0AZDfgyQkKn8T9rD8YN_3hqpIvasJRbg75GZzt8zYTO3dMgS7G1ftELWBzDAuhRb2bCa1iKwut2YfNYJp-2bshYcX0JD5RDW_Gp28Bc'}]


chrome.load_cookies(cookies = cookies, cookie_domain = 'https://www.google.com.br/')

firefox.load_cookies(cookies = cookies, cookie_domain = 'https://www.google.com.br/')

```

## TO-DO

- Rotação de user-agents para Chrome
- Rotação de IPs via lista de proxys
- Aumentar cobertura de testes