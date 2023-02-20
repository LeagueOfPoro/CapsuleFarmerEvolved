from flask_socketio import SocketIO,emit
from threading import Thread,Lock
from flask import Flask, render_template
from Stats import Stats


class WebServerThread(Thread):
    def __init__(self, host, port,stats:Stats):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app,cors_allowed_origins="*")
        self.stats = stats
        self.thread = None
        self.thread_lock = Lock()

    def run(self):
        # Default route
        @self.app.route("/")
        def default():
            return render_template('index.html')


        def handle_poro_data():
            """Sends the account data to front-end server"""
            while True:
                self.socketio.emit('my_response',{'stats':self.stats.accountData})
                self.socketio.sleep(1)

        @self.socketio.event
        def connect():    
            with self.thread_lock:
                if self.thread is None:
                    self.thread = self.socketio.start_background_task(handle_poro_data)
            self.socketio.emit('my_response',{'stats':self.stats.accountData})
       
        # Start the Flask web server
        self.socketio.run(self.app, host=self.host, port=self.port)

class PoroWebServer(object):
    def __init__(self, host, port,stats):
        self.host = host
        self.port = port
        self.stats = stats

    def start(self):
        # Create and start the web server thread
        web_thread = WebServerThread(self.host, self.port,self.stats)
        web_thread.start()
