from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

import redis
from pymongo import MongoClient
import pika
'''
Написати додаток-вебсайт, який:

    1) Рахувати кількість відвідувачів
    2) Виводити декілька останніх унікальних відвідувачів
        2.1) Зберігати поточного відвідувача
        2.2) Діставати певну кількість унікальних відвідувачів


ip_address: 192.168.0.1
timestamp: 2025.04.27 20:18

{
    "ip": "192.168.0.1",
    "timestamp": "2025.04.27 20:18"
}

http server

redis
mongo
rabbitmq
'''

redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)

CONNECTION_STRING = "mongodb://localhost:27017"
mongo_client = MongoClient(CONNECTION_STRING)
mongo_db = mongo_client['website_visitors']
visitors_collection = mongo_db['visitors']

credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters)
rabbit_channel = connection.channel()

# item_1 = {
#     "ip": "192.168.0.1",
#     "timestamp": "2025.04.27 20:18"
# }

# visitors_collection.insert_one(item_1)
# visitors_count = 0

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        # global visitors_count
        # visitors_count += 1
        visitors_count = redis_connection.incr("visitors_count", amount=1)

        # client_ip = self.client_address[0]
        # current_timestamp = str(datetime.now())

        # user_info = {
        #     "ip": self.client_address[0],
        #     "timestamp": str(datetime.now())
        # }

        # visitors_collection.insert_one(user_info)

        json_str = json.dumps({
                "ip": self.client_address[0],
                "timestamp": str(datetime.now())
        })
        rabbit_channel.basic_publish(exchange='',
                      routing_key='visit_queue',
                      body=json_str)

        # visitor_in_db = visitors_collection.find_one({"ip": self.client_address[0]})
        # if visitor_in_db is None:
            # visitors_collection.insert_one({
            #     "ip": self.client_address[0],
            #     "timestamp": str(datetime.now())
            # })
        

        visitors_info = redis_connection.get("visitors_info")
        if visitors_info is None:
            visitors_cursor = visitors_collection.find().limit(5)
            visitors_info = ""
            for visitor in visitors_cursor:
                visitors_info += f"<p>IP: {visitor['ip']} TIMESTAMP: {visitor['timestamp']}<p>"

            redis_connection.set("visitors_info", visitors_info)

        

        response = f"""
            <h2>Welcome to our website!</h2>
            <p>Number of visitors is <b>{visitors_count}</b>!</p>
            <h3>Latest Visitors:</h3>
            {visitors_info}
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(str(response).encode('utf8'))

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    print("Starting web server...")
    run(handler_class=RequestHandler)
