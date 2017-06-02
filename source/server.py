# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import socket, queue, threading, json, sys, time

# Global variables start
global HOST
global PORT
global TICKRATE
global DATA_TO_FORWARD
global ID_COUNTER
global IDS
global END_TAG
global DISTRIBUTER_SLEEP

DISTRIBUTER_SLEEP = 0.01 # 0.01 is 100 TICKRATE? TWEAK THIS!!
CLIENTS = []
DATA_TO_FORWARD = queue.Queue()
ID_COUNTER = 0
IDS = []
END_TAG = "MSG_END"

# Global variables end

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

    def Receive(self):
        self.c.sendall(bytes(str(TICKRATE) + "#" + str(self.ID), "Latin-1"))
        while True:
            try:
                self.data = str(self.c.recv(4096), "latin-1")
                latest_data = self.data.split(END_TAG)[-2]
                if latest_data != "":
                    DATA_TO_FORWARD.put_nowait(((self.a[0], str(self.a[1])), latest_data))
            except Exception as e:
                if self.c in CLIENTS:
                    CLIENTS.remove(self.c)
                break


'''
Read config parameters from config file: config.json
if there is no config.json file, create one.
'''
def Get_Config():
    global HOST
    global PORT
    global TICKRATE
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

    HOST = config["Default"].get("HOST")
    PORT = config["Default"].get("PORT")
    TICKRATE = config["Default"].get("TICKRATE")


'''
Use this function in loop that you want to have tickrate.
Example:
while True:
    begin = time.time()


    end = time.time() - begin
    Tick(end)
'''
def Tick(loop_time):
    global TICKRATE
    t = 1 / TICKRATE - loop_time
    if t < 0:
        pass
    else:
        time.sleep(t)


'''
Combine all received data to one, and send it to all clients.
Do it this way because we want that this server can be used with any game.
'''
def Distributer():
    global DATA_TO_FORWARD
    global CLIENTS
    global END_TAG
    global DISTRIBUTER_SLEEP
    clients_to_remove = []
    while True:
        data = ""
        addrs = []
        if DATA_TO_FORWARD.qsize() > len(CLIENTS):

            # Gather data from every client (avoid duplicates from one client)
            for i in range(len(CLIENTS)):
                a, d = DATA_TO_FORWARD.get_nowait()
                if a not in addrs:
                    data += d
                    addrs.append(a)

            data = data + END_TAG

            # Try to send data to client
            for i in range(len(CLIENTS)):
                try:
                    CLIENTS[i].sendall(bytes(data, "Latin-1"))
                except Exception as e:
                    clients_to_remove.append(CLIENTS[i])

            # Remove clients that failed to receive data
            for i in range(len(clients_to_remove)):
                if clients_to_remove[i] in CLIENTS:
                    CLIENTS.remove(clients_to_remove[i])

            # If server does not have client. (it is empty)
            if len(CLIENTS) == 0:
                ID_COUNTER = 0
                if DATA_TO_FORWARD.empty() == False:
                    DATA_TO_FORWARD.get_nowait()

        time.sleep(DISTRIBUTER_SLEEP)


'''
Just ugly fix for port already in use error.
Could be possible to add other commands also for the the server.
(Remember to add loop in case of more commands)
'''
def Console(ServerSocket):
    command = input("_> ")
    if command == "exit": # Be able to manually close ServerSocket, so address will not be in use after exiting
        ServerSocket.close()
        print("Server socket closed.")
        sys.exit()


'''
Main function for starting threads and accepting new clients.
'''
def main():
    global ID_COUNTER
    global IDS
    global CLIENTS
    address = (socket.gethostbyname(HOST), PORT)
    s = socket.socket()
    s.bind(address)
    s.listen(5)

    # Start thread to console
    adminT = threading.Thread(target=Console, args=[s])
    adminT.daemon = True
    adminT.start()

    # Start thread for data distributer
    dT = threading.Thread(target=Distributer)
    dT.daemon = True
    dT.start()

    while True:

        # Accept connections and add clients to clients list
        try:
            conn, addr = s.accept()
            print("Client connected from %s:%s" % (addr[0], str(addr[1])))
            CLIENTS.append(conn)
            ID_COUNTER += 1
        except KeyboardInterrupt or OSError:
            s.close()
            return

        # Spawn thread for every client
        Client = ClientHandler(conn, addr, ID_COUNTER)
        c = threading.Thread(target=Client.Receive)
        c.daemon = True
        c.start()

if __name__ == "__main__":
    Get_Config()
    main()
