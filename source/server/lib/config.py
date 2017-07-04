import json

class Config:

    def __init__(self):
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

        self.host = config["Default"].get("HOST")
        self.port = config["Default"].get("PORT")
        self.tickrate = config["Default"].get("TICKRATE")

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_tickrate(self):
        return self.tickrate
