import time

from elasticsearch import Elasticsearch

if __name__ == '__main__':
    es_client = Elasticsearch(hosts='http://elasticsearch:9200')
    while True:
        if es_client.ping():
            print('es success')
            break
        time.sleep(1)
        print('es ping')
