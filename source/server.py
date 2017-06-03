# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import socket, queue, threading, json, sys, time

# Global variables start
lock = threading.Lock()
distributer_sleep = 0.01 # 0.01 is 100 TICKRATE? TWEAK THIS!!
clients = []
data_to_forward = []
id_counter = 0
end_tag = "MSG_END"


'''
Handle client:
 - put data to queue for Distributer
 - get only latest data with END_TAG
 - remove client from CLIENTS list if connection is interrupted
'''
class ClientHandler:

    def __init__(self, conn, addr, ID):
        self.c = conn
        self.a = addr
        self.ID = ID
        self.data = ""

    def receive(self):
        self.c.sendall(bytes(str(tickrate) + "#" + str(self.ID), "Latin-1"))
        while True:
            try:
                self.data = str(self.c.recv(4096), "latin-1")
                latest_data = self.data.split(end_tag)[-2]
                if latest_data != "":
                    with lock:
                        data_to_forward.append(((self.a[0], str(self.a[1])), latest_data))
            except Exception as e:
                if self.c in clients:
                    with lock:
                        print("Client %s:%s disconnected" % (self.a[0], str(self.a[1])))
                    clients.remove(self.c)
                break


'''
Read config parameters from config file: config.json
if there is no config.json file, create one.
'''
def get_config():
    global host
    global port
    global tickrate
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        config = {}
        config["Default"] = {
            "HOST": "localhost",
            "PORT": 1234,
            "TICKRATE": 8
        }
        with open("config.json", "w") as f:
            f.write(json.dumps(config, indent=2, sort_keys=True))

    host = config["Default"].get("HOST")
    port = config["Default"].get("PORT")
    tickrate = config["Default"].get("TICKRATE")


'''
Use this function in loop that you want to have tickrate.
Example:
while True:
    begin = time.time()


    end = time.time() - begin
    tick(end)
'''
def tick(loop_time):
    global tickrate
    t = 1 / tickrate - loop_time
    if t < 0:
        pass
    else:
        time.sleep(t)


'''
Combine all received data to one, and send it to all clients.
Do it this way because we want that this server can be used with any game.
'''
def distributer():
    global data_to_forward
    global clients
    global id_counter
    global distributer_sleep

    clients_to_remove = []
    while True:
        data_to_send = ""
        addrs = []
        if len(data_to_forward) > len(clients):

            # Gather data from every client (avoid duplicates from one client)
            while True:
                if len(clients) == len(addrs):
                    break
                if len(data_to_forward) > 0:
                    with lock:
                        a, d = data_to_forward.pop(0)
                if a not in addrs:
                    data_to_send += d
                    addrs.append(a)

            data_to_send = data_to_send + end_tag

            # Try to send data to client
            for i in range(len(clients)):
                try:
                    clients[i].sendall(bytes(data_to_send, "Latin-1"))
                except Exception as e:
                    print("Client %s disconnected because of: %s" % (str(clients[i]), str(e)))
                    clients_to_remove.append(clients[i])

            # Remove clients that failed to receive data
            for i in range(len(clients_to_remove)):
                if clients_to_remove[i] in clients:
                    clients.remove(clients_to_remove[i])

            # If server does not have client. (it is empty)
            if len(clients) == 0:
                id_counter = 0
                data_to_forward = []

        time.sleep(distributer_sleep)


'''
Just ugly fix for port already in use error.
Could be possible to add other commands also for the the server.
(Remember to add loop in case of more commands)
'''
def console(server_socket):
    command = input("_> ")
    if command == "exit": # Be able to manually close ServerSocket, so address will not be in use after exiting
        server_socket.close()
        print("Server socket closed.")
        sys.exit()


'''
Main function for starting threads and accepting new clients.
'''
def main():
    global id_counter
    global clients
    address = (socket.gethostbyname(host), port)
    s = socket.socket()
    s.bind(address)
    s.listen(5)

    # Start thread to console
    admin_thread = threading.Thread(target=console, args=[s])
    admin_thread.daemon = True
    admin_thread.start()

    # Start thread for data distributer
    distributer_thread = threading.Thread(target=distributer)
    distributer_thread.daemon = True
    distributer_thread.start()

    while True:

        # Accept connections and add clients to clients list
        try:
            conn, addr = s.accept()
            print("Client connected from %s:%s" % (addr[0], str(addr[1])))
            clients.append(conn)
            id_counter += 1
        except KeyboardInterrupt or OSError:
            s.close()
            return

        # Spawn thread for every client
        client = ClientHandler(conn, addr, id_counter)
        client_thread = threading.Thread(target=client.receive)
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    get_config()
    main()
