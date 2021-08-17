# C01
Desenvolvimento de ferramentas para construção e manutenção de coletores de páginas da Web.

Existem coletores bases, que podem ser personalizados através da interface feita em django. Eles são capazes de coletar:

- Páginas estáticas
- Páginas dinâmicas ou onde é necessário interagir com formulários.
- Arquivos
- Conjunto de arquivos

Os coletores são desenvolvidos em Scrapy em conjunto com Pyppeteer para o caso de páginas dinâmicas. O gerenciamento dos coletores é feito com o Scrapy-cluster.

Dentre as funcionalidades disponíveis para os coletores, pode-se se citar, por exemplo:

- Mecanismos para camuflagem dos coletores, como rotação de endereço de IP e gerenciamento de cookies.
- Ferramentas para gerar endereços automaticamente através de templates
- Os coletores também podem ser gerenciados através de uma API RESTful.

Para que seja possível utilizar o sistema, e consequentemente configurar e executar coletores, é necessário inicialmente instalar a aplicação. Essa página se refere a essa etapa inicial. Preferencialmente, a instalação deve ser feita nativamente em sistemas baseados em Linux, contudo, através do Docker, é possível instalar o sistema em outros SO, como Windows. Portanto, se esse for o seu caso, foque nas instruções de instalação no final da página, na seção "Execução com Docker (standalone)". Futuramente, será possível realizar uma instalação distribuída do sistema, que ainda está sendo desenvolvida.


## Instalação
A primeira etapa para poder instalar o sistema é realizar o donwload de seu código-fonte. Para isso, utilize as ferramentas do GitHub para baixar o repositório localmente.

Em seguida, é importante notar que para usar o programa é necessário um _virtualenv_ ou uma máquina apenas com **Python 3.7+**, de maneira que os comandos _"python"_ referencie o Python 3.7+, e _"pip"_ procure a instalação de pacotes também do Python 3.7+. Assim, configure esse ambiente. Para mais informações de como criar e manter _virtualenvs_, o [seguinte material](https://docs.python.org/pt-br/3/library/venv.html) pode ajudar.

Além disso, alguns serviços necessitam que o Java esteja rodando no sistema, que pode ser instalado por 
```
sudo apt install default-jre  
```
Caso seu sistema não seja Linux, siga as instruções de instalação da Java Runtime para o seu sistema, as quais podem ser encontradas nesse [link](https://www.java.com/en/download/manual.jsp).

Para instalar todos os programas e suas dependências execute o script install.py.
```
python install.py
```
Esse script deve ser executado a partir da raiz do repositório. No final da execução, logs semelhantes a esses devem aparecer no seu terminal:

<img  src="https://drive.google.com/uc?export=view&id=1DXXS-CQyXThC4xlPYp-zquUctdDhphac" >

Se deseja instalar apenas algum dos módulos implementados, por exemplo, o módulo de extração de parâmetros de formulários, navegue até a pasta do módulo e execute pip install:
```
cd src/form-parser
pip install .
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

Assim que tiver executado e acesso pelo navegador, a seguinte página aparecerá:

<img  src="https://drive.google.com/uc?export=view&id=1pfvTCtLBCk7SIu8SprEL8cD5FQcojlZl" >

Mais informações de como utilizar a interface pode ser encontrado nas próximas páginas dessa Wiki.

## Execução com Docker (standalone)

Antes de tudo, assegure-se de que o Docker está devidamente instalado no seu computador. Caso precise de instruções de como fazer isso, o seguinte link pode auxiliar nesse processo: https://docs.docker.com/get-docker/

Para instalação do sistema é necessário montar a imagem a partir do Dockerfile, para isso execute o seguinte comando a partir da raiz do repositório:
```
sudo docker build -t c01 .
```

Para conseguir executar a imagem, é preciso criar o diretório "data" a partir da raiz do repositório, para isso, execute o comando:
```
mkdir data
```
Obs: Caso seu sistema não seja Linux, utilize o comando equivalente para criar diretório.

Em seguida, é necessário executar a imagem. Ainda na raiz do respositório execute o comando responsável por isso:
```
sudo docker run --mount type=bind,source="$(pwd)/data",target=/data -p 8000:8000 -t c01
```

O comando acima garante que o container terá acesso ao disco da máquina, e esse aceso foi feito através da ligação da raiz do respositório com a raiz da imagem. Ou seja, ao configurar coletores com o seguinte caminho "/data/nome_coletor", os dados estarão sendo salvos na verdade no seguinte diretório da máquina: "caminho_da_raiz_repositório>/data/nome_coletor". É possível alterar o diretório na máquina hospedeira, para isso, basta alterar o trecho "$(pwd)" do comando para o diretório desejado.
