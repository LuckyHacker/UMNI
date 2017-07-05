# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import threading
import os

from lib.config import Config
from lib.client_models import ClientHandler

def main():
    lock = threading.Lock()
    conf = Config()
    id_counter = 0

    client_hdl = ClientHandler(id_counter, conf, lock)
    client_thread = threading.Thread(target=client_hdl.handle)
    client_thread.daemon = True
    client_thread.start()

    console = client_hdl.get_console()

    console.cmd()

if __name__ == "__main__":
    main()
