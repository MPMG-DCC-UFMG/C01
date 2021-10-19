from datetime import date, datetime
from kafka import KafkaConsumer
import ujson

if __name__ == '__main__':
    consumer = KafkaConsumer('crawler_ufmg.scrapy_cluster.crawled_firehose',
                            bootstrap_servers=['localhost:9092'],
                            auto_offset_reset='earliest',
                            value_deserializer=lambda m: ujson.loads(m.decode('utf-8')))

    it = 1
    print('...')
    for message in consumer:
        now = datetime.now() 
        print(f'[{now}] Message received ({it})')