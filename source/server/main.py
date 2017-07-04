# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import threading, sys

from lib.config import Config
from lib.client import ClientHandler

'''
Just ugly fix for port already in use error.
Could be possible to add other commands also for the the server.
(Remember to add loop in case of more commands)
'''
def console(client_hdl):
    command = input("_> ")
    if command == "exit": # Be able to manually close ServerSocket, so address will not be in use after exiting
        client_hdl.get_server_socket().close()
        print("Server socket closed.")
        sys.exit()


'''
Main function for starting threads and accepting new clients.
'''
def main():
    lock = threading.Lock()
    conf = Config()
    id_counter = 0

    # Spawn thread for every client
    client_hdl = ClientHandler(id_counter, conf, lock)
    client_thread = threading.Thread(target=client_hdl.handle)
    client_thread.daemon = True
    client_thread.start()

    console(client_hdl)

if __name__ == "__main__":
    main()
