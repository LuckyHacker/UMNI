import time

class Protocol:

    def __init__(self):
        self.end_tag = "MSG_END"

    def get_hello_msg(self, tickrate, client_id):
        return bytes("{}#{}".format(tickrate, client_id), "Latin-1")

    def get_end_tag(self):
        return self.end_tag

    def get_data_msg(self, data):
        return bytes(str(time.time()) + "\n" + data +
                     self.get_end_tag(), "Latin-1")
