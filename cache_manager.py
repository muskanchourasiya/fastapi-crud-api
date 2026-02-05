import os
import hashlib
from utils import current_timestamp, save_json, load_json, CACHE_DIR
from functools import wraps
from pathlib import Path

TTL = 300

def generate_cache_key(endpoint:str, params:str):
    raw = endpoint + str(sorted(params.items()))
    return hashlib.md5(raw.encode()).hexdigest()

def cache_path(key):
    return f"{CACHE_DIR}/{key}.json"

def save_cache(key, data):
    payload = {
        "timestamp": current_timestamp(),
        "data": data
    }

def save_json(path, payload):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f)

def load_cache(key):
    path = cache_path(key)
    if not os.path.exists(path):
        return None

    payload = load_json(path)
    if not payload:
        return None
    
    if current_timestamp() - payload["timestamp"] > TTL:
        os.remove(path)
        return None
    return payload["data"]

def cached(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        clean_kwargs = {
            k: v for k, v in kwargs.items()
            if isinstance(v, (str, int, float, bool))
        }

        endpoint = func.__name__
        key = generate_cache_key(endpoint, clean_kwargs)
        cached_data = load_cache(key)
        if cached_data is not None:
            return cached_data
        
        result = func(*args, **kwargs)
        try:
            save_cache(key, result)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
        return result
        
    return wrapper