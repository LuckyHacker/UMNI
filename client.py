# -*- coding: latin-1 -*-
############################################################
####### Author: Onni Hakkari, Updated: 11.05.2017 ##########
################# Website: luckyhacker.com #################
############################################################
import socket, json, time, threading, sys, subprocess

####################################
###### Global variables start ######
####################################
global HOST
global PORT
global GAME_PATH
global END_TAG
global READ_END
global WRITE_END

END_TAG = "MSG_END"
READ_END = 0
WRITE_END = 0

####################################
####### Global variables end #######
####################################

'''
Read config parameters from config file: config.json
if there is no config.json file, create one.
'''
def Get_Config():
    global HOST
    global PORT
    global GAME_PATH
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        config = {}
        config["Default"] = {
            "HOST": "localhost",
            "PORT": 1234,
            "GAME_PATH": "game.exe"
        }
        with open("config.json", "w") as f:
            f.write(json.dumps(config, indent=2, sort_keys=True))

    HOST = config["Default"].get("HOST")
    PORT = config["Default"].get("PORT")
    GAME_PATH = config["Default"].get("GAME_PATH")


'''
Output the read and write loop times.
'''
def print_loop_times():
    global READ_END
    global WRITE_END
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    sys.stdout.write(ERASE_LINE + CURSOR_UP_ONE + "\r")
    sys.stdout.write("Read loop time: " + str(READ_END) + "s" + "\nWrite loop time: " + str(WRITE_END) + "s")
    sys.stdout.flush()


'''
Read local.data file TICKRATE times every second and send data to server.
(Thread keeps looping)
'''
def read_local(s):
    global END_TAG
    global READ_END
    while True:
        begin = time.time()
        try:
            with open("local.data", "rb") as f:
                data = str(f.read(), "Latin-1")
        except FileNotFoundError:
            with open("local.data", "wb") as f:
                f.write(bytes("", "Latin-1"))
            with open("local.data", "rb") as f:
                data = str(f.read(), "Latin-1")

        s.sendall(bytes(data + END_TAG, "Latin-1"))
        READ_END = time.time() - begin
        print_loop_times()
        Tick(READ_END)


'''
Write to remote.data file TICKRATE times every second and receive data from server.
(Thread keeps looping)
'''
def write_remote(s):
    global END_TAG
    global WRITE_END

    while True:
        begin = time.time()
        data = str(s.recv(4096), "Latin-1")

        with open("remote.data", "wb") as f:
            f.write(bytes(data.split(END_TAG)[-2], "Latin-1"))

        WRITE_END = time.time() - begin
        Tick(WRITE_END)


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
Main function for starting threads and game.
'''
def main():
    global HOST
    global PORT
    global TICKRATE
    address = (socket.gethostbyname(HOST), PORT)
    s = socket.socket()

    try:
        s.connect(address)
    except:
        return "Cannot establish connection to server: %s" % str(address)

    # Get used tickrate and ID for client (player ID)
    settings = str(s.recv(128), "Latin-1")
    TICKRATE, ID = (int(settings.split("#")[0]), settings.split("#")[1])
    print("TICKRATE: " + str(TICKRATE) + "\n")

    # Write player ID to config.data file. Your game needs to read it from there as soon it starts.
    with open("config.data", "w") as f:
        f.write(ID)

    # Start thread for reading local.data file and sending its content to server
    RT = threading.Thread(target=read_local, args=[s])
    RT.daemon = True
    RT.start()

    # Start thread for receiving data from server and writing it to remote.data file
    WT = threading.Thread(target=write_remote, args=[s])
    WT.daemon = True
    WT.start()

    # Start game and wait it to shutdown. When game is shut down, this script will also.
    subprocess.check_call(GAME_PATH)

if __name__ == "__main__":
    Get_Config()
    output = main()
    if output != None:
        print(output)
