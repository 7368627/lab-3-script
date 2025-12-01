import json

with open("save_screens_setup.json", "r") as f:
    config = json.load(f)

config["image_id"] = 1
with open("save_screens_setup.json", "w") as f:
    json.dump(config, f)

