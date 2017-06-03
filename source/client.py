# -*- coding: latin-1 -*-
# Author: Onni Hakkari, Website: luckyhacker.com
import socket, json, time, threading, sys, subprocess

# Global variables start

end_tag = "MSG_END"
read_end = 0
write_end = 0

# Global variables end

'''
Read config parameters from config file: config.json
if there is no config.json file, create one.
'''
def get_config():
    global host
    global port
    global game_path
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

    host = config["Default"].get("HOST")
    port = config["Default"].get("PORT")
    game_path = config["Default"].get("GAME_PATH")


'''
Output the read and write loop times.
'''
def print_loop_times():
    global read_end
    global write_end
    cursor_up_one = '\x1b[1A'
    erase_line = '\x1b[2K'
    sys.stdout.write(erase_line + cursor_up_one + "\r")
    sys.stdout.write("Read loop time: " + str(read_end) + "s" + "\nWrite loop time: " + str(write_end) + "s")
    sys.stdout.flush()


'''
Read local.data file TICKRATE times every second and send data to server.
(Thread keeps looping)
'''
def read_local(s):
    global end_tag
    global read_end
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

        s.sendall(bytes(data + end_tag, "Latin-1"))
        read_end = time.time() - begin
        print_loop_times()
        tick(read_end)


'''
Write to remote.data file TICKRATE times every second and receive data from server.
(Thread keeps looping)
'''
def write_remote(s):
    global end_tag
    global write_end

    while True:
        begin = time.time()
        data = str(s.recv(4096), "Latin-1")

        with open("remote.data", "wb") as f:
            f.write(bytes(data.split(end_tag)[-2], "Latin-1"))

        write_end = time.time() - begin
        tick(write_end)


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


def clear_data_files():
    with open("local.data", "w+") as f:
        f.write("")

    with open("remote.data", "w+") as f:
        f.write("")

'''
Main function for starting threads and game.
'''
def main():
    global host
    global port
    global tickrate
    clear_data_files()
    address = (socket.gethostbyname(host), port)
    s = socket.socket()

    try:
        s.connect(address)
    except:
        return "Cannot establish connection to server: %s" % str(address)

    # Get used tickrate and ID for client (player ID)
    settings = str(s.recv(128), "Latin-1")
    tickrate, ID = (int(settings.split("#")[0]), settings.split("#")[1])
    print("TICKRATE: " + str(tickrate) + "\n")

    # Write player ID to config.data file. Your game needs to read it from there as soon it starts.
    with open("config.data", "w") as f:
        f.write(ID)

    # Start thread for reading local.data file and sending its content to server
    read_local_thread = threading.Thread(target=read_local, args=[s])
    read_local_thread.daemon = True
    read_local_thread.start()

    # Start thread for receiving data from server and writing it to remote.data file
    write_remote_thread = threading.Thread(target=write_remote, args=[s])
    write_remote_thread.daemon = True
    write_remote_thread.start()

    # Start game and wait it to shutdown. When game is shut down, this script will also.
    subprocess.check_call(game_path)

if __name__ == "__main__":
    get_config()
    output = main()
    if output != None:
        print(output)
