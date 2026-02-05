import json
import os
import time

CACHE_DIR = "cache/responses"

os.makedirs(CACHE_DIR, exist_ok=True)

def current_timestamp():
    return int(time.time())

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None
    