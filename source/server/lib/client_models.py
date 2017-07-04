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

    def reset_id_counter(self):
        self.id_counter = 0

    def get_server_socket(self):
        return self.socket

    def init_distributer(self):
        self.distributer = Distributer(self.clients, self._lock, self.tickrate, self)
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
            client.sendall(Protocol().get_hello_msg(self.tickrate, client.get_id()))
            self.clients.append(client)

            client_listen_thread = threading.Thread(target=self._listen, args=[client])
            client_listen_thread.daemon = True
            client_listen_thread.start()

    def _listen(self, client):
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

    def get_latest_data(self):
        return self.latest_data


class Distributer:

    def __init__(self, clients, lock, tickrate, client_hdl):
        self.clients = clients
        self._lock = lock
        self.tickrate = tickrate
        self.client_hdl = client_hdl

    def tick(self, loop_time):
        t = 1 / self.tickrate - loop_time
        if t < 0:
            pass
        else:
            time.sleep(t)

    def _get_data_list(self):
        # Get latest data from all clients and delete empty strings if present
        all_latest_data = list(map(lambda c: c.get_latest_data(), self.clients))
        return list(filter(("").__ne__, all_latest_data))


    def distribute(self):
        while True:
            begin = time.time()

            data_list = self._get_data_list()
            data_to_send = "".join(data_list)

            for client in self.clients:
                client.sendall(Protocol().get_data_msg(data_to_send))

            # If server is empty
            if len(self.clients) == 0:
                self.client_hdl.reset_id_counter()

            self.tick(time.time() - begin)
