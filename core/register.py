import json

# map = {"a":index,
#        "x":"",
#        "ljx":"",...
#       }

class CustomGamepad:
    def __init__(self):
        self.load_from_json()
        

    def save_to_json(self, name, mapping):
        self.config[name] = mapping
        with open("core/profiles/GenericGamepads.json", "w") as f:
            json.dump(self.config, f, indent=4)

    
    def load_from_json(self):
        try:
            with open("core/profiles/GenericGamepads.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
        return self.config


    def get(self, name):
        if name in self.config.keys():
            return self.config[name]
        return None
