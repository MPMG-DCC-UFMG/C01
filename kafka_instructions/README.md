# Instruções para uso do Kafka
Esse documento objetiva instruir a instalação e a configuração manual do Kafka para cobrir novas dependências do sistema, possibilitando o funcionamento do novo sistema de logs. Note que essa se trata de uma solução **TEMPORÁRIA**, já que em breve construiremos uma maneira mais elegante e automática de garantirmos a instalação e a atualização dessas e de outras dependências.

## Dependências
###Java
O Apache Kafka necessita do Java para funcionar. Caso não esteja instalado em sua máquina, siga as instruções no link abaixo correspondentes ao seu sistema operacional:
https://openjdk.java.net/install/

### Download do Kafka (versão 2.5.0)
Para baixar o Kafka na versão especificada, basta seguir esse link:
https://downloads.apache.org/kafka/2.5.0/kafka-2.5.0-src.tgz

- **Nota:** a versão 2.5.0 não é a mais recente da ferramenta. Optamos por essa versão por já ter sido testada no desenvolvimento do sistema de logs. Dessa forma, os scripts de inicialização foram construídos baseados nessa versão. Caso opte por usar outras versões (disponíveis [neste link](http://https://kafka.apache.org/downloads "neste link") ), é possível simplesmente alterar algumas linhas de código do` run.py` para fazê-las funcionar.

## Uso no sistema
### Passos:
**1.** Faça a extração da pasta `kafka-2.5.0-src`, armazenando-a **na raiz do projeto**.

**2.** Agora, vamos realizar uma simples alteração das configurações do Zookeeper (uma das dependências da execução do Kafka). Na pasta que contém esse documento de instruções (`kafka_instructions`), temos o arquivo `zoo.properties`. Esse arquivo deve ser inserido no diretório **`kafka-2.5.0-src/config`**.
- **Nota:** essa alteração se trata apenas da mudança do armazenamento dos dados do Zookeeper para um diretório em que o projeto tenha permissão para deletá-lo. Essa configuração se mostrou necessária na execução correta do sistema no contexto de desenvolvimento. Provavelmente será retirada na versão de produção.

**3. ** Execute o script `install.py` para que seja instalado o `kafka-python`, o cliente Python para a ferramenta. Para mais informações, visite [este link](http://https://kafka-python.readthedocs.io/en/master/ "este link").

Realizando esses passos, o sistema deve estar apto para ser iniciado normalmente: ao executar o script `run.py`, os servidores do Zookeeper e do Kafka serão iniciados automaticamente com o projeto.
