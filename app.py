from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps

import redis
'''
Написати додаток-вебсайт, який:

    1) Рахувати кількість відвідувачів
    2) Виводити декілька останніх відвідувачів

http server

redis
mongo
rabbitmq
'''

redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)

# visitors_count = 0

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        # global visitors_count
        # visitors_count += 1
        visitors_count = redis_connection.incr("visitors_count", amount=1)

        response = f"""
            <h2>Welcome to our website!</h2>
            <p>Number of visitors is <b>{visitors_count}</b>!</p>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(dumps(response))))
        self.end_headers()
        self.wfile.write(str(response).encode('utf8'))

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    print("Starting web server...")
    run(handler_class=RequestHandler)
