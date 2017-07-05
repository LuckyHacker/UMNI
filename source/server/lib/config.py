import json

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
                "TICKRATE": 8
            }
            with open("config.json", "w") as f:
                f.write(json.dumps(self.config, indent=2, sort_keys=True))

    def get_host(self):
        return self.config["Default"].get("HOST")

    def get_port(self):
        return self.config["Default"].get("PORT")

    def get_tickrate(self):
        return self.config["Default"].get("TICKRATE")
