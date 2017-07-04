import threading
import socket
import time

from lib.protocol import *

class ClientHandler:

    def __init__(self, id_counter, conf, lock):
        self.clients = []
        self.id_counter = id_counter
        self.conf = conf
        self._lock = lock
        self.address = (socket.gethostbyname(self.conf.get_host()), self.conf.get_port())
        self.tickrate = self.conf.get_tickrate()
        self.socket = socket.socket()

        self.init_distributer()

    def get_server_socket(self):
        return self.socket

    def init_distributer(self):
        self.distributer = Distributer(self.clients, self._lock)
        client_thread = threading.Thread(target=self.distributer.distribute)
        client_thread.daemon = True
        client_thread.start()

    def handle(self):
        self.socket.bind(self.address)
        self.socket.listen(5)

        while True:
            # Accept connections and add clients to clients list
            conn, addr = self.socket.accept()
            print("Client connected from %s:%s" % (addr[0], str(addr[1])))
            self.id_counter += 1
            client = Client(conn, addr[0], addr[1], self.id_counter, self._lock)
            self.clients.append(client)

            client_listen_thread = threading.Thread(target=self._listen, args=[client])
            client_listen_thread.daemon = True
            client_listen_thread.start()

    def _listen(self, client):
        client.sendall(Protocol().get_hello_msg(self.tickrate, client.get_id()))
        while True:
            try:
                client.recv()
            except Exception as e:
                print("Client {}:{} has been disconnected.".format(client.get_ip(), client.get_port()))
                self.clients.remove(client)
                break

class Client:

    def __init__(self, socket, ip, port, client_id, lock):
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
        self._lock = lock
        self.latest_data = ""

    def sendall(self, data):
        self.socket.sendall(data)

    def recv(self):
        data = str(self.socket.recv(4096), "Latin-1")
        self.latest_data = data.split(Protocol().get_end_tag())[-2]

    def get_socket(self):
        return self.socket

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def set_latest_data(self, data):
        self.latest_data = data

    def get_latest_data(self):
        return self.latest_data


class Distributer:

    def __init__(self, clients, lock):
        self.clients = clients
        self._lock = lock
        self.distributer_sleep = 0.01

        self.data_to_send = ""
        self.addresses = []

    def _get_data_list(self):
        # Get latest data from all clients and delete empty strings if present
        all_latest_data = list(map(lambda c: c.get_latest_data(), self.clients))
        return list(filter(("").__ne__, all_latest_data))


    def distribute(self):
        data_list = self._get_data_list()
        while True:
            data_to_send = "".join(data_list) + Protocol().get_end_tag()

            for client in self.clients:
                if client:
                    client.sendall(Protocol().get_data_msg(data_to_send))
                else:
                    self.clients.remove(client)

            # If server is empty
            if len(self.clients) == 0:
                id_counter = 0

            time.sleep(self.distributer_sleep)
