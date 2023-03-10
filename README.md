# C01
Desenvolvimento de ferramentas para construção e manutenção de coletores de páginas da Web. O sistema é capaz de coletar:

## Status atual

Os coletores são desenvolvidos em Scrapy em conjunto com Playwright para o caso de páginas dinâmicas. Dentre as funcionalidades disponíveis para os coletores, pode-se se citar, por exemplo:
## Instalação
Antes de tudo, assegure-se de que o Docker está devidamente instalado no seu computador. Caso precise de instruções de como fazer isso, o seguinte link pode auxiliar nesse processo: https://docs.docker.com/get-docker/

A primeira etapa para poder instalar o sistema é realizar o donwload de seu código-fonte. Para isso, utilize as ferramentas do GitHub para baixar o repositório localmente.

Para instalar pela primeira vez todos os programas e suas dependências execute o script install.py.
```
python clean_install.py
```
Esse script deve ser executado a partir da raiz do repositório.


Após o primeiro clone e instalação, se deseja instalar as modificações no sistema (incluidas em novos commits), deve realizar uma atualização do branch local, através de comandos git, e em seguida, executar:
```
python install.py
```

## Execução

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

Ao final da execução, deve-se desligar o sistema através do comando:

```
python stop.py
```

Por fim, para acessar os documentos coletados, ao configurar coletores com o seguinte caminho "nome_coletor", os dados estarão sendo salvos na verdade no seguinte diretório da máquina: "caminho_da_raiz_repositório>/data/nome_coletor".
