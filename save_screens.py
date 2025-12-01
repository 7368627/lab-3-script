from PIL import ImageGrab
from datetime import datetime
import os
import json

with open('save_screens_setup.json', 'r') as f:
    config = json.load(f)    

save_path = config.get('folder', '.')
if not os.path.exists(save_path):
    os.makedirs(save_path)

img = ImageGrab.grabclipboard()

if isinstance(img, list):
    print("Clipboard contains file paths, not an image.")
elif img is None:
    print("No image in clipboard.")
else:
    filename = config["image_id"]
    config["image_id"] += 1
    with open('save_screens_setup.json', 'w') as f:
        json.dump(config, f)

    filepath = os.path.join(save_path, f"{filename}.png")

    img.save(filepath, 'PNG')
    print(f"Saved to: {filepath}")