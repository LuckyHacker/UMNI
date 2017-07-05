# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import socket
import json
import time
import threading
import sys
import subprocess

class Config:

    def __init__(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.loads(f.read())
        except FileNotFoundError:
            self.config = {}
            self.config["Default"] = {
                "HOST": "localhost",
                "PORT": 1234,
                "GAME_PATH": "game.exe"
            }
            with open("config.json", "w") as f:
                f.write(json.dumps(self.config, indent=2, sort_keys=True))

    def get_host(self):
        return self.config["Default"].get("HOST")

    def get_port(self):
        return self.config["Default"].get("PORT")

    def get_game_path(self):
        return self.config["Default"].get("GAME_PATH")


class LoopTimes:

    def __init__(self):
        self.read_end = 0
        self.write_end = 0

    def set_read_end(self, read_end):
        self.read_end = read_end

    def get_read_end(self):
        return self.read_end

    def set_write_end(self, write_end):
        self.write_end = write_end

    def get_write_end(self):
        return self.write_end

    def print_loop_times(self):
        cursor_up_one = '\x1b[1A'
        erase_line = '\x1b[2K'
        sys.stdout.write(erase_line + cursor_up_one + "\r")
        sys.stdout.write("Read loop time: " +
                         str(self.read_end) +
                         "s" +
                         "\nWrite loop time: " +
                         str(self.write_end) +
                         "s")
        sys.stdout.flush()


class Protocol:

    def __init__(self):
        self.end_tag = "MSG_END"

    def get_end_tag(self):
        return self.end_tag


class Tick:

    def __init__(self, tickrate):
        self.tickrate = tickrate

    def tick(self, loop_time):
        t = 1 / self.tickrate - loop_time
        if t < 0:
            pass
        else:
            time.sleep(t)


class ReadLocal:

    def __init__(self, socket, looptimes, tick):
        self.socket = socket
        self.looptimes = looptimes
        self.tick = tick
        self.data = ""
        with open("local.data", "wb") as f:
            f.write(bytes("", "Latin-1"))

    def read_local_data(self):
        while True:
            begin = time.time()

            with open("local.data", "rb") as f:
                self.data = str(f.read(), "Latin-1")

            self.socket.sendall(bytes(self.data + Protocol().get_end_tag(), "Latin-1"))
            self.looptimes.set_read_end(time.time() - begin)
            self.looptimes.print_loop_times()
            self.tick.tick(self.looptimes.get_read_end())

class WriteRemote:

    def __init__(self, socket, looptimes, tick):
        self.socket = socket
        self.looptimes = looptimes
        self.tick = tick
        self.data = ""
        with open("remote.data", "wb") as f:
            f.write(bytes("", "Latin-1"))

    def write_remote_data(self):
        while True:
            begin = time.time()

            self.data = str(self.socket.recv(4096), "Latin-1")
            with open("remote.data", "wb") as f:
                f.write(bytes(self.data.split(Protocol().get_end_tag())[-2], "Latin-1"))

            self.looptimes.set_write_end(time.time() - begin)
            self.tick.tick(self.looptimes.get_write_end())


def clear_data_files():
    with open("local.data", "w+") as f:
        f.write("")

    with open("remote.data", "w+") as f:
        f.write("")

def main():
    conf = Config()
    clear_data_files()
    address = (socket.gethostbyname(conf.get_host()), conf.get_port())
    s = socket.socket()

    try:
        s.connect(address)
    except:
        return "Cannot establish connection to server: %s" % str(address)

    # Get tickrate and ID for client (player ID)
    settings = str(s.recv(128), "Latin-1").split("#")
    tickrate, client_id = (int(settings[0]), settings[1])
    print("TICKRATE: " + str(tickrate) + "\n")

    # Write player ID to config.data file.
    # Your game needs to read it from there as soon it starts.
    with open("config.data", "w") as f:
        f.write(client_id)

    looptimes = LoopTimes()
    tick = Tick(tickrate)
    readlocal = ReadLocal(s, looptimes, tick)
    writeremote = WriteRemote(s, looptimes, tick)

    # Start thread for reading local.data file and
    # sending its content to server
    read_local_thread = threading.Thread(target=readlocal.read_local_data)
    read_local_thread.daemon = True
    read_local_thread.start()

    # Start thread for receiving data from server and
    # writing it to remote.data file
    write_remote_thread = threading.Thread(target=writeremote.write_remote_data)
    write_remote_thread.daemon = True
    write_remote_thread.start()

    # Start game and wait it to shutdown.
    # When game is shut down, this script will also.
    subprocess.check_call(conf.get_game_path())

if __name__ == "__main__":
    output = main()
    if output: print(output)
