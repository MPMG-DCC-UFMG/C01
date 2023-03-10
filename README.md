# C01
Desenvolvimento de ferramentas para construção e manutenção de coletores de páginas da Web. O sistema é capaz de coletar:

- Páginas estáticas
- Páginas dinâmicas ou onde é necessário interagir com formulários.
- Arquivos
- Conjunto de arquivos

Os coletores são desenvolvidos em Scrapy em conjunto com Playwright para o caso de páginas dinâmicas. Dentre as funcionalidades disponíveis para os coletores, pode-se se citar, por exemplo:

- Mecanismos para camuflagem dos coletores, como rotação de endereço de IP e gerenciamento de cookies.
- Ferramentas para gerar endereços automaticamente através de templates
- Os coletores também podem ser gerenciados através de uma API RESTful.

Para que seja possível utilizar o sistema, e consequentemente configurar e executar coletores, é necessário inicialmente instalar a aplicação. Essa página se refere a essa etapa inicial. Preferencialmente, a instalação deve ser feita nativamente em sistemas baseados em Linux, contudo, através do Docker, é possível instalar o sistema em outros SO, como Windows.

## Instalação
Antes de tudo, assegure-se de que o Docker está devidamente instalado no seu computador. Caso precise de instruções de como fazer isso, o seguinte link pode auxiliar nesse processo: https://docs.docker.com/get-docker/

A primeira etapa para poder instalar o sistema é realizar o donwload de seu código-fonte. Para isso, utilize as ferramentas do GitHub para baixar o repositório localmente.

Para instalar pela primeira vez todos os programas e suas dependências execute o script clean_install.py.
```
python clean_install.py
```
Esse script deve ser executado a partir da raiz do repositório.


Após o primeiro clone e instalação, se deseja instalar as modificações no sistema (incluidas em novos commits), deve realizar uma atualização do branch local, através de comandos git, e em seguida, executar:
```
python install.py
```

## Execução

Para execução da interface basta executar o seguinte comando:
```
python run.py
```
E em seguida acessar _http://localhost:8000/_

Se quiser acessar o programa através da rede, execute:
```
python run.py 0.0.0.0:8000
```
E então use o IP da máquina onde a interface está sendo executada para acessá-la. Por exemplo, se a máquina onde você rodou o comando acima tem endereço de IP _1.2.3.4_, e esse endereço é visível para sua máquina através da rede, você pode acessar _http://1.2.3.4:8000/_. Essa execução só dará certo se a máquina estiver com o acesso externo desse IP liberado, caso contrário, não será possível acessar o sistema remotamente.

Mais informações de como utilizar a interface pode ser encontrado nas próximas páginas dessa Wiki.

Ao final da execução, deve-se desligar o sistema através do comando:

```
python stop.py
```

Por fim, para acessar os documentos coletados, ao configurar coletores com o seguinte caminho "nome_coletor", os dados estarão sendo salvos na verdade no seguinte diretório da máquina: "caminho_da_raiz_repositório>/data/nome_coletor".
