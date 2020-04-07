# Módulo responsável por camuflar coletores
De maneira geral, webdrivers do Selenium ou sessões da biblioteca Requests são especializados para rotacionar IPs, controlar número de requisições por tempo, introduzir aleatoriedade, rotacionar User-Agents, evitar Honeypots, etc.   

## Rotação de IPs
Pode ser feito de duas formas, usando o Tor ou passando uma lista de servidores proxies a serem usados. 

Caso se use o Tor, é necessário que ele esteja instalado, configurado e ter acesso **root**. Para isso, faça:

Instale o Tor:
> sudo apt-get install tor

Acesse seu arquivo de configuração:
> sudo nano /etc/tor/torrc

E adicione as linhas abaixo:
> ControlPort 9051

> CookieAuthentication 1

(Em construção)
