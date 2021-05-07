# Spider Manager

[EXPERIMENTAL]

Para executar:

- Criar a imagem: `sudo docker image build . -t spider_manager`
- Certifique-se que o `Zookeeper`, `Kafka`, `Redis`, `Kafka-Monitor (Scrapy-Cluster)` e `Rest (Scrapy-Cluster)`.
- Rodar o container: `sudo docker container run -i --network="host" spider_manager`