import json

# map = {"a":index,
#        "x":"",
#        "ljx":"",...
#       }

class CustomGamepad:
    def __init__(self, name, map):
        self.load_from_json()
                

    def save_to_json(self, name, map):
        self.config[name] = map
        json.dump(self.config, indent=4)
    
    def load_from_json(self):
        with open("core/profiles/GenericGamepads.json", "r") as f:
            self.config = json.load(f)
            return self.config

    def get(self, name):
        if name in self.config.keys():
            return self.config[name]
        return None
