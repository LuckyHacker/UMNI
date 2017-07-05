import sys, shutil

class Console:

    def __init__(self, client_hdl, lock):
        self.commands = {"exit": self._shutdown,
                         "ban": self._ban_client,
                         "unban": self._unban_client,
                         }
        self.client_hdl = client_hdl
        self._lock = lock
        self.screen_columns, self.screen_lines = shutil.get_terminal_size((80, 20))
        self.cursor_up = '\x1b[1A'
        self.erase_line = '\x1b[2K'
        self.output = []

    def _up_line(self, amount_lines):
        for i in range(amount_lines):
            sys.stdout.write(self.erase_line + self.cursor_up)

    def _get_newlines(self, amount_lines):
        return self.screen_lines - amount_lines

    def stdout(self, line):
        with self._lock:
            self.output.append(line[:self.screen_columns])
            if len(self.output) > self.screen_lines - 2:
                self.output.pop(0)
            self._up_line(len(self.output))
            amount_of_newlines = self._get_newlines(len(self.output))
            sys.stdout.write("\n".join(self.output) + "\n"*amount_of_newlines)
            sys.stdout.flush()

    def cmd(self):
        command = input("").split(" ")
        self.stdout("server command : " + " ".join(command))
        try:
            func = command[0]
            self.commands[func](command)
        except (KeyError, IndexError):
            self.stdout(
                "server error : bad command '{}'".format(
                " ".join(command)))
        self.cmd()

    def _shutdown(self, command):
        self.client_hdl.get_server_socket().close()
        sys.exit()

    def _ban_client(self, command):
        ip = command[1]
        self.client_hdl.ban_client(ip)

    def _unban_client(self, command):
        ip = command[1]
        self.client_hdl.unban_client(ip)
