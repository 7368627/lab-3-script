from PIL import ImageGrab
from datetime import datetime
import os
import json

def formatted_filename(pattern, image_id):
    # Support {id} and {timestamp} tokens in pattern
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    name = pattern.replace('{id}', str(image_id)).replace('{timestamp}', ts)
    return name

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
    # Determine filename pattern
    pattern = config.get('pattern', '{id}')
    # Ensure image_id exists
    image_id = config.get('image_id', 1)

    filename = formatted_filename(pattern, image_id)

    # If pattern uses {id}, increment the counter; otherwise still increment to avoid collisions
    config['image_id'] = image_id + 1
    with open('save_screens_setup.json', 'w') as f:
        json.dump(config, f)

    # sanitize/append extension
    if not filename.lower().endswith('.png'):
        filename = f"{filename}.png"

    filepath = os.path.join(save_path, filename)

    img.save(filepath, 'PNG')
    print(f"Saved to: {filepath}")