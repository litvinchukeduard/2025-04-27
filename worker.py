import json

import pika
from pymongo import MongoClient

credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters)
rabbit_channel = connection.channel()

CONNECTION_STRING = "mongodb://localhost:27017"
mongo_client = MongoClient(CONNECTION_STRING)
mongo_db = mongo_client['website_visitors']
visitors_collection = mongo_db['visitors']

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    client_info = json.loads(body)
    visitor_in_db = visitors_collection.find_one({"ip": client_info['ip']})
    if visitor_in_db is None:
        visitors_collection.insert_one(client_info)

rabbit_channel.basic_consume(queue='visit_queue',
                      auto_ack=True,
                      on_message_callback=callback)

rabbit_channel.start_consuming()